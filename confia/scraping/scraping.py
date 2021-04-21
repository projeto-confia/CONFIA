# packages
import time, os
import requests
from bs4 import BeautifulSoup
from confia.scraping.dao import ScrapingDAO


class Scraping(object):
    
    def __init__(self):
        self._dao = ScrapingDAO()
        self._article_csv_filename = 'articles.csv'
        self._article_csv_path = os.path.join("confia", "data", self._article_csv_filename)
        
        
    def scrape_all_data(self):
        # scraping
        page = 1
        url = "https://www.boatos.org/tag/coronavirus/page/{}".format(page)
        response = requests.get(url)

        while response.status_code == 200:
            print('\tscraping page {}...'.format(page))
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.findAll('article')
            
            for article in articles:
                self._write_in_csv(article)
            
            time.sleep(5)
            page += 1
            url = "https://www.boatos.org/tag/coronavirus/page/{}".format(page)
            response = requests.get(url)


    def _parse_to_dict(self, article):
        # init
        parsed_article = dict()
        parsed_article['external_id'] = article['id'][5:]
        element = article.select_one('.entry-title > a')
        parsed_article['title'] = element['title'][:-7]
        parsed_article['url'] = element['href']
        parsed_article['datetime'] = article.select_one('.entry-date')['datetime']
        parsed_article['tags'] = [tag.text for tag in article.select('.tag-links > a') if tag.text not in ('Lista de fake news sobre o novo coronavírus (Covid-19)')]
        return parsed_article
            
            
    def _write_in_csv(self, article):
        parsed_article = self._parse_to_dict(article)
        self._dao.write_in_csv_from_dict(parsed_article, self._article_csv_path)
