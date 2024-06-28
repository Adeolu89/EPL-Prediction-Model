# EPL-Prediction-Model

In this project, I combined my knowledge of web scraping and machine learning to create a model that predicts the outcomes of games in the English Premier League.

**Summary:**
- I first created a class called LeagueScraper to scrape the league table to obtain links for every team in the league.
- Next, I created a subclass called TeamScraper to scrape the scores and key statistics from each team's games across the season and stored these results in a Pandas DataFrame.
- I performed some data preprocessing and feature engineering to get rid of columns that I would not be using and transform features such as the team names into data that a machine learning model can use.
- Used a Random Forest Classifier to predict the outcomes of games: 1 meaning the team wins the game, 2 being the team draws or loses the game.


**Areas of Improvement:**
- As of right now, my model is not extremely accurate so I would like to make it more precise, though it is difficult because football is unpredictable, especially the EPL.
- I would very much like to perform some data analysis to be able to classify a team based on their style of play, e.g. 'Possession', 'Counter-Attacking', 'High-Press', etc, and see what type of styles of play perform the best against other styles of play.
- I want to make the predictions more specific, where drawing a game and losing a game are different values
- Adding visualizations to make my insights more readable.


