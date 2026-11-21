# LifeCycle IAM — Gestão do Ciclo de Vida de Identidades com Python

---

## 📌 Descrição do Projeto

O **LifeCycle IAM** é um projeto desenvolvido em Python com foco em **Identity and Access Management (IAM)**, gerenciamento de identidades digitais e controle de acesso.

A solução simula processos do ciclo de vida de colaboradores em um ambiente organizacional, contemplando admissão (Joiner), movimentação (Mover) e desligamento (Leaver), associados à autenticação de operadores, controle de acesso baseado em funções (RBAC) e registro de auditoria.

O projeto utiliza SQLite para persistência dos dados e demonstra a aplicação de controles de segurança, segregação de responsabilidades e rastreabilidade das operações.

---

## ⚙️ Funcionalidades Implementadas

### 1. Gestão do Ciclo de Vida — Joiner, Mover e Leaver

**Admissão (Joiner)**

- Cadastro de novos colaboradores.
- Validação de informações obrigatórias.
- Verificação de e-mails duplicados.
- Registro da admissão no histórico de auditoria.
- Controle de autorização para executar a operação.

**Movimentação (Mover)**

- Atualização de departamento e cargo.
- Registro das informações anteriores e atualizadas.
- Histórico das movimentações para auditoria.
- Verificação de permissões antes da alteração.

**Desligamento (Leaver)**

- Alteração do status do colaborador para INATIVO.
- Impedimento de novo desligamento de colaborador já inativo.
- Desativação de conta de usuário vinculada, quando existente.
- Registro do evento de desligamento na auditoria.

### 2. Autenticação e Gerenciamento de Usuários

- Autenticação individual por e-mail e senha.
- Proteção de senhas utilizando PBKDF2-HMAC-SHA256, com salt aleatório.
- Controle de contas de operadores ativos e inativos.
- Associação opcional entre uma conta de operador e um colaborador.
- Provisionamento inicial seguro do administrador, sem credenciais padrão.

### 3. Controle de Acesso — RBAC

Implementação do modelo **Role-Based Access Control (RBAC)**, com permissões associadas aos perfis de acesso.

**Perfis implementados:**

| Perfil | Responsabilidades |
|---|---|
| RH | Admissão, movimentação, desligamento e consulta de colaboradores |
| TI | Consulta de colaboradores e auditoria |
| Auditor | Consulta de colaboradores e auditoria |
| Administrador | Acesso administrativo e gerenciamento de permissões |

O sistema realiza verificações de autorização no backend antes da execução das operações.

**Controles adicionais:**

- Atribuição e revogação de perfis.
- Suporte a múltiplos perfis por usuário.
- Proteção contra a revogação do último perfil de Administrador ativo.
- Registro de alterações de perfis na auditoria.

### 4. Auditoria e Rastreabilidade

- Registro das operações realizadas.
- Identificação do operador responsável.
- Histórico de eventos relacionados aos colaboradores.
- Registro de operações administrativas e alterações de perfis.
- Persistência dos registros em banco de dados SQLite.

---

## 🛠️ Tecnologias Utilizadas

- Python 3
- SQLite
- SQL
- PBKDF2-HMAC-SHA256
- Git
- GitHub

---

## 📁 Estrutura do Projeto

```text
lifecycle-iam/
├── docs/
│   └── evidencias/
│       ├── 01-menu-principal.png
│       ├── 02-consulta-colaboradores.png
│       ├── 03-historico-auditoria-parte1 a 4.png
│       ├── 04-historico-auditoria-parte 2 - 5 a 7.png
│       ├── 05-validacao-protecao-administrador.md
│       └── DESCRICAO.md
│
├── modules/
│   ├── __init__.py
│   ├── admission.py
│   ├── auth.py
│   ├── bootstrap.py
│   ├── database.py
│   ├── movement.py
│   ├── rbac.py
│   └── termination.py
│
├── main.py
├── README.md
├── LICENSE
└── .gitignore
```

---

## 📸 Evidências de Funcionamento

A pasta `docs/evidencias/` contém registros dos testes realizados em ambiente local.

As evidências incluem:

- **01 — Menu Principal:** opções disponíveis no sistema.
- **02 — Consulta de Colaboradores:** visualização dos colaboradores cadastrados.
- **03 e 04 — Histórico de Auditoria:** registros das operações realizadas.
- **05 — Proteção do Administrador:** documentação do teste que confirmou o bloqueio da revogação do último perfil de Administrador ativo.

---

## 🔐 Ambiente de Desenvolvimento e Segurança

O projeto utiliza um ambiente local de simulação, com dados fictícios.

O banco de dados SQLite é armazenado localmente e não faz parte dos arquivos publicados no repositório.

As senhas dos usuários são protegidas por derivação criptográfica com PBKDF2-HMAC-SHA256 e salt aleatório.

O sistema não realiza criação, alteração ou desativação de contas corporativas reais, nem possui integração com serviços externos de identidade.

Possíveis integrações com serviços de diretório e plataformas IAM poderão ser consideradas em etapas futuras, exclusivamente em ambientes de teste autorizados.

---

## 🎯 Objetivo

Aplicar conceitos de Identity and Access Management, segurança da informação, autenticação, autorização, RBAC, gestão de identidades e automação de processos.

O projeto busca demonstrar, de maneira prática, como controles de acesso e processos de gerenciamento de identidades podem contribuir para a governança e a segurança em ambientes organizacionais.

---

## 🔗 Repositório no GitHub

[LifeCycle IAM — Acessar projeto](https://github.com/marcioaugustomazzochi/lifecycle-iam)

---

## 📄 Licença

Este projeto está disponibilizado sob a licença MIT.

---

## 🚧 Status do Projeto

Projeto em desenvolvimento contínuo, com implementação de funcionalidades de gestão do ciclo de vida de identidades, autenticação, controle de acesso RBAC e auditoria.
