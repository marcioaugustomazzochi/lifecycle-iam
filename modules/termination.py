from contextlib import closing
from datetime import datetime, timezone

from modules.database import conectar


def desligar_colaborador(colaborador_id):
    """Desativa um colaborador e registra o evento de desligamento."""

    if not isinstance(colaborador_id, int) or colaborador_id <= 0:
        raise ValueError("O identificador do colaborador é inválido.")

    data_evento = datetime.now(timezone.utc).isoformat()

    with closing(conectar()) as conexao:
        with conexao:
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

            descricao = (
                f"Desligamento registrado para {colaborador['nome']}. "
                "Status alterado de ATIVO para INATIVO."
            )

            conexao.execute(
                """
                INSERT INTO auditoria
                (colaborador_id, evento, descricao, data_evento)
                VALUES (?, ?, ?, ?)
                """,
                (
                    colaborador_id,
                    "DESLIGAMENTO",
                    descricao,
                    data_evento
                )
            )

    return True