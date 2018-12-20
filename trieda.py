import requests
import csv
from bs4 import BeautifulSoup
from tkinter import *


def get_next_page_url(nextPage):
    return url_input.get() + "strana-" + str(nextPage) + "/"


def transform_table_row(cols):
    nazov = cols[0].getText()
    hodnotenie = ''
    if cols[1].find("img") and cols[1].find("img").has_attr('alt'):
        hodnotenie = cols[1].find("img").attrs['alt']
    datum = cols[2].getText()
    return [nazov, hodnotenie, datum]


def print_table(table, writer):
    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if (cols):
            transformedRow = transform_table_row(cols)
            if radioButtonSelection.get() == 1:
                print(transformedRow)
            elif radioButtonSelection.get() == 2:
                writer.writerow(transformedRow)


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
            statusText.set(nextPageUrl)  # todo update at run


root = Tk()

top_frame = Frame(root)
main_frame = Frame(root)
bottom_frame = Frame(root)

top_frame.pack()
main_frame.pack()
bottom_frame.pack()

# -- top frame content --------------------------------------------------------
header = Label(top_frame, text="CSFD.cz", fg="red",
               font=("Helvetica", 44, "bold italic"))
header.pack()

# -- main frame content -------------------------------------------------------
url_label = Label(main_frame, text="reviews url")
url_input = Entry(main_frame, width=70)
url_input.insert(0, "https://www.csfd.cz/uzivatel/51520-r3musko/hodnoceni/")

url_label.grid(row=0)
url_input.grid(row=0, column=1)

radioButtonSelection = IntVar()
r1 = Radiobutton(main_frame, text="console",
                 variable=radioButtonSelection, value=1)
r1.grid(row=1)

r2 = Radiobutton(main_frame, text="csv file",
                 variable=radioButtonSelection, value=2)
r2.grid(row=2)

b = Button(main_frame, text="run", command=print_pages, width=60)
b.grid(row=2, column=1)

# -- bottom frame content -----------------------------------------------------
statusText = StringVar()
statusText.set('Hello')
status = Label(bottom_frame, textvariable=statusText)
status.grid(row=1, column=1)

root.mainloop()
