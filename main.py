import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

DEFAULT_STATE_FILE = '/tmp/vacstate.txt'


class Info:
    def __init__(self, n, date, source):
        self.n = n
        self.date = date
        self.source = source


def extract_description_info(description):
    d = dict([
        tuple([x.strip() for x in kv.split(':')])
        for kv in description.split('–')
    ])

    date = datetime.strptime(d['Status'], '%d.%m.%Y, %H.%Mh')

    return date, d['Source']


def extract_info(soup, string):
    header = soup.find(string=string)
    table_head = header.parent.parent

    description = table_head.find_next_sibling().text
    date, source = extract_description_info(description)

    row = table_head.parent
    n = int(row.find_next_sibling().text.replace(' ', ''))

    return Info(n, date, source)


def retrieve_info():
    r = requests.get('https://www.covid19.admin.ch/en/overview')

    s = BeautifulSoup(r.text, features='html.parser')

    delivered = extract_info(s, 'Vaccine doses delivered to the cantons and FL')
    administered = extract_info(s, 'Vaccine doses administered')

    return delivered, administered


class App():
    def __init__(self, state_file):
        self.state_file = state_file

    def read_date_last_tweet(self):
        try:
            with open(self.state_file) as f:
                s = f.read().strip() or 0
                return datetime.fromtimestamp(int(s))

        except IOError:
            return datetime.fromtimestamp(0)


if __name__ == '__main__':
    state_file = os.environ.get('STATE_FILE',  DEFAULT_STATE_FILE)
    app = App(state_file)

    date_last_tweet = app.read_date_last_tweet()

    delivered, administered = retrieve_info()
    data_date = max(delivered.date, administered.date)

    if date_last_tweet < data_date:
        with open(state_file, 'w') as f:
            st = 1 + data_date.timestamp()  # avoid rounding errors
            f.write(f'{st:0.0f}')
