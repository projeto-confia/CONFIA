# packages
import time, os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from src.scraping.dao import ScrapingDAO
import logging
from src.config import Config as config


# TODO: refatorar
# implementar uma interface
# implementar uma classe (extends interface) para cada agẽncia de checagem
class Scraping(object):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._dao = ScrapingDAO()
        self._article_csv_filename = 'articles.csv'
        self._article_csv_path = os.path.join("src", "data", self._article_csv_filename)
        # TODO: o método abaixo está buscando o count do id_agency
        # refatorar, usando o método já existente no DAO (get_id_agency)
        self.initial_load = False if self._dao.get_num_storaged_articles() else True
        self._logger.info("Scraping initialized.")
        
        
    def fetch_data(self):
        self._logger.info("Fetching data...")
        
        # scraping
        page = 1
        url = "https://www.boatos.org/tag/coronavirus/page/{}".format(page)
        response = requests.get(url)

        while response.status_code == 200:
            self._logger.info('scraping page {}...'.format(page))
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.findAll('article')
            
            for article in articles:
                self._write_in_csv(article)
            
            time.sleep(5)
            page += 1
            url = "https://www.boatos.org/tag/coronavirus/page/{}".format(page)
            response = requests.get(url)
            
            
    def persist_data(self):
        # TODO: verificar antes se há arquivo de dados
        #       caso contrário, return
        self._logger.info('Persisting data...')
        self._dao.insert_articles(self.initial_load)
            
            
    def update_data(self):
        self._logger.info("Updating data...")
        
        # recupera o último datetime no banco
        last_article_datetime = self._dao.get_last_article_datetime()
        
        # recupera a página mais recente do site boatos.org
        url = "https://www.boatos.org/tag/coronavirus/page/1"
        response = requests.get(url)
        if response.status_code != 200:
            self._logger.info('Unreachable URL! Response status code: {}'.format(response.status_code))
            raise Exception('Unreachable URL! Request Status Code: {}'.format(response.status_code))
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.findAll('article')
        
        # insere artigos com datetime superior ao último cadastrado no banco
        for article in articles:
            current_article_datetime_str = article.select_one('.entry-date')['datetime'][:-6]
            current_article_datetime = datetime.strptime(current_article_datetime_str, '%Y-%m-%dT%H:%M:%S')
            if current_article_datetime <= last_article_datetime:
                return
            self._write_in_csv(article)


    def _parse_to_dict(self, article):
        # init
        parsed_article = dict()
        parsed_article['name_agency'] = 'boatos.org'
        parsed_article['publication_external_id'] = article['id'][5:]
        element = article.select_one('.entry-title > a')
        parsed_article['publication_title'] = element['title'][:-7]
        parsed_article['publication_url'] = element['href']
        parsed_article['publication_datetime'] = article.select_one('.entry-date')['datetime']
        parsed_article['publication_tags'] = [tag.text for tag in article.select('.tag-links > a') if tag.text not in ('Lista de fake news sobre o novo coronavírus (Covid-19)')]
        return parsed_article
            
            
    def _write_in_csv(self, article):
        parsed_article = self._parse_to_dict(article)
        self._dao.write_in_csv_from_dict(parsed_article, self._article_csv_path)
