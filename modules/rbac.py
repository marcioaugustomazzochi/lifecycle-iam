
from contextlib import closing
from datetime import datetime, timezone

from modules.database import conectar


def _verificar_permissao(conexao, usuario_id, codigo_permissao):
    """Verifica a permissão de um usuário ativo."""

    resultado = conexao.execute(
        """
        SELECT 1
        FROM usuarios u
        JOIN usuario_perfis up ON up.usuario_id = u.id
        JOIN perfil_permissoes pp ON pp.perfil_id = up.perfil_id
        JOIN permissoes p ON p.id = pp.permissao_id
        WHERE u.id = ?
          AND u.ativo = 1
          AND p.codigo = ?
        LIMIT 1
        """,
        (usuario_id, codigo_permissao)
    ).fetchone()

    return resultado is not None


def listar_perfis_usuario(usuario_id):
    """Retorna os perfis associados a um usuário ativo."""

    with closing(conectar()) as conexao:
        usuario = conexao.execute(
            """
            SELECT ativo
            FROM usuarios
            WHERE id = ?
            """,
            (usuario_id,)
        ).fetchone()

        if usuario is None or usuario["ativo"] != 1:
            return []

        perfis = conexao.execute(
            """
            SELECT p.nome
            FROM perfis p
            JOIN usuario_perfis up ON up.perfil_id = p.id
            WHERE up.usuario_id = ?
            ORDER BY p.nome
            """,
            (usuario_id,)
        ).fetchall()

        return [perfil["nome"] for perfil in perfis]


def usuario_tem_permissao(usuario_id, codigo_permissao):
    """Verifica se um usuário ativo possui determinada permissão."""

    with closing(conectar()) as conexao:
        return _verificar_permissao(
            conexao,
            usuario_id,
            codigo_permissao
        )


def exigir_permissao(usuario_id, codigo_permissao):
    """Impede a operação quando o usuário não tem autorização."""

    if not usuario_tem_permissao(usuario_id, codigo_permissao):
        raise PermissionError(
            "Acesso negado. Você não possui permissão para esta operação."
        )


def _registrar_auditoria(
    conexao,
    operador_id,
    usuario_id,
    evento,
    descricao,
    data_evento
):
    """Registra uma operação de gerenciamento de perfis."""

    colaborador = conexao.execute(
        """
        SELECT colaborador_id
        FROM usuarios
        WHERE id = ?
        """,
        (usuario_id,)
    ).fetchone()

    colaborador_id = (
        colaborador["colaborador_id"]
        if colaborador is not None
        else None
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
            evento,
            descricao,
            data_evento,
            operador_id
        )
    )


def atribuir_perfil(operador_id, usuario_id, nome_perfil):
    """Atribui um perfil mediante autorização administrativa."""

    if not isinstance(nome_perfil, str) or not nome_perfil.strip():
        raise ValueError("O nome do perfil é obrigatório.")

    nome_perfil = nome_perfil.strip()
    data_evento = datetime.now(timezone.utc).isoformat()

    with closing(conectar()) as conexao:
        with conexao:
            if not _verificar_permissao(
                conexao,
                operador_id,
                "permissao.gerenciar"
            ):
                raise PermissionError(
                    "Acesso negado. Você não possui permissão "
                    "para esta operação."
                )

            usuario = conexao.execute(
                """
                SELECT id, ativo
                FROM usuarios
                WHERE id = ?
                """,
                (usuario_id,)
            ).fetchone()

            if usuario is None or usuario["ativo"] != 1:
                raise ValueError("Usuário não encontrado ou inativo.")

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

            existente = conexao.execute(
                """
                SELECT 1
                FROM usuario_perfis
                WHERE usuario_id = ? AND perfil_id = ?
                """,
                (usuario_id, perfil["id"])
            ).fetchone()

            if existente:
                raise ValueError("O usuário já possui esse perfil.")

            conexao.execute(
                """
                INSERT INTO usuario_perfis (
                    usuario_id,
                    perfil_id,
                    atribuido_em
                )
                VALUES (?, ?, ?)
                """,
                (usuario_id, perfil["id"], data_evento)
            )

            _registrar_auditoria(
                conexao,
                operador_id,
                usuario_id,
                "PERFIL_ATRIBUIDO",
                f"Perfil {nome_perfil} atribuído ao usuário ID {usuario_id}.",
                data_evento
            )

    return True


def revogar_perfil(operador_id, usuario_id, nome_perfil):
    """Revoga um perfil mediante autorização administrativa."""

    if not isinstance(nome_perfil, str) or not nome_perfil.strip():
        raise ValueError("O nome do perfil é obrigatório.")

    nome_perfil = nome_perfil.strip()
    data_evento = datetime.now(timezone.utc).isoformat()

    with closing(conectar()) as conexao:
        with conexao:
            if not _verificar_permissao(
                conexao,
                operador_id,
                "permissao.gerenciar"
            ):
                raise PermissionError(
                    "Acesso negado. Você não possui permissão "
                    "para esta operação."
                )

            usuario = conexao.execute(
                """
                SELECT id, ativo
                FROM usuarios
                WHERE id = ?
                """,
                (usuario_id,)
            ).fetchone()

            if usuario is None or usuario["ativo"] != 1:
                raise ValueError("Usuário não encontrado ou inativo.")

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

            vinculo = conexao.execute(
                """
                SELECT 1
                FROM usuario_perfis
                WHERE usuario_id = ? AND perfil_id = ?
                """,
                (usuario_id, perfil["id"])
            ).fetchone()

            if vinculo is None:
                raise ValueError("O usuário não possui esse perfil.")

            if nome_perfil == "Administrador":
                administradores = conexao.execute(
                    """
                    SELECT COUNT(DISTINCT u.id)
                    FROM usuarios u
                    JOIN usuario_perfis up ON up.usuario_id = u.id
                    JOIN perfis p ON p.id = up.perfil_id
                    WHERE u.ativo = 1
                      AND p.nome = 'Administrador'
                    """
                ).fetchone()[0]

                if administradores <= 1:
                    raise ValueError(
                        "Não é possível revogar o último perfil "
                        "de Administrador ativo."
                    )

            conexao.execute(
                """
                DELETE FROM usuario_perfis
                WHERE usuario_id = ? AND perfil_id = ?
                """,
                (usuario_id, perfil["id"])
            )

            _registrar_auditoria(
                conexao,
                operador_id,
                usuario_id,
                "PERFIL_REVOGADO",
                f"Perfil {nome_perfil} revogado do usuário ID {usuario_id}.",
                data_evento
            )

    return True
