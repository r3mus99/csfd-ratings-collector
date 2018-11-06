import requests
from bs4 import BeautifulSoup

url = "https://www.csfd.cz/uzivatel/51520-r3musko/hodnoceni/"
soup = BeautifulSoup(requests.get(url).content, 'html.parser')

table = soup.find("table")
rows = table.find_all("tr")

for row in rows:
    cols = row.find_all("td")
    if (cols):
        nazov = cols[0].getText()
        if cols[1].find("img") and cols[1].find("img").has_attr('alt'):
            hodnotenie = cols[1].find("img").attrs['alt']
        datum = cols[2].getText()
        print(nazov + " [" + hodnotenie + "] " + datum)


def get_next_page_url(nextPage):
    return url + "strana-" + str(nextPage) + "/"  # "https://www.csfd.cz/uzivatel/55555-marecko/hodnoceni/strana-2/"


# check other sites
actualPage = 1
while table is not None:
    actualPage = actualPage + 1
    nextPageUrl = get_next_page_url(actualPage)
    nextPageRequest = requests.get(nextPageUrl)

    soup = BeautifulSoup(nextPageRequest.content, 'html.parser')
    table = soup.find("table")

    print("{0} - {1}".format(table is not None, nextPageUrl))
