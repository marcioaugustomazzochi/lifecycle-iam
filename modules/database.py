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
    """Cria as tabelas necessárias para o sistema."""

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

    print("Banco de dados inicializado com sucesso.")
