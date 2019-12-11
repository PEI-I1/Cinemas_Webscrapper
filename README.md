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
* Create & migrate DB
```
./manage.py makemigrations
./manage.py migrate
```
* Import static data:
`./manage.py loaddata static/cinemas_fixture.json`
* Run *Django* project:
`./manage.py runserver`
* Run *Redis* back-end
`docker run -p 6379:6379 redis`
* Run *Celery* (for periodic database update):
`celery -A cinemas_scrapper.celery worker -B -l INFO`

### Deployment
* Build Docker image
`docker build -t cinemas_scrapper .`
* Run Docker container
`docker run -p 5003:8000 -it cinemas_scrapper`
* Run script
`./Cinemas_Webscrapper/run.sh`


## Architecture
### Database ER diagram
![Database model](static/doc/Cinemas_NOS_DB_EN.png)

### API
<details>
<summary>Search for cinemas or get the closest ones</summary>

```http
GET /scrapper/cinemas/search?search_term=<>&lat=<>&lon=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional***. Cinema query. |
| `lat` and `lon` | `float` | **Optional***. User location. |


**Note**: When values are given to `lat` and `lon` the returned cinemas are in a maximum distance of 20 km.

📄 **Example of use**
```http
GET /scrapper/cinemas/search?search_term=Algarve
```

```json
{
    "cinemas": [
        "Forum Algarve",
        "Mar Shopping Algarve"
    ]
}
```
------
</details>

<!---------------------------------------------------->

<details>
<summary>Search for movies in cinema</summary>

```http
GET /scrapper/movies/by_cinema?search_term=<>&lat=<>&lon=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional***. Cinema query. |
| `lat` and `lon` | `float` | **Optional***. User location. |

📄 **Example of use**
```http
GET /scrapper/movies/by_cinema?search_term=Algarve
```

```json
{
    "Mar Shopping Algarve": [
        "Charlie’s Angels",
        "Le Mans 66'",
        "Knives Out",
        "Jumanji: The Next Level",
        "A Shaun The Sheep Movie: Farmageddon",
        "Bikes",
        "21 Bridges",
        "Frozen II",
        "Star Wars: Episode IX - The Rise of Skywalker",
        "The Aeronauts"
    ],
    "Forum Algarve": [
        "Charlie’s Angels",
        "Jumanji: The Next Level",
        "Knives Out",
        "A Shaun The Sheep Movie: Farmageddon",
        "Cats and Peachtopia",
        "Frozen II",
        "Qu'est-ce qu'on a encore fait au Bon Dieu?",
        "Star Wars: Episode IX - The Rise of Skywalker",
        "The Aeronauts"
    ]
}
```
------
</details>

<!---------------------------------------------------->

<details>
<summary>Search for movies based on genre, producer, cast, synopsis and age restriction</summary>

```http
GET /scrapper/movies/search?genre=<>&cast=<>&producer=<>&synopsis=<>&age=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `genre` | `string` | **Optional**. Movie genre. |
| `cast` | `string` | **Optional**. Actors names, comma separated. |
| `producer` | `string` | **Optional**. Producer name. |
| `synopsis` | `string` | **Optional**. Words to search on the movie synopsis, comma separated. |
| `age` | `int` | **Optional**. Maximum age restriction. |

**Note**: All parameters are optional but at least one of them needs to be provided.

📄 **Example of use**
```http
GET /scrapper/movies/search?cast=Kevin Hart,Dwayne Johnson
```

```json
[
    {
        "Genre": "Aventura",
        "Producer": "Jake Kasdan",
        "Portuguese title": "Jumanji: O Nível Seguinte",
        "Cast": "Dwayne Johnson, Jack Black, Kevin Hart",
        "Banner": "http://cinemas.nos.pt/_layouts/15/Handlers/RenderImage.ashx?file=52285.jpg",
        "Length (min)": 120,
        "Original title": "Jumanji: The Next Level",
        "Synopsis": "O gangue está de volta, mas o jogo mudou. Quando regressam a Jumanji para resgatar um deles, descobrem que nada é como estavam à espera. Os jogadores terão de enfrentar lugares desconhecidos e inexplorados, desde os áridos desertos às montanhas nevadas, para escapar do jogo mais perigoso do mundo.",
        "Released": true,
        "Age rating": 12,
        "Trailer": "https://youtube.com/embed/yx9u6IsJrxM"
    }
]
```
------
</details>

<!---------------------------------------------------->
<details>
<summary>Search for upcoming movies</summary>

```http
GET /scrapper/movies/releases
```

📄 **Example of response**

```json
[
    {
        "Genre": "Animação",
        "Original title": "Spies In Disguise",
        "Cast": "Pedro Bargado, André Raimundo, Carlá de Sá",
        "Banner": "http://cinemas.nos.pt/_layouts/15/Handlers/RenderImage.ashx?file=52276.jpg"
    },
    {
        "Genre": "Thriller",
        "Original title": "Mr. Jones",
        "Cast": "James Norton, Vanessa Kirby, Peter Sarsgaard",
        "Banner": "http://cinemas.nos.pt/_layouts/15/Handlers/RenderImage.ashx?file=52247.jpg"
    },
    {
        "Genre": "Drama",
        "Original title": "Richard Jewell",
        "Cast": "Paul Walter Hauser, Sam Rockwell, Olivia Wilde",
        "Banner": "http://cinemas.nos.pt/_layouts/15/Handlers/RenderImage.ashx?file=52280.jpg"
    }
]
```
------

</details>

<!---------------------------------------------------->

<details>
<summary>Get details of movie</summary>

```http
GET /scrapper/movies/details?movie=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `movie` | `string` | **Required**. Name of the movie. |

