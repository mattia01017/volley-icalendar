import argparse
import requests
from src.volley import Tournament
from bs4 import BeautifulSoup
import asyncio


def get_options():
    parser = argparse.ArgumentParser(
        description="Create iCalendar file from URLs of FIPAV Bergamo tournaments")
    parser.add_argument('-o', '--output', metavar="FILE", default=["calendar.ics"], nargs="*",
                        help="Name the output files with the given values (\"calendar.ics\" by default). If option -s is present," +
                        " if you use this option you can specify all names or a name for all files")
    parser.add_argument('-a', '--all', action='store_true',
                        help="Include every team of the specified tournaments in the output calendars")
    parser.add_argument("urls", metavar="URL", nargs="+",
                        help="URLs of tournaments")
    parser.add_argument('-s', "--split", action="store_true",
                        help="Create a different file for each tournament")
    opts = parser.parse_args()

    if not opts.split and len(opts.output) != 1:
        parser.error("--split option not specified, not more than one output file must be specified\n" +
                     f"{len(opts.output)} name(s) given")
    elif opts.split and len(opts.output) != 1 and len(opts.output) != len(opts.urls):
        parser.error("--split option specified, you can specify only one name or the same number as the URLs.\n" +
                     f"{len(opts.output)} name(s) given, {len(opts.urls)} URL(s) given")
    return opts


async def fetch_and_soup(url) -> BeautifulSoup:
    res = requests.get(url).content
    return BeautifulSoup(res, "html.parser")


async def create_ical_file(tournament: Tournament, filename: str) -> None:
    with open(filename, 'wb') as f:
        out = tournament.icalendar().to_ical()
        f.write(out.replace("\\", ""))


async def main():
    opts = get_options()
    print("Loading...")
    coros = await asyncio.wait(
        [fetch_and_soup(url) for url in opts.urls]
    )
    soups = [c.result() for c in coros[0]]
    tournaments = [Tournament(s) for s in soups]

    if opts.all:
        print("Saving...")
        if len(opts.output) > 1:
            await asyncio.wait(
                [create_ical_file(tournaments[i], opts.output[i])
                 for i in range(0, len(tournaments))]
            )
        else:
            with open(opts.output[0], "ab") as f:
                for t in tournaments:
                    f.write(t.icalendar().to_ical())
    else:
        pass
    print("Done")
        
