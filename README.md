


# Sistema de Gerenciamento de Usuários e Contas de Jogos

Este é um projeto de um aplicativo web simples para gerenciar usuários e suas contas em jogos, implementado em Python utilizando o framework Flask e o banco de dados SQLite. O sistema permite que os usuários se cadastrem, editem seus dados, visualizem a lista de usuários e excluam suas contas.

## Descrição do Projeto

Este projeto tem como objetivo criar uma plataforma simples para o gerenciamento de usuários e suas contas em jogos. O sistema utiliza o Flask como framework web e SQLite como banco de dados. Ele permite que os usuários se cadastrem, visualizem seus dados, editem suas informações e excluam sua conta do sistema. Além disso, é possível associar contas de diferentes jogos a um usuário.

## Funcionalidades

- Adicionar Usuário: Permite adicionar um novo usuário ao sistema através de um formulário.
- Listar Usuários: Exibe todos os usuários cadastrados em uma lista com opções de edição e exclusão.
- Editar Usuário: Permite editar as informações de um usuário, como nome, e-mail e senha.
- Deletar Usuário: Permite excluir um usuário do sistema.
Associar Contas de Jogos a Usuários: Cada usuário pode ter múltiplas contas associadas a diferentes jogos.

## Tecnologias Utilizadas

`Python`: Linguagem de programação utilizada para o desenvolvimento do backend.

`Flask`: Framework web utilizado para construir o backend.

`SQLite`: Banco de dados relacional utilizado para armazenar as informações dos usuários e das contas de jogos.

`HTML/CSS/JavaScript`: Tecnologias utilizadas para o frontend.

`Bootstrap`: Framework CSS para tornar a interface mais bonita e responsiva.

`Font Awesome`: Biblioteca de ícones para melhorar a interface com ícones nas ações.

## Estrutura do Banco de Dados
O banco de dados é composto por três tabelas principais:

1. Tabela de Usuários (`usuarios`)

- id_usuario (INTEGER, PK): Identificador único do usuário.
- nome (VARCHAR): Nome completo do usuário.
- email (VARCHAR): E-mail do usuário.
- senha (VARCHAR): Senha de acesso do usuário.
- data_cadastro (DATETIME): Data e hora de criação da conta. 

2. Tabela de Jogos (`jogos`)

- id_jogo (INTEGER, PK): Identificador único do jogo.
- nome_jogo (VARCHAR): Nome do jogo.
- desenvolvedor (VARCHAR): Nome do desenvolvedor do jogo.
- data_lancamento (DATE): Data de lançamento do jogo.

3. Tabela de Contas de Jogos (`contas_jogos`)

- id_conta (INTEGER, PK): Identificador único da conta.
- id_usuario (INTEGER, FK): Chave estrangeira referenciando o usuário.
- id_jogo (INTEGER, FK): Chave estrangeira referenciando o jogo.
- username (VARCHAR): Nome de usuário no jogo.
- data_criacao (DATETIME): Data de criação da conta no jogo.
- nivel (INTEGER): Nível ou status da conta no jogo.