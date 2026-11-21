from contextlib import closing
from datetime import datetime, timezone
from getpass import getpass

from modules.auth import gerar_hash_senha
from modules.database import conectar


def inicializar_primeiro_administrador():
    """Cria o primeiro Administrador somente se não houver usuários."""

    print("\n=== CONFIGURAÇÃO DO PRIMEIRO ADMINISTRADOR ===")

    email = input("E-mail do Administrador: ").strip().lower()

    if not email or "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Endereço de e-mail inválido.")

    senha = getpass("Crie uma senha (mínimo 12 caracteres): ")
    confirmacao = getpass("Confirme a senha: ")

    if senha != confirmacao:
        raise ValueError("As senhas não coincidem.")

    hash_senha, salt = gerar_hash_senha(senha)
    criado_em = datetime.now(timezone.utc).isoformat()

    with closing(conectar()) as conexao:
        with conexao:
            quantidade = conexao.execute(
                "SELECT COUNT(*) FROM usuarios"
            ).fetchone()[0]

            if quantidade > 0:
                raise RuntimeError(
                    "A inicialização já foi realizada. "
                    "Não é permitido criar outro primeiro Administrador."
                )

            perfil = conexao.execute(
                """
                SELECT id
                FROM perfis
                WHERE nome = 'Administrador'
                """
            ).fetchone()

            if perfil is None:
                raise RuntimeError(
                    "Perfil Administrador não encontrado no banco."
                )

            cursor = conexao.execute(
                """
                INSERT INTO usuarios (
                    colaborador_id,
                    email,
                    senha_hash,
                    senha_salt,
                    ativo,
                    criado_em
                )
                VALUES (NULL, ?, ?, ?, 1, ?)
                """,
                (email, hash_senha, salt, criado_em)
            )

            administrador_id = cursor.lastrowid

            conexao.execute(
                """
                INSERT INTO usuario_perfis (
                    usuario_id,
                    perfil_id,
                    atribuido_em
                )
                VALUES (?, ?, ?)
                """,
                (administrador_id, perfil["id"], criado_em)
            )

            conexao.execute(
                """
                INSERT INTO auditoria (
                    colaborador_id,
                    evento,
                    descricao,
                    data_evento,
                    operador_id
                )
                VALUES (NULL, ?, ?, ?, ?)
                """,
                (
                    "ADMINISTRADOR_INICIAL_CRIADO",
                    "Primeiro Administrador configurado no sistema.",
                    criado_em,
                    administrador_id
                )
            )

    print("\nPrimeiro Administrador criado com sucesso.")
    print(f"Identificador do usuário: {administrador_id}")


if __name__ == "__main__":
    try:
        inicializar_primeiro_administrador()
    except (ValueError, RuntimeError) as erro:
        print(f"\nNão foi possível concluir: {erro}")
