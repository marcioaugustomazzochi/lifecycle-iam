from contextlib import closing
from datetime import datetime, timezone

from modules.database import conectar
from modules.rbac import _verificar_permissao


def movimentar_colaborador(
    colaborador_id,
    novo_departamento,
    novo_cargo,
    operador_id
):
    """Atualiza departamento e cargo com autorização e auditoria."""

    if not isinstance(colaborador_id, int) or colaborador_id <= 0:
        raise ValueError("O identificador do colaborador é inválido.")

    campos = {
        "departamento": novo_departamento,
        "cargo": novo_cargo
    }

    for campo, valor in campos.items():
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"O campo {campo} é obrigatório.")

    novo_departamento = novo_departamento.strip()
    novo_cargo = novo_cargo.strip()

    data_evento = datetime.now(timezone.utc).isoformat()

    with closing(conectar()) as conexao:
        with conexao:
            autorizado = _verificar_permissao(
                conexao,
                operador_id,
                "colaborador.movimentar"
            )

            if not autorizado:
                raise PermissionError(
                    "Acesso negado. Você não possui permissão "
                    "para movimentar colaboradores."
                )

            colaborador = conexao.execute(
                """
                SELECT nome, departamento, cargo
                FROM colaboradores
                WHERE id = ? AND status = 'ATIVO'
                """,
                (colaborador_id,)
            ).fetchone()

            if colaborador is None:
                raise ValueError(
                    "Colaborador não encontrado ou não está ativo."
                )

            departamento_anterior = colaborador["departamento"]
            cargo_anterior = colaborador["cargo"]

            conexao.execute(
                """
                UPDATE colaboradores
                SET departamento = ?, cargo = ?
                WHERE id = ?
                """,
                (novo_departamento, novo_cargo, colaborador_id)
            )

            descricao = (
                f"Movimentação de {colaborador['nome']}: "
                f"departamento de '{departamento_anterior}' para "
                f"'{novo_departamento}' e cargo de '{cargo_anterior}' "
                f"para '{novo_cargo}'."
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
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    colaborador_id,
                    "MOVIMENTACAO",
                    descricao,
                    data_evento,
                    operador_id
                )
            )

    return True
