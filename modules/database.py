import sqlite3
from contextlib import closing
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "lifecycle.db"


def conectar():
    """Estabelece uma conexão com o banco de dados SQLite."""
    DATABASE_DIR.mkdir(exist_ok=True)

    conexao = sqlite3.connect(DATABASE_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def inicializar_banco():
    """Cria e atualiza a estrutura do banco de dados."""

    with closing(conectar()) as conexao:
        with conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS colaboradores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    departamento TEXT NOT NULL,
                    cargo TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'ATIVO',
                    data_admissao TEXT NOT NULL
                )
            """)

            conexao.execute("""
                CREATE TABLE IF NOT EXISTS auditoria (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    colaborador_id INTEGER,
                    evento TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    data_evento TEXT NOT NULL,
                    FOREIGN KEY (colaborador_id)
                        REFERENCES colaboradores(id)
                )
            """)

            conexao.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    colaborador_id INTEGER UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    senha_hash TEXT NOT NULL,
                    senha_salt TEXT NOT NULL,
                    ativo INTEGER NOT NULL DEFAULT 1
                        CHECK (ativo IN (0, 1)),
                    criado_em TEXT NOT NULL,
                    FOREIGN KEY (colaborador_id)
                        REFERENCES colaboradores(id)
                )
            """)

            conexao.execute("""
                CREATE TABLE IF NOT EXISTS perfis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    descricao TEXT NOT NULL
                )
            """)

            conexao.execute("""
                CREATE TABLE IF NOT EXISTS permissoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT NOT NULL UNIQUE,
                    descricao TEXT NOT NULL
                )
            """)

            conexao.execute("""
                CREATE TABLE IF NOT EXISTS perfil_permissoes (
                    perfil_id INTEGER NOT NULL,
                    permissao_id INTEGER NOT NULL,
                    PRIMARY KEY (perfil_id, permissao_id),
                    FOREIGN KEY (perfil_id)
                        REFERENCES perfis(id),
                    FOREIGN KEY (permissao_id)
                        REFERENCES permissoes(id)
                )
            """)

            conexao.execute("""
                CREATE TABLE IF NOT EXISTS usuario_perfis (
                    usuario_id INTEGER NOT NULL,
                    perfil_id INTEGER NOT NULL,
                    atribuido_em TEXT NOT NULL,
                    PRIMARY KEY (usuario_id, perfil_id),
                    FOREIGN KEY (usuario_id)
                        REFERENCES usuarios(id),
                    FOREIGN KEY (perfil_id)
                        REFERENCES perfis(id)
                )
            """)

            # Migração compatível com registros antigos de auditoria.
            colunas_auditoria = {
                coluna["name"]
                for coluna in conexao.execute(
                    "PRAGMA table_info(auditoria)"
                ).fetchall()
            }

            if "operador_id" not in colunas_auditoria:
                conexao.execute("""
                    ALTER TABLE auditoria
                    ADD COLUMN operador_id INTEGER
                    REFERENCES usuarios(id)
                """)

            conexao.execute("""
                CREATE INDEX IF NOT EXISTS idx_auditoria_operador
                ON auditoria(operador_id)
            """)

            # Perfis iniciais.
            perfis = [
                ("RH", "Gestão das operações do ciclo de vida."),
                ("TI", "Consulta de colaboradores e auditoria."),
                ("Auditor", "Consulta de colaboradores e auditoria."),
                ("Administrador", "Administração completa do sistema.")
            ]

            conexao.executemany("""
                INSERT OR IGNORE INTO perfis (nome, descricao)
                VALUES (?, ?)
            """, perfis)

            # Permissões disponíveis.
            permissoes = [
                ("colaborador.admitir", "Admitir colaboradores."),
                ("colaborador.movimentar", "Movimentar colaboradores."),
                ("colaborador.desligar", "Desligar colaboradores."),
                ("colaborador.consultar", "Consultar colaboradores."),
                ("auditoria.consultar", "Consultar registros de auditoria."),
                ("permissao.gerenciar", "Gerenciar perfis e permissões.")
            ]

            conexao.executemany("""
                INSERT OR IGNORE INTO permissoes (codigo, descricao)
                VALUES (?, ?)
            """, permissoes)

            # Matriz inicial de permissões.
            matriz = {
                "RH": [
                    "colaborador.admitir",
                    "colaborador.movimentar",
                    "colaborador.desligar",
                    "colaborador.consultar"
                ],
                "TI": [
                    "colaborador.consultar",
                    "auditoria.consultar"
                ],
                "Auditor": [
                    "colaborador.consultar",
                    "auditoria.consultar"
                ],
                "Administrador": [
                    "colaborador.admitir",
                    "colaborador.movimentar",
                    "colaborador.desligar",
                    "colaborador.consultar",
                    "auditoria.consultar",
                    "permissao.gerenciar"
                ]
            }

            for nome_perfil, codigos in matriz.items():
                perfil = conexao.execute(
                    "SELECT id FROM perfis WHERE nome = ?",
                    (nome_perfil,)
                ).fetchone()

                for codigo in codigos:
                    permissao = conexao.execute(
                        "SELECT id FROM permissoes WHERE codigo = ?",
                        (codigo,)
                    ).fetchone()

                    conexao.execute("""
                        INSERT OR IGNORE INTO perfil_permissoes
                        (perfil_id, permissao_id)
                        VALUES (?, ?)
                    """, (perfil["id"], permissao["id"]))

    print("Banco de dados inicializado com sucesso.")


