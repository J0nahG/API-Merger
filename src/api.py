from fastapi import FastAPI, Request
import aiohttp
import asyncio
from contextlib import asynccontextmanager
import json

urls = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Loads list of URLs from config file when API is started.
    """
    urls.clear()
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        for source in config["sources"]:
            if source["enabled"] == True:
                urls.append(source["url"])
        # urls.extend([source["url"] for source in config["sources"]])
    except Exception:
        pass
    yield

app = FastAPI(debug=True, lifespan=lifespan)

@app.get("/cubelify")
async def cubelify_endpoint(id: str, name: str, sources: str, request: Request):
    """
    Handles requests from cubelify.
    """
    formatted_urls = [format_url(url=url, id=id, name=name, sources=sources) for url in urls]
    headers = dict(request.headers)
    headers.pop('accept-encoding', None)
    headers.pop('host', None)
    
    cubelify_response = {"score":{"value":0,"mode":"add"},"tags":[]}
    tasks = [api_worker(url=url, headers=headers) for url in formatted_urls]
    api_responses = await asyncio.gather(*tasks)

    for api_response in api_responses:
        if "score" in api_response.keys():
            cubelify_response["score"]["value"] += api_response["score"]["value"]
        if "tags" in api_response.keys():
            cubelify_response["tags"].extend(api_response["tags"])

    return cubelify_response

async def api_worker(url: str, headers: dict):
    """
    Makes a request to an external API and returns the resulting json data.
    """
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                data = await response.json()
                if response.status == 200:
                    return data
                else:
                    return {"score":{"value":0,"mode":"add"},"tags":[{'icon': 'mdi-alert-circle', 'tooltip': f'{url} returned status code {response.status}', 'color': 13959168}]}
    except Exception as e:
        return {"score":{"value":0,"mode":"add"},"tags":[{'icon': 'mdi-alert-circle', 'tooltip': str(e), 'color': 13959168}]}

def format_url(url: str, id: str, name: str, sources: str):
    """
    Takes a cubelify formatted URL and sets query fields properly.
    """
    if '?' in url:
        if "{{id}}" in url or "{{name}}" in url or "{{sources}}" in url:
            url = url.replace("{{id}}", id)
            url = url.replace("{{name}}", name)
            url = url.replace("{{sources}}", sources)
        else:
            base_url = url.split("?")[0]
            try:
                query_string = url.split("?", 1)[1]
            except IndexError:
                query_string = ""

            query_fields = query_string.split("&")
            for field in query_fields:
                if field.startswith("id=") or field.startswith("name="):
                    del query_fields[query_fields.index(field)]

            query_fields.append(f"id={id}")
            query_fields.append(f"name={name}")
            query_string = query_fields[0]

            for field in query_fields[1:]:
                query_string += "&" + field

            url = base_url + "?" + query_string
    else:
        url += f'?id={id}&name={name}'

    return url
