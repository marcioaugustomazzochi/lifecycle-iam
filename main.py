import sqlite3
from contextlib import closing

from modules.database import conectar, inicializar_banco
from modules.admission import admitir_colaborador
from modules.movement import movimentar_colaborador
from modules.termination import desligar_colaborador


def admitir():
    print("\n--- Admissão de colaborador ---")

    nome = input("Nome completo: ")
    email = input("E-mail corporativo: ")
    departamento = input("Departamento: ")
    cargo = input("Cargo: ")

    try:
        colaborador_id = admitir_colaborador(
            nome, email, departamento, cargo
        )
        print(f"\nColaborador cadastrado com sucesso! ID: {colaborador_id}")

    except ValueError as erro:
        print(f"\nErro: {erro}")

    except sqlite3.IntegrityError:
        print("\nErro: este e-mail já está cadastrado.")

    except sqlite3.Error as erro:
        print(f"\nErro no banco de dados: {erro}")


def movimentar():
    print("\n--- Movimentação de colaborador ---")

    try:
        colaborador_id = int(input("ID do colaborador: "))
        novo_departamento = input("Novo departamento: ")
        novo_cargo = input("Novo cargo: ")

        movimentar_colaborador(
            colaborador_id,
            novo_departamento,
            novo_cargo
        )

        print("\nMovimentação realizada com sucesso!")

    except ValueError as erro:
        print(f"\nErro: {erro}")

    except sqlite3.Error as erro:
        print(f"\nErro no banco de dados: {erro}")


def desligar():
    print("\n--- Desligamento de colaborador ---")

    try:
        colaborador_id = int(input("ID do colaborador: "))

        confirmacao = input(
            "Confirma o desligamento? (S/N): "
        ).strip().upper()

        if confirmacao != "S":
            print("\nOperação cancelada.")
            return

        desligar_colaborador(colaborador_id)

        print("\nDesligamento realizado com sucesso!")

    except ValueError as erro:
        print(f"\nErro: {erro}")

    except sqlite3.Error as erro:
        print(f"\nErro no banco de dados: {erro}")


def consultar_colaboradores():
    print("\n--- Consulta de colaboradores ---")

    with closing(conectar()) as conexao:
        colaboradores = conexao.execute(
            """
            SELECT id, nome, email, departamento, cargo, status
            FROM colaboradores
            ORDER BY id
            """
        ).fetchall()

    if not colaboradores:
        print("\nNenhum colaborador cadastrado.")
        return

    for colaborador in colaboradores:
        print(
            f"\nID: {colaborador['id']}"
            f"\nNome: {colaborador['nome']}"
            f"\nE-mail: {colaborador['email']}"
            f"\nDepartamento: {colaborador['departamento']}"
            f"\nCargo: {colaborador['cargo']}"
            f"\nStatus: {colaborador['status']}"
        )
        print("-" * 45)


def consultar_auditoria():
    print("\n--- Consulta de auditoria ---")

    with closing(conectar()) as conexao:
        registros = conexao.execute(
            """
            SELECT
                a.id,
                a.colaborador_id,
                c.nome,
                a.evento,
                a.descricao,
                a.data_evento
            FROM auditoria AS a
            LEFT JOIN colaboradores AS c
                ON a.colaborador_id = c.id
            ORDER BY a.id
            """
        ).fetchall()

    if not registros:
        print("\nNenhum registro de auditoria encontrado.")
        return

    for registro in registros:
        print(
            f"\nRegistro: {registro['id']}"
            f"\nColaborador: {registro['nome'] or 'Não identificado'}"
            f"\nEvento: {registro['evento']}"
            f"\nDescrição: {registro['descricao']}"
            f"\nData: {registro['data_evento']}"
        )
        print("-" * 45)


def main():
    inicializar_banco()

    while True:
        print("\n================================")
        print("         LIFECYCLE IAM")
        print(" Gerenciamento de Identidades")
        print("================================")
        print("1 - Admitir colaborador")
        print("2 - Movimentar colaborador")
        print("3 - Desligar colaborador")
        print("4 - Consultar colaboradores")
        print("5 - Consultar auditoria")
        print("0 - Sair")
        print("================================")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            admitir()

        elif opcao == "2":
            movimentar()

        elif opcao == "3":
            desligar()

        elif opcao == "4":
            consultar_colaboradores()

        elif opcao == "5":
            consultar_auditoria()

        elif opcao == "0":
            print("\nEncerrando o LifeCycle IAM. Até logo!")
            break

        else:
            print("\nOpção inválida. Tente novamente.")


if __name__ == "__main__":
    try:
        main()
    except sqlite3.Error as erro:
        print(f"\nErro ao acessar o banco de dados: {erro}")
