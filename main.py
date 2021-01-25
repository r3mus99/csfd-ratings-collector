import csv
from tkinter import *
from tkinter.ttk import Progressbar
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import zlib


def url_to_soup(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urlopen(req)

    if res.info().get('Content-Encoding') == 'gzip':
        html = zlib.decompress(res.read(), 16+zlib.MAX_WBITS)
    else:
        html = res.read().decode("utf-8")

    return BeautifulSoup(html, "html.parser")


def get_next_page_url(next_page):
    return e_url.get() + "strana-" + str(next_page) + "/"


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
    csfd_soup = url_to_soup(csfd_url)

    share_div = csfd_soup.find("div", {"id": "share"})

    if share_div is None:
        return None

    imdb_link = share_div.find("a", {"title": "profil na IMDb.com"})

    if imdb_link is None:
        return None

    return imdb_link.attrs['href']


def cols_to_data(cols):
    title = cols[0].getText()
    rating = get_rating(cols)
    rating_date = cols[2].getText()
    csfd_url = get_link_on_csfd(cols)
    imdb_url = None
    if cb_read_imdb_val.get() == 1:
        imdb_url = get_link_on_imdb(csfd_url)

    return [title, rating, rating_date, csfd_url, imdb_url]


def print_table(table, writer):
    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if cols:
            data = cols_to_data(cols)
            if rb_value.get() == 1:
                print(data)
            elif rb_value.get() == 2:
                writer.writerow(data)


def print_first_row(table):
    rows = table.find_all("tr")
    row = rows[2]
    cols = row.find_all("td")
    if cols:
        data = cols_to_data(cols)
        print(data)


def print_pages():
    if rb_value.get() != 1 and rb_value.get() != 2:
        return

    soup = url_to_soup(e_url.get())

    table = soup.find("table")

    actual_page = 1

    with open('output.csv', 'w', encoding='utf-16') as myfile:
        writer = csv.writer(myfile, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='', lineterminator='\n')

        if cb_read_all_val.get() != 1:
            print_table(table, writer)
        else:
            while table is not None:
                print_table(table, writer)

                actual_page = actual_page + 1
                next_page_url = get_next_page_url(actual_page)

                soup = url_to_soup(next_page_url)
                table = soup.find("table")
                print("{0} - {1}".format(table is not None, next_page_url))

                root.update_idletasks()
                statusText.set(next_page_url)
                progress['value'] = actual_page
        progress['value'] = 100


root = Tk()
root["padx"] = 10
root["pady"] = 10

f_header = Frame(root)
f_input = Frame(root)
f_footer = Frame(root)

f_header.pack()
f_input.pack()
f_footer.pack()

# -- top frame content -------------------------------------------------------------------------------------------------
header = Label(f_header, text="CSFD.cz", fg="red", font=("Helvetica", 20, "bold italic"))
header.pack()

# -- main frame content -------------------------------------------------------
l_url = Label(f_input, text="url", padx=5)
l_url.grid(row=0, sticky='w')

e_url = Entry(f_input, w=60)
e_url.insert(0, "https://www.csfd.cz/uzivatel/51520-r3musko/hodnoceni/")
e_url.grid(row=0, column=1)

l_output = Label(f_input, text="výstup", padx=5)
l_output.grid(row=1, sticky='w')

rb_value = IntVar()
rb_console = Radiobutton(f_input, text="konzola", variable=rb_value, value=1)
rb_console.grid(row=1, column=1, sticky='w')
rb_console.select()

rb_csv = Radiobutton(f_input, text="csv", variable=rb_value, value=2)
rb_csv.grid(row=2, column=1, sticky=W)

l_settings = Label(f_input, text="nastavenia", padx=5)
l_settings.grid(row=3, sticky='w')

cb_read_imdb_val = IntVar()
cb_read_imdb = Checkbutton(f_input, text="čítať imdb adresy", variable=cb_read_imdb_val)
cb_read_imdb.grid(row=3, column=1, sticky=W)

cb_read_all_val = IntVar()
cb_read_all = Checkbutton(f_input, text="čítať všetky strany", variable=cb_read_all_val)
cb_read_all.grid(row=4, column=1, sticky=W)


b_load = Button(f_input, text="Načítaj", command=print_pages)
b_load.grid(row=5, column=1, sticky='we')

# -- bottom frame content -----------------------------------------------------
statusText = StringVar()
status = Label(f_footer, textvariable=statusText)
status.pack()

progress = Progressbar(f_footer, orient=HORIZONTAL, length=500, mode='determinate')
progress.pack()

root.mainloop()
