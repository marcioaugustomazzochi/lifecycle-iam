import sqlite3
from contextlib import closing
from getpass import getpass

from modules.database import conectar, inicializar_banco
from modules.auth import autenticar_usuario, criar_usuario
from modules.rbac import (
    listar_perfis_usuario,
    usuario_tem_permissao,
    exigir_permissao,
    atribuir_perfil,
    revogar_perfil
)
from modules.admission import admitir_colaborador
from modules.movement import movimentar_colaborador
from modules.termination import desligar_colaborador


def admitir(operador_id):
    print("\n--- Admissão de colaborador ---")

    nome = input("Nome completo: ")
    email = input("E-mail corporativo: ")
    departamento = input("Departamento: ")
    cargo = input("Cargo: ")

    try:
        colaborador_id = admitir_colaborador(
            nome, email, departamento, cargo, operador_id
        )
        print(f"\nColaborador cadastrado com sucesso! ID: {colaborador_id}")

    except PermissionError as erro:
        print(f"\n{erro}")

    except ValueError as erro:
        print(f"\nErro: {erro}")

    except sqlite3.IntegrityError:
        print("\nErro: este e-mail já está cadastrado.")

    except sqlite3.Error as erro:
        print(f"\nErro no banco de dados: {erro}")


def movimentar(operador_id):
    print("\n--- Movimentação de colaborador ---")

    try:
        colaborador_id = int(input("ID do colaborador: "))
        novo_departamento = input("Novo departamento: ")
        novo_cargo = input("Novo cargo: ")

        movimentar_colaborador(
            colaborador_id,
            novo_departamento,
            novo_cargo,
            operador_id
        )

        print("\nMovimentação realizada com sucesso!")

    except PermissionError as erro:
        print(f"\n{erro}")

    except ValueError as erro:
        print(f"\nErro: {erro}")

    except sqlite3.Error as erro:
        print(f"\nErro no banco de dados: {erro}")


def desligar(operador_id):
    print("\n--- Desligamento de colaborador ---")

    try:
        colaborador_id = int(input("ID do colaborador: "))

        confirmacao = input(
            "Confirma o desligamento? (S/N): "
        ).strip().upper()

        if confirmacao != "S":
            print("\nOperação cancelada.")
            return

        desligar_colaborador(colaborador_id, operador_id)

        print("\nDesligamento realizado com sucesso!")

    except PermissionError as erro:
        print(f"\n{erro}")

    except ValueError as erro:
        print(f"\nErro: {erro}")

    except sqlite3.Error as erro:
        print(f"\nErro no banco de dados: {erro}")


def consultar_colaboradores(operador_id):
    exigir_permissao(operador_id, "colaborador.consultar")

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


def consultar_auditoria(operador_id):
    exigir_permissao(operador_id, "auditoria.consultar")

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
                a.data_evento,
                u.email AS operador
            FROM auditoria AS a
            LEFT JOIN colaboradores AS c
                ON a.colaborador_id = c.id
            LEFT JOIN usuarios AS u
                ON a.operador_id = u.id
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
            f"\nOperador: {registro['operador'] or 'Não identificado'}"
            f"\nData: {registro['data_evento']}"
        )
        print("-" * 45)


