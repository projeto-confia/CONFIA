# packages
import time
import requests
from bs4 import BeautifulSoup


# scraping
page = 1
url = "https://www.boatos.org/tag/coronavirus/page/{}".format(page)
response = requests.get(url)

while response.status_code == 200:
    print('###################################################')
    print(url)
    print('page {} exists'.format(page))
    print('###################################################')
    
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.findAll('article')
    
    for article in articles:
        id = article['id'][5:]
        element = article.select_one('.entry-title > a')
        title = element['title'][:-7]
        link = element['href']
        datetime = article.select_one('.entry-date')['datetime']
        tags = [tag.text for tag in article.select('.tag-links > a') if tag.text not in ('Lista de fake news sobre o novo coronavírus (Covid-19)')]

        print(id)
        print(title)
        print(link)
        print(datetime)
        print(tags)
        print()
    
    time.sleep(5)
    page += 1
    url = "https://www.boatos.org/tag/coronavirus/page/{}".format(page)
    response = requests.get(url)
