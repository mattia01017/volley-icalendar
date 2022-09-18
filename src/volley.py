from datetime import datetime, timedelta
import pytz
from parse import parse
from bs4 import BeautifulSoup
import icalendar


class Tournament:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        title = soup.find("span", "h3-wrap").string
        title = title.split("/", 1)
        self.title = title[0]
        round_soups = soup.find_all(class_="gare-wrap")
        self.rounds = [Round(r, self) for r in round_soups]
        self._teams = None

    def icalendar(self) -> icalendar.Calendar:
        calendar = icalendar.Calendar({
            'prodid': '-//My calendar product//mxm.dk//',
            'version': '2.0'
        })
        for r in self.rounds:
            for m in r.matches:
                calendar.add_component(m.icalendar_event())
        return calendar

    def get_teams(self) -> list[str]:
        self._teams = list(
            set(self.rounds[0].get_teams() + self.rounds[1].get_teams()))
        return self._teams

    def __str__(self) -> str:
        string = "TOURNAMENT\n"
        string += f"Title: {self.title}\n"
        string += f"Rounds:\n{self.rounds}\n"
        return string

    def __repr__(self) -> str:
        return self.__str__()

    def remove_other_teams(self, team_names: list) -> None:
        for r in self.rounds:
            r._remove_other_teams(team_names)
            


class Round:
    def __init__(self, round_soup: BeautifulSoup, tournament: Tournament):
        self.id = parse("g_{}", round_soup['id'])[0]
        match_soups = round_soup.find_all(class_="gara-big-wrap")
        self.matches = [Match(m, self) for m in match_soups]
        self.tournament = tournament
        self._teams = None

    def get_teams(self) -> list[str]:
        if self._teams is None:
            teams = [m.host_team for m in self.matches] + \
                [m.guest_team for m in self.matches]
            self._teams = list(set(teams))
        return self._teams

    def _remove_other_teams(self,team_names: list) -> None:
        self.matches = [m for m in self.matches if True in list(map(m.has_team, team_names))]

    def __str__(self) -> str:
        string = "ROUND\n"
        string += f"ID: {self.id}\n"
        string += f"Matches:\n{self.matches}\n"
        string += f"From the tournament: {self.tournament.title}\n"
        return string

    def __repr__(self) -> str:
        return self.__str__()


class Match:
    duration = timedelta(hours=1)

    def __init__(self, match_soup: BeautifulSoup, round: Round):
        strDate = match_soup.find(class_="info-gara-data").string
        dl = parse('{} {}/{}/{} {}.{}', strDate)
        self.date = datetime(int(dl[3]), int(
            dl[2]), int(dl[1]), int(dl[4]), int(dl[5]), 0, tzinfo=pytz.timezone('Europe/Rome'))
        self.num = match_soup.find(class_="info-gara-giornata").string
        self.address = match_soup.find(class_="info-gara-campo-desc").string + ", " + \
            match_soup.find(class_="info-gara-campo-loc").string
        teams = match_soup.find_all(class_="sq-nLong")
        self.host_team = teams[0].string
        self.guest_team = teams[1].string
        self.round = round

    def has_team(self, teamName) -> bool:
        return self.host_team == teamName or self.guest_team == teamName

    def is_old(self) -> bool:
        return self.date < datetime.now()

    def icalendar_event(self) -> icalendar.Event:
        event = icalendar.Event({
            'summary': self.host_team + " VS " + self.guest_team,
            'location': self.address,
            'description': self.round.tournament.title + ", " + self.num
        })
        event.add('dtstart', self.date)
        event.add('dtend', self.date + Match.duration)
        return event

    def __str__(self) -> str:
        string = "MATCH\n"
        string += f"Number: {self.num}\n"
        string += f"Host team: {self.host_team}\n"
        string += f"Guest team: {self.guest_team}\n"
        string += f"Date: {self.date}\nAddress: {self.address}\n"
        string += f"From round {self.round.id}\n"
        return string

    def __repr__(self) -> str:
        return self.__str__()
