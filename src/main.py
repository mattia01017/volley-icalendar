import argparse
import requests
from src.volley import Tournament
from bs4 import BeautifulSoup
import asyncio


def get_options():
    parser = argparse.ArgumentParser(
        description="Create iCalendar file from URLs of FIPAV Bergamo tournaments")
    parser.add_argument('-o', '--output', metavar="FILE", default="calendar",
                        help="Name of the output file (\"calendar.ics\" by default)")
    parser.add_argument('-a', '--all', action='store_true',
                        help="Include every team of the specified tournaments in the output calendars")
    parser.add_argument("urls", metavar="URL", nargs="+",
                        help="URLs of tournaments")
    return parser.parse_args()


async def fetch_and_soup(url):
    res = requests.get(url).content
    return BeautifulSoup(res, "html.parser")


async def get_soups(urls):
    soups = await asyncio.wait(
        [fetch_and_soup(url) for url in urls]
    )
    return soups


def main():
    print("Loading...")
    opts = get_options()
    coros = asyncio.run(get_soups(opts.urls))
    soups = [c.result() for c in coros[0]]
    tournaments = [Tournament(s) for s in soups]
    