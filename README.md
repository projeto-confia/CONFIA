# AUTOMATA

Aplicação que monitora redes sociais virtuais (RSV) com a finalidade de detectar Fake News e gerar alertas nas RSV.

# Dependências com Componentes do Ambiente
Esta aplicação depende da componente [database](https://github.com/projeto-confia/database).

# Instalação

Abra um terminal Linux e execute os seguintes comandos para a instalação e configuração do projeto:

Instale os pacotes necessários para o build

```
    sudo apt install build-essential python3-dev libpq-dev
```

Instale o [venv](https://docs.python.org/3/library/venv.html):

```
    sudo apt install python3-venv
```

Crie o ambiente virtual para o AUTOMATA:

```
    python3 -m venv .venv
```

Ative o ambiente virtual

```
    source .venv/bin/activate
```

Instale as dependências:

```
    pip install -r requirements.txt
```

# Configuração das variáveis de ambiente
Crie um arquivo `config.py` usando o arquivo `config.py.example` como base. A maioria dos parâmetros já estão calibrados para um melhor desempenho do AUTOMATA, apesar de você poder mudá-los conforme as orientações presentes da documentação.

De todo modo, você deverá editar os seguintes parãmetros usando suas credenciais de acesso:

* `EMAIL` - conta de e-mail que será empregada para disparo e recebimento de notificações.
* `TWITTER_CREDENTIAL` - credenciais que devem ser obtidas por você por meio de [solicitação ao Twitter](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api).
* `DATABASE` - parâmetros que você configurou na instalação da componente [database](https://github.com/projeto-confia/database).

Caso deseje uma execução em modo `verbose`, certifique-se de habilitar a variável `LOGGING.VERBOSE`.

# Inicialização do AUTOMATA

Para inicializar o AUTOMATA certifique-se que o ambiente virtual está ativado e, em seguida, execute no terminal:

```
    python3 -m src
```

# Desativar o ambiente virtual

No terminal, execute:

```
    deactivate
```