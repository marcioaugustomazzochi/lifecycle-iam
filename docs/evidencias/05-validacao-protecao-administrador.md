# Evidência 05 — Validação da Proteção do Administrador

## Objetivo

Verificar se o LifeCycle IAM impede a revogação do último perfil de Administrador ativo.

## Procedimento

Foi realizada uma tentativa controlada de revogação do perfil Administrador da conta principal (ID 1).

## Resultado

O sistema bloqueou a operação e apresentou a mensagem:

`ValueError: Não é possível revogar o último perfil de Administrador ativo.`

## Verificações complementares

- Foi confirmado que existe apenas um Administrador ativo.
- O perfil Administrador permaneceu atribuído à conta principal.
- A consulta ao histórico não identificou evento de revogação de perfil.
- Os três registros de colaboradores existentes foram preservados.

## Conclusão

O teste confirmou o funcionamento da proteção contra a revogação do último perfil de Administrador ativo.

## Ambiente

Teste realizado em ambiente local, utilizando Python, SQLite e dados fictícios.