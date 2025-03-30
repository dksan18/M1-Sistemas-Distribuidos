from fastapi import FastAPI, HTTPException
import httpx
import asyncio

OMDB_API_KEY = "fecfc339"
TMDB_API_KEY = "f8ba41067baa4af0ee72f4f26e60d955"
OMDB_URL = "http://www.omdbapi.com/"
TMDB_URL = "https://api.themoviedb.org/3/movie/"


async def fetch_omdb(title: str, year: int):
    params = {"t": title, "y": year, "apikey": OMDB_API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(OMDB_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            return {"titulo": data.get("Title"), "ano": data.get("Year"), "sinopse": data.get("Plot")}
        raise HTTPException(status_code=400, detail="Erro ao buscar dados no OMDB")


async def fetch_tmdb_reviews(movie_id: int):
    url = f"{TMDB_URL}{movie_id}/reviews"
    params = {"api_key": TMDB_API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            reviews = [review["content"] for review in data.get("results", [])][:3]
            return reviews
        raise HTTPException(status_code=400, detail="Erro ao buscar reviews no TMDB")


async def fetch_tmdb_movie_id(title: str, year: int):
    search_url = "https://api.themoviedb.org/3/search/movie"
    params = {"query": title, "year": year, "api_key": TMDB_API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(search_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                return data["results"][0]["id"]
        raise HTTPException(status_code=400, detail="Filme não encontrado no TMDB")


async def get_movie(title: str, year: int):
    omdb_task = fetch_omdb(title, year)
    movie_id_task = fetch_tmdb_movie_id(title, year)

    omdb_data, movie_id = await asyncio.gather(omdb_task, movie_id_task)
    reviews = await fetch_tmdb_reviews(movie_id)

    return {
        "titulo": omdb_data["titulo"],
        "ano": omdb_data["ano"],
        "sinopse": omdb_data["sinopse"],
        "reviews": reviews
    }


if __name__ == "__main__":
    title = input("Digite o título do filme: ")
    year = int(input("Digite o ano do filme: "))
    result = asyncio.run(get_movie(title, year))

    print("\nResultados da pesquisa:\n")
    print(f"Título: {result['titulo']}")
    print(f"Ano: {result['ano']}")
    print(f"Sinopse: {result['sinopse']}\n")

    print("Reviews:\n")
    if result["reviews"]:
        for idx, review in enumerate(result["reviews"], start=1):
            print(f"Review {idx}: {review}\n")
    else:
        print("Não há reviews disponíveis.")
