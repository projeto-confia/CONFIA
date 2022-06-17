# Documento de especificação dos parâmetros da aplicação AUTOMATA

Este documento especifica os parâmetros da aplicação AUTOMATA. Os parâmetros devem ser configurados no arquivo `config.py` gerado por você com base no arquivo [src/config.py.example](/src/config.py.example).

# Parâmetros

`LOGGING.VERBOSE`
> Valores aceitos: `{True, False}`. 
<br>Se habilitado imprime no terminal de comando as etapas de processamento dos módulos do AUTOMATA.

`LOGGING.SMTP_LOG`
> Valores aceitos: `{True, False}`. 
<br>Se habilitado envia para o e-mail configurado notificações em caso de falhas ou erros críticos (level WARNING ou superior).

`LOGGING.FILE_PATH`
> Valores aceitos: `string`. 
<br>Endereço no sistema de arquivos local para o arquivo que armazenará os logs do sistema.

`LOGGING.NAME`
> Valores aceitos: `string`. 
<br>Nome global do logger do sistema. Devido ao sistema ter sido configurado para usar um único logger, mudanças no valor desse parâmetro não terão impacto no sistema.

`STATUS.STOPPED`
> Valores aceitos: `int`. 
<br>Valor numérico inteiro que representa o estado de ambiente `PARADO`. É recomendado não alterar este valor.

`STATUS.RUNNING`
> Valores aceitos: `int`. 
<br>Valor numérico inteiro que representa o estado de ambiente `EM PROCESSAMENTO`. É recomendado não alterar este valor.

`STATUS.ERROR`
> Valores aceitos: `int`. 
<br>Valor numérico inteiro que representa o estado de ambiente `EM ESTADO CRÍTICO`. É recomendado não alterar este valor.

`ENGINE.FREQUENCY`
> Valores aceitos: `int`. 
<br>Valor numérico inteiro que define o tempo de intervalo em segundos entre cada inicialização de um novo ciclo de processamento do AUTOMATA. Cada ciclo de processamento do AUTOMATA engloba as etapas de processamento de todos os módulos do sistema.

`ENGINE.MONITOR_ACTIVATED`
> Valores aceitos: `{True, False}`. 
<br>Se habilitado ativa o módulo de monitoramento.

`ENGINE.FACT_CHECK_MANAGER_ACTIVATED`
> Valores aceitos: `{True, False}`. 
<br>Se habilitado ativa o módulo de processamento de checagem.

`ENGINE.DETECTOR_ACTIVATED`
> Valores aceitos: `{True, False}`. 
<br>Se habilitado ativa o módulo de detecção.

`ENGINE.INTERVENTOR_ACTIVATED`
> Valores aceitos: `{True, False}`. 
<br>Se habilitado ativa o módulo de intervenção.

`ENGINE.SCRAPING_ACTIVATED`
> Valores aceitos: `{True, False}`. 
<br>Se habilitado ativa o módulo de _scraping_. Este módulo realiza o download automático de análises de Fake News publicadas pelas agências de checagem de fatos. Os dados obtidos são armazenados no banco de dados do AUTOMATA.

`MONITOR.STREAM_FILTER_OF_SHARES`
> valores aceitos: `int`
<br>Valor numérico inteiro **maior ou igual a 0**. Atua como um limiar para descarte dos *tweets* colhidos via *streaming* que possuem um número de compartilhamentos menor do que o valor definido em `MONITOR.STREAM_FILTER_OF_SHARES`.

`MONITOR.STREAM_TIME`
> Valores aceitos: `int`. 
<br>Valor numérico inteiro que define o tempo de coleta em segundos de publicações em tempo real (_stream_) das redes sociais virtuais.

`MONITOR.SEARCH_TAGS`
> Valores aceitos: `array de strings`. 
<br>Define as palavras-chave de busca. Uma publicação na rede social virtual somente será coletada pelo AUTOMATA se conter pelo menos uma palavra-chave definida nesta variável.

`MONITOR.WINDOW_SIZE`
> Valores aceitos: `int`. 
<br>Valor numérico inteiro que define o tamanho em dias da janela de tempo passada para busca de publicações similares no banco de dados. Publicações coletadas da rede social virtual serão associadas (se possível) à publicações já existentes na base de dados caso o texto das publicações sejam similares. Para o cálculo da similaridade e associação, serão consideradas somente as publicações da base de dados que tem data de publicação igual ou superior à WINDOW_SIZE dias anteriores à data atual.

`DETECTOR.TRAIN_ICS`
> Valores aceitos: `{True, False}`. 
<br>Se habilitado, realiza o treinamento do modelo de inteligência artificial a cada novo ciclo de processamento do AUTOMATA. 

