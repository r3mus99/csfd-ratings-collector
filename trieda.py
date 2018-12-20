import requests
import csv
from bs4 import BeautifulSoup
from tkinter import *


def get_next_page_url(nextPage):
    return url_input.get() + "strana-" + str(nextPage) + "/"


def print_table(table, writer):
    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if (cols):
            nazov = cols[0].getText()
            hodnotenie = ''
            if cols[1].find("img") and cols[1].find("img").has_attr('alt'):
                hodnotenie = cols[1].find("img").attrs['alt']
            datum = cols[2].getText()
            if var.get() == 1:
                print(nazov + " [" + hodnotenie + "] " + datum)
            if var.get() == 2:
                writer.writerow([nazov, hodnotenie, datum])


def print_pages():
    url = url_input.get()
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    table = soup.find("table")
    actualPage = 1

    with open('output.csv', 'w', encoding='utf-16') as myfile:
        writer = csv.writer(myfile, delimiter='\t',
                            quoting=csv.QUOTE_NONE, quotechar='', lineterminator='\n')

        while table is not None:  # todo add not later
            print_table(table, writer)

            actualPage = actualPage + 1
            nextPageUrl = get_next_page_url(actualPage)
            nextPageRequest = requests.get(nextPageUrl)

            soup = BeautifulSoup(nextPageRequest.content, 'html.parser')
            table = soup.find("table")
            print("{0} - {1}".format(table is not None, nextPageUrl))
            statusVar.set(nextPageUrl)  # todo update at run


root = Tk()

url_label = Label(root, text="reviews url")
url_input = Entry(root, width="70")
url_input.insert(0, "https://www.csfd.cz/uzivatel/51520-r3musko/hodnoceni/")

url_label.grid(row=0)
url_input.grid(row=0, column=1)

var = IntVar()
r1 = Radiobutton(root, text="console", variable=var, value=1)
r1.grid(row=1)

r2 = Radiobutton(root, text="csv file", variable=var, value=2)
r2.grid(row=2)

statusVar = StringVar()
statusVar.set('Hello')
status = Label(root, textvariable=statusVar)
status.grid(row=1, column=1)

b = Button(root, text="run", command=print_pages)
b.grid(row=2, column=1)

root.mainloop()
