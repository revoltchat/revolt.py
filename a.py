from aiohttp import web, web_request
import aiohttp

API_ENDPOINT = 'https://discord.com/api/v8'
CLIENT_ID = '380423502810972162'
CLIENT_SECRET = 'pt1qgGOiWWhroqPM_NBqM_Nb1OSuySgU'
REDIRECT_URI = 'http://127.0.0.1:8080'

async def exchange_code(code):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    async with aiohttp.ClientSession() as session:
        r = await session.post(f'{API_ENDPOINT}/oauth2/token', data=data, headers=headers)
        r.raise_for_status()
        return await r.json()

async def get_user(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with aiohttp.ClientSession() as session:
        r = await session.get(f"{API_ENDPOINT}/users/@me")
        r.raise_for_status()
        return await r.json()

async def hello(request: web_request.Request):
    code = request.query["code"]
    data = await exchange_code(code)
    user = await get_user(data["access_token"])

    return web.Response(text=user["email"])

app = web.Application()
app.add_routes([web.get('/', hello)])
web.run_app(app)
