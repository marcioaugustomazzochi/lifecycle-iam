from contextlib import closing
from datetime import datetime, timezone

from modules.database import conectar


def admitir_colaborador(nome, email, departamento, cargo):
    """Cadastra um colaborador e registra o evento de admissão."""

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
                (colaborador_id, evento, descricao, data_evento)
                VALUES (?, ?, ?, ?)
                """,
                (
                    colaborador_id,
                    "ADMISSAO",
                    f"Admissão registrada para {nome}.",
                    data_admissao
                )
            )

    return colaborador_id