def gerenciar_perfis(operador_id):
    exigir_permissao(operador_id, "permissao.gerenciar")

    while True:
        print("\n--- Gerenciamento de perfis e usuários ---")
        print("1 - Consultar usuários")
        print("2 - Atribuir perfil")
        print("3 - Revogar perfil")
        print("4 - Cadastrar novo usuário")
        print("0 - Voltar")

        opcao = input("Escolha uma opção: ").strip()

        try:
            if opcao == "1":
                with closing(conectar()) as conexao:
                    usuarios = conexao.execute(
                        """
                        SELECT id, email, ativo, colaborador_id
                        FROM usuarios
                        ORDER BY id
                        """
                    ).fetchall()

                print("\n--- Usuários cadastrados ---")

                for usuario in usuarios:
                    perfis = listar_perfis_usuario(usuario["id"])

                    situacao = (
                        "ATIVO" if usuario["ativo"] == 1 else "INATIVO"
                    )

                    print(
                        f"\nID: {usuario['id']}"
                        f"\nE-mail: {usuario['email']}"
                        f"\nSituação: {situacao}"
                        f"\nColaborador vinculado: "
                        f"{usuario['colaborador_id'] or 'Nenhum'}"
                        f"\nPerfis: {', '.join(perfis) or 'Nenhum'}"
                    )
                    print("-" * 40)

                if not usuarios:
                    print("\nNenhum usuário cadastrado.")

            elif opcao == "2":
                usuario_id = int(input("ID do usuário: "))
                nome_perfil = input("Nome do perfil: ")

                atribuir_perfil(
                    operador_id,
                    usuario_id,
                    nome_perfil
                )

                print("\nPerfil atribuído com sucesso.")

            elif opcao == "3":
                usuario_id = int(input("ID do usuário: "))
                nome_perfil = input("Nome do perfil: ")

                revogar_perfil(
                    operador_id,
                    usuario_id,
                    nome_perfil
                )

                print("\nPerfil revogado com sucesso.")

            elif opcao == "4":
                print("\n--- Cadastro de novo usuário ---")

                email = input("E-mail de acesso: ").strip()

                senha = getpass(
                    "Crie uma senha (mínimo 12 caracteres): "
                )

                confirmacao = getpass("Confirme a senha: ")

                if senha != confirmacao:
                    raise ValueError("As senhas não coincidem.")

                print(
                    "\nPerfis disponíveis: "
                    "RH, TI, Auditor, Administrador"
                )

                nome_perfil = input("Perfil inicial: ").strip()

                vinculo = input(
                    "Vincular a um colaborador existente? (S/N): "
                ).strip().upper()

                colaborador_id = None

                if vinculo == "S":
                    colaborador_id = int(
                        input("ID do colaborador: ")
                    )

                elif vinculo != "N":
                    raise ValueError("Opção de vínculo inválida.")

                novo_usuario_id = criar_usuario(
                    operador_id,
                    email,
                    senha,
                    nome_perfil,
                    colaborador_id
                )

                print(
                    "\nUsuário criado com sucesso! "
                    f"ID: {novo_usuario_id}"
                )

            elif opcao == "0":
                break

            else:
                print("\nOpção inválida.")

        except PermissionError as erro:
            print(f"\n{erro}")

        except ValueError as erro:
            print(f"\nErro: {erro}")

        except sqlite3.IntegrityError:
            print("\nErro: este e-mail já está cadastrado.")

        except sqlite3.Error as erro:
            print(f"\nErro no banco de dados: {erro}")


def autenticar():
    print("\n================================")
    print("       LOGIN - LIFECYCLE IAM")
    print("================================")

    while True:
        email = input("E-mail: ").strip()
        senha = getpass("Senha: ")

        usuario = autenticar_usuario(email, senha)

        if usuario is not None:
            print("\nAutenticação realizada com sucesso.")
            return usuario

        print("\nE-mail ou senha inválidos, ou usuário inativo.")

        tentar_novamente = input(
            "Tentar novamente? (S/N): "
        ).strip().upper()

        if tentar_novamente != "S":
            return None


def executar_menu(usuario):
    operador_id = usuario["id"]

    while True:
        perfis = listar_perfis_usuario(operador_id)

        print("\n================================")
        print("         LIFECYCLE IAM")
        print(" Gerenciamento de Identidades")
        print("================================")
        print(f"Operador: {usuario['email']}")
        print(f"Perfis: {', '.join(perfis)}")
        print("--------------------------------")

        if usuario_tem_permissao(operador_id, "colaborador.admitir"):
            print("1 - Admitir colaborador")

        if usuario_tem_permissao(operador_id, "colaborador.movimentar"):
            print("2 - Movimentar colaborador")

        if usuario_tem_permissao(operador_id, "colaborador.desligar"):
            print("3 - Desligar colaborador")

        if usuario_tem_permissao(operador_id, "colaborador.consultar"):
            print("4 - Consultar colaboradores")

        if usuario_tem_permissao(operador_id, "auditoria.consultar"):
            print("5 - Consultar auditoria")

        if usuario_tem_permissao(operador_id, "permissao.gerenciar"):
            print("6 - Gerenciar perfis e permissões")

        print("0 - Encerrar sessão")
        print("9 - Sair do sistema")
        print("================================")

        opcao = input("Escolha uma opção: ").strip()

        try:
            if opcao == "1":
                admitir(operador_id)

            elif opcao == "2":
                movimentar(operador_id)

            elif opcao == "3":
                desligar(operador_id)

            elif opcao == "4":
                consultar_colaboradores(operador_id)

            elif opcao == "5":
                consultar_auditoria(operador_id)

            elif opcao == "6":
                gerenciar_perfis(operador_id)

            elif opcao == "0":
                print("\nSessão encerrada.")
                return True

            elif opcao == "9":
                print("\nEncerrando o LifeCycle IAM. Até logo!")
                return False

            else:
                print("\nOpção inválida ou não disponível.")

        except PermissionError as erro:
            print(f"\n{erro}")

        except sqlite3.Error as erro:
            print(f"\nErro no banco de dados: {erro}")


def main():
    inicializar_banco()

    while True:
        usuario = autenticar()

        if usuario is None:
            print("\nAcesso não realizado.")
            break

        continuar = executar_menu(usuario)

        if not continuar:
            break


if __name__ == "__main__":
    try:
        main()
    except sqlite3.Error as erro:
        print(f"\nErro ao acessar o banco de dados: {erro}")
