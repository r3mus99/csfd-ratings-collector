import time
import requests
import csv
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import ttk


def get_next_page_url(nextPage):
    return url_input.get() + "strana-" + str(nextPage) + "/"


# -- parsing table row --------------------------------------------------------
def get_rating(cols):
    if cols[1].find("img") and cols[1].find("img").has_attr('alt'):
        return cols[1].find("img").attrs['alt']
    else:
        return 'odpad!'


def get_link_on_csfd(cols):
    if cols[0].find("a") and cols[0].find("a").has_attr('href'):
        return 'https://www.csfd.cz' + cols[0].find("a").attrs['href']
    else:
        return ''


def get_link_on_imdb(csfd_url):
    csfd_page = requests.get(csfd_url)
    csfd_soup = BeautifulSoup(csfd_page.content, 'html.parser')

    share_div = csfd_soup.find("div", {"id": "share"})
    if share_div is None:
        return ''
    imdb_link = share_div.find("a", {"title": "profil na IMDb.com"})
    if imdb_link is None:
        return ''

    if imdb_link.attrs['href'] is None:
        return ''

    statusText.set(imdb_link.attrs['href'])


def transform_table_row(cols):
    title = cols[0].getText()
    rating = get_rating(cols)
    rating_date = cols[2].getText()
    link_on_csfd = get_link_on_csfd(cols)
    # todo
    # link_on_imdb = get_link_on_imdb(link_on_csfd)

    return [title, rating, rating_date, link_on_csfd]


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

            # update at run
            statusText.set(nextPageUrl)
            root.update_idletasks()
            progress['value'] = actualPage
        # update after run
        progress['value'] = 100


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

output_label = Label(main_frame, text="output")
output_label.grid(row=1)

radioButtonSelection = IntVar()
r1 = Radiobutton(main_frame, text="console",
                 variable=radioButtonSelection, value=1)
r1.grid(row=1, column=1, sticky="w")

r2 = Radiobutton(main_frame, text="csv file",
                 variable=radioButtonSelection, value=2)
r2.grid(row=2, column=1, sticky="w")

b = Button(main_frame, text="run", command=print_pages, width=60)
b.grid(row=3, column=1)

# bTest = Button(main_frame, text='test', command=get_link_on_imdb, width=60)
# bTest.grid(row=4, column=1)

# -- bottom frame content -----------------------------------------------------
statusText = StringVar()
statusText.set('Hello')
status = Label(bottom_frame, textvariable=statusText)
status.pack()

progress = ttk.Progressbar(bottom_frame, orient=HORIZONTAL,
                           length=500, mode='determinate')
progress.pack()
# progress.start()

root.mainloop()