📄 **Example of use**
```http
GET /scrapper/movies/details?movie=Joker
```

```json
[
    {
        "Genre": "Thriller",
        "Producer": "Todd Phillips",
        "Portuguese title": "Joker",
        "Cast": "Joaquin Phoenix, Robert De Niro, Zazie Beetz",
        "Banner": "http://cinemas.nos.pt/_layouts/15/Handlers/RenderImage.ashx?file=52161.jpg",
        "Length (min)": 122,
        "Original title": "Joker",
        "Synopsis": "Arthur Fleck é um homem que enfrenta a crueldade e o desprezo da sociedade, juntamente com a indiferença de um sistema que lhe permite passar da vulnerabilidade para a depravação. Durante o dia é um palhaço e à noite luta para se tornar um artista de stand-up comedy…mas descobre que é ele próprio a piada. Sempre diferente de todos em seu redor, o seu riso incontrolável e inapropriado, ganha ainda mais força quando tenta contê-lo, expondo-o a situações ridículas e até à violência. Preso numa existência cíclica que oscila entre o precipício da realidade e da loucura, uma má decisão acarreta uma reacção em cadeia de eventos crescentes e, por fim, mortais.",
        "Released": true,
        "Age rating": 14,
        "Trailer": "https://youtube.com/embed/rje8OUw45UQ"
    }
]
```
------
</details>

<!---------------------------------------------------->

<details>
<summary>Search for sessions of movies under a certain duration</summary>

```http
GET /scrapper/sessions/by_duration?search_term=<>&lat=<>&lon=<>&duration=<>&date=<>&start_time=<>&end_time=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional***. Cinema query. |
| `lat` and `lon` | `float` | **Optional***. User location. |
| `duration` | `int` | **Required**. Maximum value of duration (in minutes). |
| `date` | `Year-Month-Day` | **Optional**. Date. |
| `start_time` | `Hours:Minutes:Seconds` | **Optional**. Lower time limit for the beginning of the sessions. |
| `end_time` | `Hours:Minutes:Seconds` | **Optional**. Upper time limit for the beginning of the sessions. |

📄 **Example of use**
```http
GET /scrapper/sessions/by_duration?search_term=Braga&duration=130&date=2019-12-11&start_time=15:00:00&end_time=15:50:00
```

```json
{
    "Braga Parque": [
        {
            "Availability": "184",
            "Start time": "15:00:00",
            "Movie": "Joker",
            "Start date": "2019-12-11",
            "Ticket link": "https://bilheteira.cinemas.nos.pt/webticket/bilhete.jsp?CinemaId=WA&CodFilme=1983870&DataSessao=2019-12-11&HoraSessao=15:00&Sala=5",
            "Length (min)": 122
        },
        {
            "Availability": "160",
            "Start time": "15:40:00",
            "Movie": "Charlie’s Angels",
            "Start date": "2019-12-11",
            "Ticket link": "https://bilheteira.cinemas.nos.pt/webticket/bilhete.jsp?CinemaId=WA&CodFilme=1000335&DataSessao=2019-12-11&HoraSessao=15:40&Sala=2",
            "Length (min)": 120
        },
        {
            "Availability": "216",
            "Start time": "15:50:00",
            "Movie": "The Aeronauts",
            "Start date": "2019-12-11",
            "Ticket link": "https://bilheteira.cinemas.nos.pt/webticket/bilhete.jsp?CinemaId=WA&CodFilme=1728200&DataSessao=2019-12-11&HoraSessao=15:50&Sala=6",
            "Length (min)": 100
        }
    ]
}
```
------
</details>

<!---------------------------------------------------->

<details>
<summary>Search for the next sessions</summary>

```http
GET /scrapper/sessions/next_sessions?search_term=<>&lat=<>&lon=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional***. Cinema query. |
| `lat` and `lon` | `float` | **Optional***. User location. |

📄 **Example of use**
```http
GET /scrapper/sessions/next_sessions?search_term=Braga
```

