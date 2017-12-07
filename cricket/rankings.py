import urllib2
import grequests
from bs4 import BeautifulSoup
from collections import OrderedDict


class IccRankingsParser:
    def __init__(self, rankings_url):
        self.url = rankings_url

    def team_standings(self):
        standings_page = urllib2.urlopen(self.url)
        standings = BeautifulSoup(standings_page, 'html.parser')
        container = standings.find('div', attrs={'class': 'ciPhotoContainer'})
        championships = [championship.text for championship in container.findAll('h3')]
        tables = container.findAll('table', attrs={'class': 'StoryengineTable'})
        standings_data = []
        for table in tables:
            table_data = []
            rows = table.findAll('tr')
            for row in rows:
                headers = row.findAll('th')
                table_data.append([header.text for header in headers if header])
                cols = [data.text for data in row.findAll('td')]
                table_data.append([data for data in cols if data])
            standings_data.append(table_data)
        return OrderedDict(zip(championships, standings_data))

    def player_rankings(self):
        rankings_page = urllib2.urlopen(self.url)
        rankings = BeautifulSoup(rankings_page, 'html.parser')
        container = rankings.find('div', attrs={'class': 'ciPhotoContainer'})
        categories = [category.text for category in container.findAll('h3')]
        iframes = container.findAll('iframe')
        ranking_sources = (grequests.get(url) for url in [iframe.attrs['src'] for iframe in iframes])
        ranking_data = []
        for ranking_source in grequests.map(ranking_sources):
            table = BeautifulSoup(ranking_source.content, 'html.parser').find('table', attrs={'class': 'ratingstable'})
            table_data = [['Rank', 'Name', 'Country', 'Rating']]
            rows = table.findAll('tr')
            for row in rows:
                cols = [data.text for data in row.findAll('td')]
                table_data.append([data for data in cols if data])
            ranking_data.append(table_data)
        return OrderedDict(zip(categories, ranking_data))
