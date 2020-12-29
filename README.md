# Projeto CONFIA

*Detectando e interceptando Fake News em Redes Sociais*

## 1. Pré-requisitos

Abra um terminal Linux e execute os seguintes comandos para a instalação e configuração do projeto:

#### 1.1. Instale os pacotes necessários para o build

```
sudo apt install build-essential python3-dev libpq-dev
```

#### 1.2. Faça o clone do repositório

```
git clone https://github.com/projeto-confia/CONFIA
```

#### 1.3. Configure o banco de dados (docker e docker-compose devem estar instalados)

Edite o arquivo `docker.env.example`, inserindo seu e-mail e uma senha definida por você. Estas serão as credenciais para acessar o pgAdmin. Após a edição, renomeie o arquivo para `docker.env`.

Inicialize os serviços `postgreSQL` e `pgAdmin`. Abra um terminal, acesse o diretório que contém o arquivo `docker-compose.yml` e execute:

```
docker-compose up -d
```

Se tudo correr bem, você verá as seguintes mensagens no terminal

```
Starting postgres ... done
Starting pgadmin  ... done
```

Se quiser utilizar o `pgAdmin`, acesse o serviço pelo browser (localhost:16543) e faça o login com as credencias que você configurou no arquivo `docker.env`. Após o login, clique em `Add New Server` e além do nome do server (escolhido por você), na aba `Connection` insira os seguintes dados:

```
Host name/address: postgres
Usarname: admin
Password: postgres
```

Para encerrar os serviços `postgreSQL` e `pgAdmin`, abra um terminal, acesse o diretório que contém o arquivo `docker-compose.yml` e execute:

```
docker-compose stop
```

Se tudo correr bem, você verá as seguintes mensagens no terminal

```
Stopping pgadmin  ... done
Stopping postgres ... done
```

#### 1.4. Instale o [venv](https://docs.python.org/3/library/venv.html):

```
sudo apt install python3-venv
```

#### 1.5. Ative o ambiente

```
source confia/bin/activate
```

#### 1.6. Instale as demais dependências:

```
sudo pip3 install -r requirements.txt
```

*Caso seja necessário, digite `deactivate` no terminal para desativar o ambiente.* 

## 2. Rodando o projeto

Para rodar o projeto, verifique se o ambiente está ativado e, em seguida, digite no terminal:

```
python3 -m confia
```