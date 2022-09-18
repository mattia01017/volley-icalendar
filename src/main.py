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
    elif opts.split and len(opts.urls) == 1:
        parser.error("--split option can't be used with just 1 URL given")
    return opts


async def fetch_and_soup(url) -> BeautifulSoup:
    res = requests.get(url).content
    return BeautifulSoup(res, "html.parser")


async def create_ical_file(tournament: Tournament, filename: str) -> None:
    with open(filename, 'wb') as f:
        out = tournament.icalendar().to_ical()
        f.write(out)


async def main():
    opts = get_options()
    print("Loading resources...")
    coros = await asyncio.wait(
        [fetch_and_soup(url) for url in opts.urls]
    )
    print("Parsing matches...")
    soups = [c.result() for c in coros[0]]
    tournaments = [Tournament(s) for s in soups]
    
    if not opts.all:
        for tournament in tournaments:
            print(f"Title: {tournament.title}")
            index = 1
            teams = tournament.get_teams()
            for t in teams:
                print(f"{index}.\t{t}")
                index += 1
            fav_teams_index = input(
                "select teams to add to calendar: ").split()
            to_keep = [teams[i]
                       for i in range(0, index-1) 
                       if str(i+1) in fav_teams_index]
            tournament.remove_other_teams(to_keep)
            print()

    print("Saving calendars...")
    filenames = opts.output
    if opts.split:
        if len(filenames) == 1:
            filenames = [f"{t.title}_{filenames[0]}" for t in tournaments]
        await asyncio.wait(
            [create_ical_file(tournaments[i], filenames[i])
                for i in range(0, len(tournaments))]
        )
    else:
        with open(filenames[0], 'w') as f:
            f.flush()
        with open(filenames[0], "ab") as f:
            for tournament in tournaments:
                f.write(tournament.icalendar().to_ical())
    print("Done")
