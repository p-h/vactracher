import os
import sys
from collections import namedtuple
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import tweepy

DEFAULT_STATE_FILE = "/tmp/vacstate.txt"

Infos = namedtuple("Infos", "delivered administered fully_vaccinated data_date")
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

    data_date = max(max(delivered.date, administered.date), fully_vaccinated.date)

    return Infos(delivered, administered, fully_vaccinated, data_date)


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
            f"Vaccine status update as of {infos.data_date:%Y-%m-%d %H:%M}:\n"
            f"Delivered vaccines: {infos.delivered.n}\n"
            f"Administered doses: {infos.administered.n}\n"
            f"Fully vaccinated people: {infos.fully_vaccinated.n}"
        )


def main():
    state_file = os.environ.get("STATE_FILE", DEFAULT_STATE_FILE)
    api_key = os.environ.get("API_KEY") or sys.exit("API_KEY not set")
    api_secret = os.environ.get("API_SECRET") or sys.exit("API_SECRET not set")
    access_token = os.environ.get("ACCESS_TOKEN") or sys.exit("ACCESS_TOKEN not set")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET") or sys.exit(
        "ACCESS_TOKEN_SECRET not set"
    )
    app = App(state_file, api_key, api_secret, access_token, access_token_secret)

    date_last_tweet = app.read_date_last_tweet()

    infos = retrieve_info()

    if date_last_tweet < infos.data_date:
        app.send_tweet(infos)

        with open(state_file, "w") as f:
            st = 1 + infos.data_date.timestamp()  # avoid rounding errors
            f.write(f"{st:0.0f}")


if __name__ == "__main__":
    main()
