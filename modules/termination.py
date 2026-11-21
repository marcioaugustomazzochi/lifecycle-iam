from contextlib import closing
from datetime import datetime, timezone

from modules.database import conectar
from modules.rbac import _verificar_permissao


def desligar_colaborador(colaborador_id, operador_id):
    """Desativa colaborador e acesso ao sistema, com auditoria."""

    if not isinstance(colaborador_id, int) or colaborador_id <= 0:
        raise ValueError("O identificador do colaborador é inválido.")

    data_evento = datetime.now(timezone.utc).isoformat()

    with closing(conectar()) as conexao:
        with conexao:
            autorizado = _verificar_permissao(
                conexao,
                operador_id,
                "colaborador.desligar"
            )

            if not autorizado:
                raise PermissionError(
                    "Acesso negado. Você não possui permissão "
                    "para desligar colaboradores."
                )

            colaborador = conexao.execute(
                """
                SELECT nome, status
                FROM colaboradores
                WHERE id = ?
                """,
                (colaborador_id,)
            ).fetchone()

            if colaborador is None:
                raise ValueError("Colaborador não encontrado.")

            if colaborador["status"] == "INATIVO":
                raise ValueError("O colaborador já está inativo.")

            conexao.execute(
                """
                UPDATE colaboradores
                SET status = 'INATIVO'
                WHERE id = ?
                """,
                (colaborador_id,)
            )

            # Desativa a conta de acesso vinculada ao colaborador.
            conexao.execute(
                """
                UPDATE usuarios
                SET ativo = 0
                WHERE colaborador_id = ?
                """,
                (colaborador_id,)
            )

            descricao = (
                f"Desligamento registrado para {colaborador['nome']}. "
                "Status alterado de ATIVO para INATIVO. "
                "Contas de acesso vinculadas foram desativadas."
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
                    "DESLIGAMENTO",
                    descricao,
                    data_evento,
                    operador_id
                )
            )

    return True