`INTERVENTOR.WINDOW_SIZE`
> Valores aceitos: `int`. 
<br>Valor numérico inteiro que define o tamanho em dias da janela de tempo passada para seleção de publicações candidatas à checagem. Serão consideradas somente as publicações da base de dados que tem data de publicação igual ou superior à WINDOW_SIZE dias anteriores à data atual. `Este parâmetro compõe o conjunto de parâmetros do algoritmo de seleção de publicações para checagem`.

`INTERVENTOR.PROB_CLASSIF_THRESHOLD`
> Valores aceitos: `float, range [0-1]`.
<br>Valor numérico contínuo entre 0 e 1 que define o grau de certeza atribuído à publicação pelo módulo de detecção que servirá como limiar para seleção de publicações candidatas à checagem. Valores mais próximos de 0 indicam baixa certeza, enquanto valores mais próximos de 1 indicam alta certeza. Serão consideradas somente as publicações com grau de certeza acima de PROB_CLASSIF_THRESHOLD. `Este parâmetro compõe o conjunto de parâmetros do algoritmo de seleção de publicações para checagem`.

`INTERVENTOR.NUM_NEWS_TO_SELECT`
> Valores aceitos: `int`. 
<br>Valor numérico inteiro que define o número de publicações que serão enviadas para checagem. `Este parâmetro compõe o conjunto de parâmetros do algoritmo de seleção de publicações para checagem`.

`INTERVENTOR.CURATOR`
> Valores aceitos: `{True, False}`. 
<br>Se habilitado redireciona as publicações selecionadas para checagem para o módulo de curadoria.

`INTERVENTOR.SOCIAL_MEDIA_ALERT_ACTIVATE`
> Valores aceitos: `{True, False}`. 
<br>Se habilitado dispara um alerta PREMATURO na rede social virtual para cada publicação enviada para checagem, informando que a publicação foi detectada como POSSÍVEL Fake News. `Não implementado nesta versão`.

`FCMANAGER.SOCIAL_MEDIA_ALERT_ACTIVATE`
> Valores aceitos: `{True, False}`. 
<br>Se habilitado dispara um alerta na rede social virtual para cada publicação confirmada pela agẽncia de checagem de fatos como sendo Fake News, informando que a notícia foi CONFIRMADA como Fake News. `Não implementado nesta versão`.

`EMAIL.ACCOUNT`
> Valores aceitos: `string`. 
<br>Conta de e-mail que será usada para envio e recebimento de notificações geradas pelo AUTOMATA. A conta de e-mail deve estar configurada para permitir o acesso por softwares de terceiros. `Somente contas de e-mail do GMail são aceitas nesta versão`.

`EMAIL.PASSWORD`
> Valores aceitos: `string`. 
<br>Senha de acesso da onta de e-mail configurada em `EMAIL.ACCOUNT`.

`TWITTER_CREDENTIAL.CONSUMER_KEY`
> Valores aceitos: `string`. 
<br>Chave CONSUMER_KEY das credenciais de acesso à API do twitter.

`TWITTER_CREDENTIAL.CONSUMER_SECRET`
> Valores aceitos: `string`. 
<br>Chave CONSUMER_SECRET das credenciais de acesso à API do twitter.

`TWITTER_CREDENTIAL.ACCESS_TOKEN`
> Valores aceitos: `string`. 
<br>Chave ACCESS_TOKEN das credenciais de acesso à API do twitter.

`TWITTER_CREDENTIAL.ACCESS_TOKEN_SECRET`
> Valores aceitos: `string`. 
<br>Chave ACCESS_TOKEN_SECRET das credenciais de acesso à API do twitter.

`TEXT_PREPROCESSOR.DEFAULT_THRESHOLD`
> Valores aceitos: `int, range [0-100]`.
<br>Valor numérico inteiro entre 0 e 100 que define o grau de similaridade entre textos de publicações que servirá como limiar para rotular as publicações como similares. Valores mais próximos de 0 indicam baixa similaridade, enquanto valores mais próximos de 1 indicam alta similaridade.

`DATABASE.HOST`
> Valores aceitos: `string`. 
<br>Endereço do servidor de banco de dados.

`DATABASE.PORT`
> Valores aceitos: `string`. 
<br>Porta de comunicação com o servidor de banco de dados.

`DATABASE.NAME`
> Valores aceitos: `string`. 
<br>Nome da base de dados.

`DATABASE.USER`
> Valores aceitos: `string`. 
<br>Conta de usuário com acesso à base de dados.

`DATABASE.PASSWORD`
> Valores aceitos: `string`. 
<br>Senha de usuário com acesso à base de dados.
