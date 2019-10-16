

movies = getMovies()
next_debuts = getNextDebuts()
for m in next_debuts:
    movies.append(m)
for m in movies:
    print(m)
