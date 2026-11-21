from contextlib import closing
from datetime import datetime, timezone

from modules.database import conectar
from modules.rbac import _verificar_permissao


def admitir_colaborador(
    nome,
    email,
    departamento,
    cargo,
    operador_id
):
    """Cadastra colaborador com autorização e auditoria do operador."""

    campos = {
        "nome": nome,
        "email": email,
        "departamento": departamento,
        "cargo": cargo
    }

    for campo, valor in campos.items():
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"O campo {campo} é obrigatório.")

    nome = nome.strip()
    email = email.strip().lower()
    departamento = departamento.strip()
    cargo = cargo.strip()

    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("O endereço de e-mail é inválido.")

    data_admissao = datetime.now(timezone.utc).isoformat()

    with closing(conectar()) as conexao:
        with conexao:
            autorizado = _verificar_permissao(
                conexao,
                operador_id,
                "colaborador.admitir"
            )

            if not autorizado:
                raise PermissionError(
                    "Acesso negado. Você não possui permissão para admitir colaboradores."
                )

            cursor = conexao.execute(
                """
                INSERT INTO colaboradores
                (nome, email, departamento, cargo, status, data_admissao)
                VALUES (?, ?, ?, ?, 'ATIVO', ?)
                """,
                (nome, email, departamento, cargo, data_admissao)
            )

            colaborador_id = cursor.lastrowid

            conexao.execute(
                """
                INSERT INTO auditoria
                (
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
                    "ADMISSAO",
                    f"Admissão registrada para {nome}.",
                    data_admissao,
                    operador_id
                )
            )

    return colaborador_id
