# packages
import time
import requests
from bs4 import BeautifulSoup


# scraping
page = 1
url = "https://www.boatos.org/tag/coronavirus/page/{}".format(page)
response = requests.get(url)

while response.status_code == 200:
    print(url)
    print('page {} exists'.format(page))
    time.sleep(5)
    page += 1
    url = "https://www.boatos.org/tag/coronavirus/page/{}".format(page)
    response = requests.get(url)