```json
{
    "Braga Parque": [
        {
            "Start date": "2019-12-11",
            "Start time": "23:50:00",
            "Movie": "Frozen II",
            "Ticket link": "https://bilheteira.cinemas.nos.pt/webticket/bilhete.jsp?CinemaId=WA&CodFilme=1733660&DataSessao=2019-12-11&HoraSessao=23:50&Sala=3",
            "Availability": "324"
        },
        {
            "Start date": "2019-12-11",
            "Start time": "23:50:00",
            "Movie": "Knives Out",
            "Ticket link": "https://bilheteira.cinemas.nos.pt/webticket/bilhete.jsp?CinemaId=WA&CodFilme=1000338&DataSessao=2019-12-11&HoraSessao=23:50&Sala=7",
            "Availability": "174"
        },
        {
            "Start date": "2019-12-11",
            "Start time": "00:05:00",
            "Movie": "The Aeronauts",
            "Ticket link": "https://bilheteira.cinemas.nos.pt/webticket/bilhete.jsp?CinemaId=WA&CodFilme=1728200&DataSessao=2019-12-12&HoraSessao=00:05&Sala=6",
            "Availability": "216"
        }
    ]
}
```
------
</details>

<!---------------------------------------------------->

<details>
<summary>Search sessions for a given movie</summary>

```http
GET /scrapper/sessions/by_movie?search_term=<>&lat=<>&lon=<>&movie=<>&date=<>&start_time=<>&end_time=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional***. Cinema query. |
| `lat` and `lon` | `float` | **Optional***. User location. |
| `movie` | `string` | **Required**. Name of the movie. |
| `date` | `Year-Month-Day` | **Optional**. Date. |
| `start_time` | `Hours:Minutes:Seconds` | **Optional**. Lower time limit for the beginning of the sessions. |
| `end_time` | `Hours:Minutes:Seconds` | **Optional**. Upper time limit for the beginning of the sessions. |

📄 **Example of use**
```http
GET /scrapper/sessions/by_movie?search_term=Braga&movie=Joker&date=2019-12-11&start_time=17:00:00&end_time=22:00:00
```

```json
{
    "Braga Parque": {
        "Joker": {
            "sessions": [
                {
                    "Start time": "18:00:00",
                    "Availability": "184",
                    "Ticket link": "https://bilheteira.cinemas.nos.pt/webticket/bilhete.jsp?CinemaId=WA&CodFilme=1983870&DataSessao=2019-12-11&HoraSessao=18:00&Sala=5",
                    "Start date": "2019-12-11"
                },
                {
                    "Start time": "21:00:00",
                    "Availability": "184",
                    "Ticket link": "https://bilheteira.cinemas.nos.pt/webticket/bilhete.jsp?CinemaId=WA&CodFilme=1983870&DataSessao=2019-12-11&HoraSessao=21:00&Sala=5",
                    "Start date": "2019-12-11"
                }
            ]
        }
    }
}
```
------
</details>

<!---------------------------------------------------->

<details>
<summary>Search for sessions by date</summary>

```http
GET /scrapper/sessions/by_date?search_term=<>&lat=<>&lon=<>&date=<>&start_time=<>&end_time=<>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `search_term` | `string` | **Optional***. Cinema query. |
| `lat` and `lon` | `float` | **Optional***. User location. |
| `date` | `Year-Month-Day` | **Optional**. Date. |
| `start_time` | `Hours:Minutes:Seconds` | **Optional**. Lower time limit for the beginning of the sessions. |
| `end_time` | `Hours:Minutes:Seconds` | **Optional**. Upper time limit for the beginning of the sessions. |

📄 **Example of use**
```http
GET /scrapper/sessions/by_date?search_term=Braga&date=2019-12-11&start_time=16:00:00&end_time=16:25:00
```

```json
{
    "Braga Parque": [
        {
            "Start time": "16:00:00",
            "Availability": "324",
            "Ticket link": "https://bilheteira.cinemas.nos.pt/webticket/bilhete.jsp?CinemaId=WA&CodFilme=1984110&DataSessao=2019-12-11&HoraSessao=16:00&Sala=3",
            "Movie": "Frozen II",
            "Start date": "2019-12-11"
        },
        {
            "Start time": "16:10:00",
            "Availability": "177",
            "Ticket link": "https://bilheteira.cinemas.nos.pt/webticket/bilhete.jsp?CinemaId=WA&CodFilme=1000350&DataSessao=2019-12-11&HoraSessao=16:10&Sala=4",
            "Movie": "Qu'est-ce qu'on a encore fait au Bon Dieu?",
            "Start date": "2019-12-11"
        },
        {
            "Start time": "16:20:00",
            "Availability": "107",
            "Ticket link": "https://bilheteira.cinemas.nos.pt/webticket/bilhete.jsp?CinemaId=WA&CodFilme=1000351&DataSessao=2019-12-11&HoraSessao=16:20&Sala=1",
            "Movie": "Bikes",
            "Start date": "2019-12-11"
        }
    ]
}
```
------
</details>

<br/>

***Note**: The methods related to sessions require `search_term` or in alternative `lat` and `lon`, so that the desired or closest cinemas can be obtained.
