import requests
import csv
from bs4 import BeautifulSoup
from tkinter import *

root = Tk()

topFrame = Frame(root)
topFrame.pack()

bottomFrame = Frame(root)
bottomFrame.pack(side=BOTTOM)

button1 = Button(topFrame, text='hahaha', fg='red')
button2 = Button(topFrame, text='hehehe', fg='red')
button3 = Button(topFrame, text='huhuhu', fg='red')
button4 = Button(bottomFrame, text='hihihi', fg='blue')

button1.pack(side=LEFT)
button2.pack(side=LEFT)
button3.pack(side=LEFT)
button4.pack()

root.mainloop()

def get_next_page_url(nextPage):
    return url + "strana-" + str(nextPage) + "/"  # "https://www.csfd.cz/uzivatel/55555-marecko/hodnoceni/strana-2/"

def print_table(table):
    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if (cols):
            nazov = cols[0].getText()
            hodnotenie = ''
            if cols[1].find("img") and cols[1].find("img").has_attr('alt'):
                hodnotenie = cols[1].find("img").attrs['alt']
            datum = cols[2].getText()
            # print(nazov + " [" + hodnotenie + "] " + datum)
            writer.writerow([nazov, hodnotenie, datum])

# print pages
url = "https://www.csfd.cz/uzivatel/51520-r3musko/hodnoceni/"
soup = BeautifulSoup(requests.get(url).content, 'html.parser')

table = soup.find("table")
actualPage = 1

with open('output.csv', 'w', encoding='utf-16') as myfile:
    writer = csv.writer(myfile, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='', lineterminator='\n')

    while table is None: # todo add not later
        print_table(table)

        actualPage = actualPage + 1
        nextPageUrl = get_next_page_url(actualPage)
        nextPageRequest = requests.get(nextPageUrl)

        soup = BeautifulSoup(nextPageRequest.content, 'html.parser')
        table = soup.find("table")
        print("{0} - {1}".format(table is not None, nextPageUrl))