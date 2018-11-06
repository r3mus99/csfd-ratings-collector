import requests
from bs4 import BeautifulSoup

page = requests.get("https://www.csfd.cz/uzivatel/51520-r3musko/hodnoceni/")
soup = BeautifulSoup(page.content, 'html.parser')

table = soup.find("table")
rows = table.find_all("tr")

for row in rows:
    cols = row.find_all("td")
    if(cols):
        nazov = cols[0].getText()
        if cols[1].find("img") and cols[1].find("img").has_attr('alt'):
            hodnotenie = cols[1].find("img").attrs['alt']
        datum = cols[2].getText()
        print(nazov + " [" + hodnotenie + "] " + datum)