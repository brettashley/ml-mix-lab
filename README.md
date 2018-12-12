# ML MIX LAB

#### Spend less time searching for music and more time creating. 

## tl;dr
Creating great mixes is an art, and musicians have been using sampling to improve their songs for years. Finding songs that mix well together can be difficult and time consuming, and can yield unsatisfying results. Using one seed song, DJ's can use ML Mix Lab to find a list of songs that they can use together in a mix. I have used collaborative filtering to determine what makes songs mix well together, according to a database of production level mixing and sampling. Technologies used include Python, PostgreSQL, PySpark, Selenium, AWS, and Psycopg2.

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
#### Data Collection Process:
1. Start at at the main page for a particular genre, such as [Soul / Funk / Disco](https://www.whosampled.com/genre/Soul-Funk-Disco/).
2. Collect most influential and most popular artists in the genre. 
3. Scrape each artist individually, based on the number of songs in the database.
4. Add all artists that are connected to each song to the database. 
5. Continue scraping, prioritizing based on artists' song frequency.

#### Conceptulization:
Create an implicit recommendation system, using each song in the dataset as both a user and item, assigning a `1` to connected songs and `0` to all others. 








