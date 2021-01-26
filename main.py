import csv
import zlib
import webbrowser
from tkinter import *
from tkinter.ttk import Progressbar, Treeview, Scrollbar
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


# region functions
def url_to_soup(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urlopen(req)

    if res.info().get('Content-Encoding') == 'gzip':
        html = zlib.decompress(res.read(), 16 + zlib.MAX_WBITS)
    else:
        html = res.read().decode("utf-8")

    return BeautifulSoup(html, "html.parser")


def get_next_page_url(next_page):
    return e_url.get() + "strana-" + str(next_page) + "/"


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
    date = cols[2].getText()
    csfd_url = get_link_on_csfd(cols)
    imdb_url = None
    if cb_read_imdb_val.get() == 1:
        imdb_url = get_link_on_imdb(csfd_url)

    return [date, rating, title, csfd_url, imdb_url]


def update_status(actual, total):
    pct = 100 * float(actual) / float(total)
    text = str(actual) + ' / ' + str(total)

    statusText.set(text)
    progress['value'] = pct
    root.update_idletasks()


def print_table(table, writer, all_pages=False):
    rows = table.find_all("tr")
    index = 0
    for row in rows:
        if not all_pages:
            update_status(index, 100)
            index += 1
        cols = row.find_all("td")
        if cols:
            data = cols_to_data(cols)
            if rb_value.get() == 1:
                parent = tree.insert(parent='', index='end', text=data[0], values=(data[1], data[2]))
                child = tree.insert(parent=parent, index='end', text='', values=('', data[3]))
                # todo style
                if cb_read_imdb_val.get() == 1:
                    tree.insert(parent=parent, index='end', text='', values=('', data[4]))
            elif rb_value.get() == 2:
                writer.writerow(data)


def print_first_row(table):
    rows = table.find_all("tr")
    row = rows[2]
    cols = row.find_all("td")
    if cols:
        data = cols_to_data(cols)
        print(data)


def try_parse_int(value):
    try:
        return int(value), True
    except ValueError:
        return value, False


def get_max_page(soup):
    max_page: int = 1
    paginator = soup.find("div", {"class": "paginator"})
    pages = paginator.find_all("a")

    for page in pages:
        val, success = try_parse_int(page.contents[0])
        if success and val > max_page:
            max_page = val

    return max_page


def print_pages():
    if rb_value.get() != 1 and rb_value.get() != 2:
        return

    soup = url_to_soup(e_url.get())

    table = soup.find("table")

    actual_page = 1
    total_pages = get_max_page(soup)

    with open('output.csv', 'w', encoding='utf-16') as myfile:
        writer = csv.writer(myfile, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='', lineterminator='\n')

        if cb_read_all_val.get() != 1:
            print_table(table, writer)
        else:
            while table is not None:
                print_table(table, writer, True)

                actual_page = actual_page + 1
                next_page_url = get_next_page_url(actual_page)

                soup = url_to_soup(next_page_url)
                table = soup.find("table")
                # print("{0} - {1}".format(table is not None, next_page_url))
                if table is None:
                    update_status(total_pages, total_pages)
                else:
                    update_status(actual_page, total_pages)
        progress['value'] = 100


def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def link_tree(self):
    input_id = tree.selection()
    input_item = tree.item(input_id, "values")[1]
    if is_valid_url(input_item):
        webbrowser.open('{}'.format(input_item))
# endregion functions


root = Tk()
root.title('CSFD.cz / IMDB.com / Trakt.tv')
root.minsize(400, 400)
root["padx"] = 10
root["pady"] = 10

f_header = Frame(root)
f_input = Frame(root)
f_content = Frame(root)
f_footer = Frame(root)

f_header.pack(anchor=W)
f_input.pack(fill=X)
f_input.columnconfigure(0, minsize=75)
f_input.columnconfigure(1, weight=1, minsize=100)
f_content.pack(fill=BOTH, expand=True)
f_footer.pack(fill=X)

# region header
header = Label(f_header, text="CSFD.cz", fg="red", font=("Helvetica", 20, "bold italic"))
header.pack(side=LEFT)
# endregion header
# region input
l_url = Label(f_input, text="url")
l_url.grid(row=0, padx=5, sticky='w')

e_url = Entry(f_input)
e_url.insert(0, "https://www.csfd.cz/uzivatel/1-pomo/hodnoceni/")
e_url.grid(row=0, column=1, sticky='we')

l_output = Label(f_input, text="výstup")
l_output.grid(row=1, padx=5, sticky='w')

rb_value = IntVar()
rb_console = Radiobutton(f_input, text="obrazovka", variable=rb_value, value=1)
rb_console.grid(row=1, column=1, sticky='w')
rb_console.select()

rb_csv = Radiobutton(f_input, text="csv", variable=rb_value, value=2)
rb_csv.grid(row=2, column=1, sticky='w')

l_settings = Label(f_input, text="nastavenia")
l_settings.grid(row=3, padx=5, sticky='w')

cb_read_imdb_val = IntVar()
cb_read_imdb = Checkbutton(f_input, text="čítať imdb adresy (náročná operácia)", variable=cb_read_imdb_val)
cb_read_imdb.grid(row=3, column=1, sticky='w')

cb_read_all_val = IntVar()
cb_read_all = Checkbutton(f_input, text="čítať všetky strany (náročná operácia)", variable=cb_read_all_val)
cb_read_all.grid(row=4, column=1, sticky='w')

b_load = Button(f_input, text="Načítaj", command=print_pages)
b_load.grid(row=5, columnspan=2, pady=5, sticky=W + E)
# endregion input
# region content
tree = Treeview(f_content, selectmode='browse')
tree["columns"] = ("#1", "#2")
tree.column("#0", width=80, stretch=NO)
tree.column("#1", width=80, stretch=NO, anchor=CENTER)
tree.column("#2", width=400)
tree.heading("#0", text="Dátum")
tree.heading("#1", text="Hodnotenie")
tree.heading("#2", text="Film")
sb_vertical = Scrollbar(f_content, orient="vertical", command=tree.yview)
sb_vertical.pack(side=RIGHT, fill=Y)
tree.bind("<Double-1>", link_tree)
tree.configure(yscrollcommand=sb_vertical.set)
tree.pack(fill=BOTH, expand=True)
# endregion content
# region footer
statusText = StringVar()
status = Label(f_footer, textvariable=statusText)
status.pack()

progress = Progressbar(f_footer, orient=HORIZONTAL, mode='determinate')
progress.pack(fill=BOTH)
# endregion footer

root.mainloop()
