from bs4 import BeautifulSoup
import pandas as pd
import requests
import lxml
import time

class LeagueScraper:
    
    """
    A class to scrape team URLs from a league's webpage on FBref.com.

    Attributes:
        base_url (str): The base URL of the league's webpage.
        league_data (requests.models.Response): The response object containing HTML content of the league's webpage.
    """
    
    def __init__(self, base_url: str) -> None:
        """
        Initializes the LeagueScraper object.

        Args:
            base_url (str): The base URL of the league's webpage.
        """
        self.base_url = base_url
        self.league_data = requests.get(base_url)
        
    def team_urls(self):
        
        """
        Extracts URLs of individual teams from the league's webpage.

        Returns:
            list: A list of URLs of individual teams.
        """
        
        data = self.league_data
        soup = BeautifulSoup(data.content, "html.parser")
        standings_table = soup.select('table.stats_table')[0] # selects the first element in a list of elements with the table.stats_table tag
        links = standings_table.find_all('a') # finds all the links
        squad_links = [link.get("href") for link in links if "/squads/" in link.get("href")] # get the particular squad links
        squad_urls = [f"https://fbref.com{link}" for link in squad_links]
        
        return squad_urls
    
class TeamScraper(LeagueScraper):
    
    """
    A class to scrape various statistics of a football team from its webpage on FBref.com.

    Attributes:
        team_url (str): The URL of the team's webpage.
        _team_data (requests.models.Response): The response object containing HTML content of the team's webpage.
    """
    
    def __init__(self, team_url) -> None:
        
        """
        Initializes the TeamScraper object.

        Args:
            team_url (str): The URL of the team's webpage.
        """
        
        self._team_data = requests.get(team_url)
        self.team_url = team_url
        
    def team_scores_and_fixtures(self):
        
        """
        Scrapes scores and fixtures data for the team.

        Returns:
            pandas.DataFrame: DataFrame containing scores and fixtures data.
        """
        
        data = self._team_data
        games = pd.read_html(data.content, match="Scores & Fixtures", flavor="lxml")
        games = games[0]
        games = games[games["Comp"].isin(["Premier League", "La Liga", "Bundesliga", "Ligue 1", "Serie A"])]
        return games
    
    def team_shooting_stats(self):
        
        """
        Scrapes shooting data for the team.

        Returns:
            pandas.DataFrame: DataFrame containing shooting data.
        """
        
        data = self._team_data
        soup = BeautifulSoup(data.content, "html.parser")
        links = soup.find_all('a')
        links = [l.get("href") for l in links]
        links = [l for l in links if l and "all_comps/shooting" in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        shooting = pd.read_html(data.text, match="Shooting")[0]
        shooting.columns = shooting.columns.droplevel() 
        shooting = shooting[shooting["Comp"].isin(["Premier League", "La Liga", "Bundesliga", "Ligue 1", "Serie A"])]

        return shooting
    
    def team_possession_stats(self):
    
        """ Scrapes possession data for the team.

        Returns:
            pandas.DataFrame: DataFrame containing possession data.
        """
        
        data = self._team_data
        soup = BeautifulSoup(data.text, 'html')
        links = soup.find_all('a')
        links = [l.get("href") for l in links]
        links = [l for l in links if l and "all_comps/possession" in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        possession = pd.read_html(data.text, match="Possession")[0]
        possession.columns = possession.columns.droplevel()
        possession = possession[possession["Comp"].isin(["Premier League", "La Liga", "Bundesliga", "Ligue 1", "Serie A"])]

        return possession
    
    def games_not_played(self):
        
        """
        Returns:
            pandas.DataFrame: DataFrame containing games the team has not yet played.
        """
        games = self.team_scores_and_fixtures()
        games = games[games["Result"].isna() == True]
        return games
        
    
    def team_complete_stats(self):
        
        """
        Scrapes scores and fixtures data, possession data abnd shooting data for the team.

        Returns:
            pandas.DataFrame: DataFrame containing the complete statistics on the team
        """
        
        scores = self.team_scores_and_fixtures()
        shooting = self.team_shooting_stats()
        possession = self.team_possession_stats()
        shooting_subset = shooting[["Date", "Sh", "SoT", "Dist", "PK", "PKatt"]]
        team_data = scores.merge(shooting_subset, on="Date")
        possession_subset = possession[["Date", "Touches", "Def Pen", "Def 3rd", "Mid 3rd", "Att 3rd", "Att Pen", "Att", "Succ%", "1/3", "CPA"]]
        team_data = team_data.merge(possession_subset ,on="Date", how="right")
        team_data["Club"] = self.team_url.split("/")[-1].replace("-Stats", "")
        club_column = team_data.pop('Club')
        team_data.insert(0, 'Club', club_column)
        return team_data 
        
        
premierleague = "https://fbref.com/en/comps/9/Premier-League-Stats"
"""str: The URL of the Premier League's webpage on FBref.com."""

EPL = LeagueScraper(premierleague)
"""LeagueScraper: An instance of the LeagueScraper class initialized with the URL of the Premier League's webpage."""

EPL_urls = EPL.team_urls()
"""list: A list of URLs of individual teams participating in the Premier League, scraped using the LeagueScraper object."""

all_games_epl = []
"""list: An empty list to store the complete statistics DataFrame for each team in the Premier League."""

for eplteam in EPL_urls:
    team_names = eplteam.split("/")[-1].replace("-Stats", "")
    scrapedeplteam = TeamScraper(eplteam)
    completestats = scrapedeplteam.team_complete_stats()
    all_games_epl.append(completestats)
    time.sleep(20)
    
epl_df = pd.concat(all_games_epl)
"""pandas.DataFrame: Concatenates all the complete statistics DataFrames of teams into a single DataFrame."""

epl_df.reset_index(drop=True, inplace=True)
"""Resets the index of the DataFrame and modifies it in place."""

epl_df.head()
"""pandas.DataFrame: The final DataFrame containing complete statistics of all teams in the Premier League."""

epl_df.to_csv("epl.csv")