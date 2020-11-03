# Projeto CONFIA

*Detectando e interceptando Fake News em Redes Sociais*

## 1. Pré-requisitos

Abra um terminal Linux e execute os seguintes comandos para a instalação e configuração do projeto:

#### 1.1. Clone o repositório

```
git clone https://github.com/projeto-confia/CONFIA
```

#### 1.2. Instale o [venv](https://docs.python.org/3/library/venv.html):

```
sudo apt install python3-venv
```

#### 1.3. Instale as demais dependências:

```
sudo pip3 install -r requirements.txt
```
#### 1.4. Ative o ambiente

```
source confia/bin/activate
```

*Caso seja necessário, digite `deactivate` no terminal para desativar o ambiente.* 

## 2. Rodando o projeto

Para rodar o projeto, verifique se o ambiente está ativado e, em seguida, digite no terminal:

```
python3 -m confia
```