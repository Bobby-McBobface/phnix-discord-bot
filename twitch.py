import discord
import urllib3
import json
import configuration

http = urllib3.PoolManager()

def refresh_token():
    '''
    Args:
    client: discord.Client
    '''
    with open("env/twitch_client_id") as file:
        client_id = file.read()

    with open("env/twitch_secret") as file:
        secret = file.read()

    r = http.request("POST", f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={secret}&grant_type=client_credentials")

    data = json.loads(r.data.decode('utf-8'))

    print(data["access_token"])

    with open("env/twitch_auth_token", "w") as file:
        file.write(data["access_token"])

def get_stream():
    with open("env/twitch_client_id") as file:
        client_id = file.read()

    with open("env/twitch_auth_token") as file:
        auth_token = file.read()

    r = http.request("GET", f"https://api.twitch.tv/helix/streams?user_id={configuration.TWITCH_CHANNEL_ID}",
    headers={'client-id': client_id, 'Authorization': f'Bearer {auth_token}'})

    if r.status == 401:
        refresh_token()

    print(r.data)

get_stream()