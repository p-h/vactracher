import os
import toml
from collections import namedtuple
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import tweepy

DEFAULT_STATE_FILE = "/tmp/vacstate.txt"

Infos = namedtuple("Infos", "delivered administered fully_vaccinated")
Info = namedtuple("Info", "n date source")


def extract_description_info(description):
    d = dict(
        [tuple([x.strip() for x in kv.split(":")]) for kv in description.split("–")]
    )

    date = datetime.strptime(d["Status"], "%d.%m.%Y, %H.%Mh")

    return date, d["Source"]


def extract_info(soup, string):
    header = soup.find(string=string)
    table_head = header.parent.parent

    description = table_head.find_next_sibling().text
    date, source = extract_description_info(description)

    row = table_head.parent
    n = int(row.find_next_sibling().text.replace(" ", ""))

    return Info(n, date, source)


def retrieve_info():
    r = requests.get("https://www.covid19.admin.ch/en/overview")

    s = BeautifulSoup(r.text, features="html.parser")

    delivered = extract_info(s, "Vaccine doses delivered to cantons and FL")
    administered = extract_info(s, "Administered vaccine doses")
    fully_vaccinated = extract_info(s, "Fully vaccinated people")

    return Infos(delivered, administered, fully_vaccinated)


class App:
    def __init__(
        self, state_file, api_key, api_secret, access_token, access_token_secret
    ):
        self.state_file = state_file
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

    def read_date_last_tweet(self):
        try:
            with open(self.state_file) as f:
                s = f.read().strip() or 0
                return datetime.fromtimestamp(int(s))

        except IOError:
            return datetime.fromtimestamp(0)

    def send_tweet(self, infos):
        auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth)
        api.update_status(
            f"Delivered vaccines: {infos.delivered.n}\n"
            f"Administered doses: {infos.administered.n}\n"
            f"Fully vaccinated people: {infos.fully_vaccinated.n}"
        )


def main():
    d = toml.load("secrets.toml")

    state_file = os.environ.get("STATE_FILE", DEFAULT_STATE_FILE)

    api_key = d["api_key"]
    api_secret = d["api_secret"]
    access_token = d["access_token"]
    access_token_secret = d["access_token_secret"]
    app = App(state_file, api_key, api_secret, access_token, access_token_secret)

    date_last_tweet = app.read_date_last_tweet()

    infos = retrieve_info()
    data_date = max(
        max(infos.delivered.date, infos.administered.date), infos.fully_vaccinated.date
    )

    if date_last_tweet < data_date:
        app.send_tweet(infos)

        with open(state_file, "w") as f:
            st = 1 + data_date.timestamp()  # avoid rounding errors
            f.write(f"{st:0.0f}")


if __name__ == "__main__":
    main()
