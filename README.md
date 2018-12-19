# ML MIX LAB

Spend less time searching for music and more time creating with [mlmixlab.com](http://mlmixlab.com/).

## tl;dr
Creating great mixes is an art, and musicians have been using sampling to improve their songs for years. Finding songs that mix well together can be difficult and time consuming, and can yield unsatisfying results. Using one seed song, DJ's can use ML Mix Lab to find a list of songs that they can use together in a mix. I have used collaborative filtering to determine what makes songs mix well together, according to a database of production level mixing and sampling. Technologies used include Python, PostgreSQL, PySpark, Selenium, AWS, Psycopg2, Brython, HTML, and Flask.

## File Structure Summary
Directory | Description
------------ | -------------
data | sample of database
mixlab | Python classes and scripts & website dir
notebooks | jupyter notebooks used for eda and class testing
bin | postgres schema

## Business Understanding
Creating great mixes is a DJ's job. Searching for music takes time, and understanding the intricacies of successful mixing takes years of experience.

The idea and structure of this project can be expanded to using audio files, finding songs that can be mixed into or sampled in songs that are still in the ideation and production process.

## Data Understanding and Preparation
### Data Collection Process:
1. Start at at the main page for a particular genre, such as [Soul / Funk / Disco](https://www.whosampled.com/genre/Soul-Funk-Disco/).
2. Collect most influential and most popular artists in the genre. 
3. Scrape each artist individually, based on the number of songs in the database.
4. Add all artists that are connected to each song to the database. 
5. Continue scraping, prioritizing based on artists' song frequency.
*(see scrape.py for scraping function, using classes found in scraper.py and database_interaction.py)*

### Conceptualization:
Equating song sampling to creative mixing allows us to use this dataset to train a model to recommend songs to mix together. We can think of each song as a 'user' and 'item' in a recommendation system, with each song being a 'user' when it samples another 'item' song.


## Modeling

Create an implicit recommendation system, using each song in the dataset as both a user and item, assigning a `1` to connected songs and `0` to all others. 

We can weight the implicit ratings based on feature matching, such as weighting a connection if two songs have a bpm within `+/- 4`.

Below is a user-item matrix for three songs where `Song 1` and `Song 3` are connected. `Song 1` and `Song 4` are both connected and have the same bpm.

| Song ID     | Song 1  | Song 2  | Song 3  | Song 4  |
| ------------|:-------:|:-------:|:-------:|:-------:|
| Song 1      | 1       | 0       | 1       | 2       |
| Song 2      | 0       | 1       | 0       | 0       |
| Song 3      | 1       | 0       | 1       | 0       |
| Song 4      | 2       | 0       | 0       | 1       |

## Evaluation

Baseline models have been compared using root mean squared error to start tuning hyperparameters such as matrix rank. Further tuning and evaluation can be done comparing professional DJ's rankings versus the model using a hypothesis test such as the [Wilcoxon signed-rank test](https://en.wikipedia.org/wiki/Wilcoxon_signed-rank_test).






 



