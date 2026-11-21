import hashlib
import hmac
import secrets
from contextlib import closing
from datetime import datetime, timezone

from modules.database import conectar


ITERACOES_PBKDF2 = 600_000
TAMANHO_SALT = 32


def gerar_hash_senha(senha, salt=None):
    """Gera hash seguro usando PBKDF2-HMAC-SHA256."""

    if not isinstance(senha, str) or len(senha) < 12:
        raise ValueError(
            "A senha deve possuir pelo menos 12 caracteres."
        )

    if salt is None:
        salt = secrets.token_bytes(TAMANHO_SALT)

    hash_senha = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        ITERACOES_PBKDF2
    )

    return hash_senha.hex(), salt.hex()


def verificar_senha(senha, hash_armazenado, salt_armazenado):
    """Compara a senha informada com o hash armazenado."""

    try:
        if not isinstance(senha, str):
            return False

        salt = bytes.fromhex(salt_armazenado)

        hash_calculado, _ = gerar_hash_senha(
            senha,
            salt
        )

        return hmac.compare_digest(
            hash_calculado,
            hash_armazenado
        )

    except (ValueError, TypeError):
        return False


def criar_usuario(
    operador_id,
    email,
    senha,
    nome_perfil,
    colaborador_id=None
):
    """Cria usuário mediante autorização administrativa."""

    if not isinstance(email, str) or not email.strip():
        raise ValueError("O e-mail é obrigatório.")

    email = email.strip().lower()

    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("O endereço de e-mail é inválido.")

    if not isinstance(nome_perfil, str) or not nome_perfil.strip():
        raise ValueError("O perfil é obrigatório.")

    nome_perfil = nome_perfil.strip()

    if colaborador_id is not None:
        if (
            not isinstance(colaborador_id, int)
            or colaborador_id <= 0
        ):
            raise ValueError("O ID do colaborador é inválido.")

    hash_senha, salt = gerar_hash_senha(senha)
    criado_em = datetime.now(timezone.utc).isoformat()

    with closing(conectar()) as conexao:
        with conexao:
            # Verifica a autorização do operador.
            autorizado = conexao.execute(
                """
                SELECT 1
                FROM usuarios u
                JOIN usuario_perfis up
                    ON up.usuario_id = u.id
                JOIN perfil_permissoes pp
                    ON pp.perfil_id = up.perfil_id
                JOIN permissoes p
                    ON p.id = pp.permissao_id
                WHERE u.id = ?
                  AND u.ativo = 1
                  AND p.codigo = 'permissao.gerenciar'
                LIMIT 1
                """,
                (operador_id,)
            ).fetchone()

            if autorizado is None:
                raise PermissionError(
                    "Acesso negado. Somente Administradores "
                    "podem criar usuários."
                )

            # Confere se o perfil solicitado existe.
            perfil = conexao.execute(
                """
                SELECT id
                FROM perfis
                WHERE nome = ?
                """,
                (nome_perfil,)
            ).fetchone()

            if perfil is None:
                raise ValueError("Perfil não encontrado.")

            # Confere o vínculo opcional com colaborador.
            if colaborador_id is not None:
                colaborador = conexao.execute(
                    """
                    SELECT id, status
                    FROM colaboradores
                    WHERE id = ?
                    """,
                    (colaborador_id,)
                ).fetchone()

                if colaborador is None:
                    raise ValueError("Colaborador não encontrado.")

                if colaborador["status"] != "ATIVO":
                    raise ValueError(
                        "Não é possível criar acesso para "
                        "colaborador inativo."
                    )

            # Cria a conta.
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
                VALUES (?, ?, ?, ?, 1, ?)
                """,
                (
                    colaborador_id,
                    email,
                    hash_senha,
                    salt,
                    criado_em
                )
            )

            novo_usuario_id = cursor.lastrowid

            # Atribui o perfil inicial.
            conexao.execute(
                """
                INSERT INTO usuario_perfis (
                    usuario_id,
                    perfil_id,
                    atribuido_em
                )
                VALUES (?, ?, ?)
                """,
                (
                    novo_usuario_id,
                    perfil["id"],
                    criado_em
                )
            )

            # Registra a criação na auditoria.
            conexao.execute(
                """
                INSERT INTO auditoria (
                    colaborador_id,
                    evento,
                    descricao,
                    data_evento,
                    operador_id
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    colaborador_id,
                    "USUARIO_CRIADO",
                    (
                        f"Usuário ID {novo_usuario_id} criado "
                        f"com perfil {nome_perfil}."
                    ),
                    criado_em,
                    operador_id
                )
            )

    return novo_usuario_id


def autenticar_usuario(email, senha):
    """Autentica um usuário ativo do sistema."""

    if not isinstance(email, str) or not isinstance(senha, str):
        return None

    email = email.strip().lower()

    with closing(conectar()) as conexao:
        usuario = conexao.execute(
            """
            SELECT
                id,
                email,
                senha_hash,
                senha_salt,
                ativo
            FROM usuarios
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

    if usuario is None or usuario["ativo"] != 1:
        return None

    if not verificar_senha(
        senha,
        usuario["senha_hash"],
        usuario["senha_salt"]
    ):
        return None

    return {
        "id": usuario["id"],
        "email": usuario["email"]
    }
