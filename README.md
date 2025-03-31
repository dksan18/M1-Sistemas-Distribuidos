1. Importações e Configurações Iniciais

from fastapi import FastAPI, HTTPException
import httpx
import asyncio
FastAPI: Usado para criar a API, mas utilizado para fazer uso do HTTPException para retornar um exception.

httpx: Biblioteca assíncrona para fazer requisições HTTP. Usada para acessar as APIs externas (OMDB e TMDB).

asyncio: Biblioteca para executar tarefas assíncronas. Permite fazer chamadas para as APIs de forma concorrente, otimizando o tempo de execução.

2. Definição de Constantes

OMDB_API_KEY = ""
TMDB_API_KEY = ""
OMDB_URL = "http://www.omdbapi.com/"
TMDB_URL = "https://api.themoviedb.org/3/movie/"
Aqui definimos as variáveis que contêm:

OMDB_API_KEY e TMDB_API_KEY: As chaves de acesso para as APIs externas (OMDB e TMDB).

OMDB_URL e TMDB_URL: URLs base das APIs OMDB e TMDB, que são usadas nas requisições para obter informações de filmes.

3. Função fetch_omdb

async def fetch_omdb(title: str, year: int):
    params = {"t": title, "y": year, "apikey": OMDB_API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(OMDB_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            return {"titulo": data.get("Title"), "ano": data.get("Year"), "sinopse": data.get("Plot")}
        raise HTTPException(status_code=400, detail="Erro ao buscar dados no OMDB")

Objetivo: Esta função consulta a API do OMDB para obter detalhes sobre um filme.

Entrada: Recebe o título (title) e o ano (year) do filme.

Requisição HTTP: Usa a biblioteca httpx para fazer uma requisição GET na API OMDB, passando o título, ano e a chave da API como parâmetros.

Resposta: Se a resposta for bem-sucedida, a função extrai os dados JSON da resposta e retorna contendo o título, ano e sinopse do filme.

Erro: Caso ocorra um erro (qualquer outro status de resposta), a função retorna uma exceção.

4. Função fetch_tmdb_reviews

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

Objetivo: Esta função consulta a API do TMDB para obter as reviews de um filme.

Entrada: Recebe o movie_id, que é o ID único do filme no TMDB.

Requisição HTTP: A requisição GET é feita à API do TMDB para obter as reviews, usando o ID do filme e a chave da API.

Resposta: Se a requisição for bem-sucedida, a função filtra as reviews e retorna até 3 delas.

Erro: Se não for possível obter as reviews ou se houver um erro, a função retorna uma exceção HTTP.

5. Função fetch_tmdb_movie_id

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

Objetivo: Esta função consulta a API do TMDB para obter o ID do filme baseado no título e ano.

Entrada: Recebe o title e o year do filme.

Requisição HTTP: A requisição GET é feita à API de pesquisa de filmes do TMDB, utilizando o título, ano e a chave da API.

Resposta: Se a resposta for bem-sucedida e encontrar filmes correspondentes, retorna o ID do primeiro filme encontrado.

Erro: Caso nenhum filme seja encontrado ou outro erro ocorra, retorna uma exceção HTTP.

6. Função get_movie

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
Objetivo: Esta função faz a coleta das informações do filme a partir das APIs OMDB e TMDB.

Processo assíncrono: Ela usa asyncio.gather() para realizar as duas requisições assíncronas para o OMDB e TMDB em paralelo, sem bloquear o processo.

A fetch_omdb retorna o título, ano e sinopse do filme.

A fetch_tmdb_movie_id retorna o ID do filme, que será usado para buscar as reviews.

Após obter o ID do filme, a função chama fetch_tmdb_reviews para coletar as reviews.

Retorno: Retorna um dicionário com as informações completas do filme, incluindo título, ano, sinopse e até 3 reviews.

7. Bloco Principal (__main__)

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

Objetivo: Este é o ponto de entrada do programa, que executa a lógica principal.

Entrada do usuário: Solicita ao usuário que forneça o título e o ano do filme, via input.

Chamada à função get_movie: Chama a função get_movie, que faz as requisições assíncronas para as APIs.

Exibição do resultado: Exibe as informações do filme (título, ano, sinopse) e as reviews (se houver) de forma organizada e clara no terminal.

Resumo de Como Funciona o Código

O usuário fornece o título e o ano do filme.

O código realiza duas consultas paralelas:

Uma consulta à API OMDB para obter informações básicas (título, ano, sinopse).

Outra consulta à API TMDB para obter o ID do filme, seguido das reviews.

As informações são processadas e exibidas de maneira organizada no terminal.
