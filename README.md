# AUTOMATA
Aplicação que monitora redes sociais virtuais (RSV) com a finalidade de detectar Fake News e gerar alertas nas RSV.

## Dependências com Componentes do Ambiente
Esta aplicação depende da componente [database](https://github.com/projeto-confia/database).

## Sistemas Operacionais homologados
A aplicação AUTOMATA foi desenvolvida e homologada para ser instalada e executada nos seguintes sistemas operacionais:
* Ubuntu 20.04 LTS

## Versão do Python suportada
* Python 3.9.7+

## Instalação da aplicação AUTOMATA
Abra um terminal e execute os seguintes comandos para a instalação e configuração da aplicação AUTOMATA:

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
    python -m venv .venv
```

Ative o ambiente virtual
```
    source .venv/bin/activate
```

Instale as dependências:
```
    pip install -r requirements.txt
```

## Configuração dos parâmetros da aplicação
Crie um arquivo `config.py` usando o arquivo `config.py.example` como base. A maioria dos parâmetros já estão calibrados para um melhor desempenho do AUTOMATA, apesar de você poder mudá-los conforme o [documento de especificação](/docs/parameters.md).

De todo modo, você deverá editar os seguintes parãmetros usando suas credenciais de acesso:

* `EMAIL` - conta de e-mail que será empregada para disparo e recebimento de notificações.
* `TWITTER_CREDENTIAL` - credenciais que devem ser obtidas por você por meio de [solicitação ao Twitter](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api).
* `DATABASE` - parâmetros que você configurou na instalação da componente [database](https://github.com/projeto-confia/database).

Caso deseje uma execução em modo `verbose`, certifique-se de habilitar o parâmetro `LOGGING.VERBOSE`.
## Configuração do módulo Schedule
O módulo `Schedule` é responsável pela execução das tarefas agendadas pela aplicação AUTOMATA, bem como pelo monitoramento e atualização dos parâmetros da aplicação. Para que o módulo seja executado pelo Sistema Operacional, proceda os seguintes passos:

Execute o comando abaixo para criar a variável de ambiente `AUTOMATA_PATH`. Certifique-se de substituir `<path_da_aplicação>` pelo caminho absoluto da aplicação AUTOMATA no Sistema Operacional.
```
echo "export AUTOMATA_PATH=<path_da_aplicação>" | sudo tee /etc/profile.d/automata.sh
```
Um exemplo comum para esse comando é:
```
echo "export AUTOMATA_PATH=/opt/automata" | sudo tee /etc/profile.d/automata.sh
```
Ative a variável de ambiente
```
source /etc/profile.d/automata.sh
```
Abra o arquivo `/etc/crontab` em modo de edição. Abaixo da linha `PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin` adicione a linha seguinte substituindo `<path_da_aplicação>` pelo caminho no Sistema Operacional:
```
AUTOMATA_PATH=<path_da_aplicação>
```
No final do arquivo, adicione a linha:
```
* * * * * root flock -n /var/lock/automata.schedule.lock ${AUTOMATA_PATH}/schedule.sh 2>> ${AUTOMATA_PATH}/logs/schedule.log
```
Salve e feche o arquivo `/etc/crontab`.

## Inicialização do AUTOMATA
Uma vez que todos os passos acima foram executados (principalmente a configuração do Módulo _Schedule_), o AUTOMATA será automaticamente inicializado em até 1 minuto. A `engine` que controla o fluxo de processamento do AUTOMATA se encarrega automaticamente de:
* Inicializar o AUTOMATA em caso de reinício do Sistema Operacional.
* Reinicar o AUTOMATA em caso de mudança do _status_ para _ERROR_.
* Reinicar o AUTOMATA em caso de alteração dos parâmetros de configuração via interface do Painel Administrativo.


## Desativação do AUTOMATA
Abra o arquivo `/etc/crontab`, comente a linha abaixo e salve o arquivo:
```
* * * * * root flock -n /var/lock/automata.schedule.lock ${AUTOMATA_PATH}/schedule.sh 2>> ${AUTOMATA_PATH}/logs/schedule.log
```
No terminal, execute:
```
ps -ef | grep "python -m src"
```
Identifique o `PID` do processo `./.venv/bin/python -m src`. Empregue o PID identificado no comando abaixo para encerrar o AUTOMATA:
```
kill <PID>
```

## Menção Bibliográfica

Caso cite o AUTOMATA em alguma produção científica, pedimos por gentileza que referencie o seguinte artigo:

```bibtex
@inproceedings{webmedia_estendido,
 author = {Augusto Fonseca and Carlos Moreira and Gabriel Machado and Paulo Freire and Ronaldo Goldschmidt},
 title = {AUTOMATA: Um Ambiente para Combate Automático de Fake News em Redes Sociais Virtuais},
 booktitle = {Anais Estendidos do XXVIII Simpósio Brasileiro de Sistemas Multimídia e Web},
 location = {Curitiba},
 year = {2022},
 keywords = {},
 issn = {2596-1683},
 pages = {79--82},
 publisher = {SBC},
 address = {Porto Alegre, RS, Brasil},
 doi = {10.5753/webmedia_estendido.2022.226555},
 url = {https://sol.sbc.org.br/index.php/webmedia_estendido/article/view/21989}}

```
