# Cinemas Webscrapper

## Table of Contents
* [What is it?](#what-is-it)
  - [Features](#features)
* [Usage](#usage)
  - [Development setup](#development-setup)
  - [Deployment](#deployment)
* [Architecture](#architecture)
  - [Database ER diagram](#database-er-diagram)
  - [API](#api)

## What is it?
Cinemas webscrapper is scrapper developed with the aim of retrieving information related
to cinemas, movies and sessions regarding Cinemas NOS. It integrates a chat bot developed
with the aim of improving the customer assistance provided by ISPs, NOS in this case, by
aggregating most of their customer services in a single endpoint.

### Features
The API provided by this service allows:
* Retrieve list of sessions based on current date and location
* Retrieve next movies based on location
* Get movie suggestions based on duration
* Search for movies based on:
    * Genre
    * Producer
    * Cast
    * Synopsis
    * Age restriction
* Retrieve of upcoming releases
* Retrieve movie details
* Retrieve next sessions based on movie, date, location


## Usage
#### Development Setup
* Install *Django* dependencies:
`pip install -r requirements.txt --user`
* Install *Docker*
* Pull *Redis* container:
`docker pull redis`
* Import static data:
`./manage.py loaddata static/cinemas_fixture.json`
`./manage.py loaddata --database=default_2 static/cinemas_fixture.json`
* Run *Django* project:
`./manage.py runserver`
* Run *Redis* back-end
`docker run -p 6379:6379 redis`
* Run *Celery* (for periodic database update):
`celery -A cinemas_scrapper.celery worker -B -l INFO`

### Deployment
(instructions go here)


## Architecture
### Database ER diagram
![Database model](static/doc/Cinemas_NOS_DB_EN.png)

### API

* Search for movies in cinema

```http
GET /movies/by_cinema?search_term=<>&lat=<>&lon=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional***. Cinema query. |
| `lat` and `lon` | `float` | **Optional***. User location. |

------
<!---------------------------------------------------->

* Search for movies based on genre, producer, cast, synopsis and age restriction

```http
GET /movies/search?genre=<>&cast=<>&producer=<>&synopsis=<>&age=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `genre` | `string` | **Optional**. Movie genre. |
| `cast` | `string` | **Optional**. Actors names, comma separated. |
| `producer` | `string` | **Optional**. Producer name. |
| `synopsis` | `string` | **Optional**. Words to search on the movie synopsis, comma separated. |
| `age` | `int` | **Optional** Maximum age restriction. |

**Note**: All parameters are optional but at least one of them needs to be provided.

------
<!---------------------------------------------------->

* Search for upcoming movies

```http
GET /movies/releases
```

------
<!---------------------------------------------------->

* Get details of movie

```http
GET /movies/details?movie=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `movie` | `string` | **Required**. Name of the movie. |

------
<!---------------------------------------------------->

* Search for sessions of movies under a certain duration

```http
GET /sessions/by_duration?search_term=<>&lat=<>&lon=<>&duration=<>&date=<>&time=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional***. Cinema query. |
| `lat` and `lon` | `float` | **Optional***. User location. |
| `duration` | `int` | **Required**. Maximum value of duration (in minutes). |
| `date` | `Year-Month-Day` | **Optional**. Date. |
| `time` | `Hours:Minutes:Seconds` | **Optional** Time. |

------
<!---------------------------------------------------->

* Search for the next sessions

```http
GET /sessions/next_sessions?search_term=<>&lat=<>&lon=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional***. Cinema query. |
| `lat` and `lon` | `float` | **Optional***. User location. |

------
<!---------------------------------------------------->

* Search sessions for a given movie

```http
GET /sessions/by_movie?search_term=<>&lat=<>&lon=<>&movie=<>&date=<>&time=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional***. Cinema query. |
| `lat` and `lon` | `float` | **Optional***. User location. |
| `movie` | `string` | **Required**. Name of the movie. |
| `date` | `Year-Month-Day` | **Optional**. Date. |
| `time` | `Hours:Minutes:Seconds` | **Optional** Time. |

------
<!---------------------------------------------------->

* Search for sessions by date

```http
GET /sessions/by_date?search_term=<>&lat=<>&lon=<>&date=<>&time=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional***. Cinema query. |
| `lat` and `lon` | `float` | **Optional***. User location. |
| `date` | `Year-Month-Day` | **Optional**. Date. |
| `time` | `Hours:Minutes:Seconds` | **Optional**. Time. |

------
***Note**: The methods related to sessions require `search_term` or in alternative `lat` and `lon`, so 
that the desired or closest cinemas can be obtained.
