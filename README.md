# Cinemas Webscrapper

## Functional Requirements

The API provided by this service must allow:
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
* ...

## Database ER diagram
![Database model](static/doc/Cinemas_NOS_DB_EN.png)

## Usage

#### Setup

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

#### API

```http
GET /movies/by_cinema?search_term=<>&lat=<>&lon=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional**. Cinema query. |
| `lat` and `lon` | `float` | **Optional**. User location. |

```http
GET /movies/search
```

```http
GET /movies/releases
```

```http
GET /movies/details
```

```http
GET /sessions/by_duration?search_term=<>&lat=<>&lon=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional**. Cinema query. |
| `lat` and `lon` | `float` | **Optional**. User location. |

```http
GET /sessions/next_sessions?search_term=<>&lat=<>&lon=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional**. Cinema query. |
| `lat` and `lon` | `float` | **Optional**. User location. |

```http
GET /sessions/by_movie?search_term=<>&lat=<>&lon=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional**. Cinema query. |
| `lat` and `lon` | `float` | **Optional**. User location. |

```http
GET /sessions/by_date?search_term=<>&lat=<>&lon=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional**. Cinema query. |
| `lat` and `lon` | `float` | **Optional**. User location. |