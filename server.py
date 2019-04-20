import os
from flask import Flask, redirect, request, render_template, session
from twilio.twiml.messaging_response import MessagingResponse
import requests
from credentials import CLIENT_ID, CLIENT_SECRET

app = Flask(__name__)

user_auth_code = []
access_token = []

curr_song = []

@app.route("/")
def start_app():
    if(user_auth_code == []):
        # user is not already authorized
        return  redirect('https://accounts.spotify.com/authorize?client_id=' + CLIENT_ID + '&response_type=code&redirect_uri=http%3A%2F%2Flocalhost:5000%2Frequestauth')
    return redirect('/app')


@app.route('/requestauth',  methods=['GET'])
def request_authorization():
    code = request.args.get('code');
    error = request.args.get('error')
    if(error == None):
        # user accepted authorization
        user_auth_code.append(code)

        # requesting access token from spotify api
        payload = {'grant_type':'authorization_code', 'code' : user_auth_code, 'redirect_uri' : 'http://localhost:5000/requestauth'}
        r = requests.post('https://accounts.spotify.com/api/token', data=payload, auth=(CLIENT_ID, CLIENT_SECRET)).json()

        # storing retreived access token
        access_token.append(r['access_token'])
        return redirect('/app')
    else:
        # user denied authorization
        return redirect('/noauth')

@app.route('/app',  methods=['GET'])
def main_app():
    # check if user is currently verified
    if(user_auth_code == []):
        return redirect('/')
    print(curr_song)
    return render_template("home.html")


@app.route('/noauth',  methods=['GET'])
def not_authorized():
    return render_template('no_auth.html')

# route for receiving sms via Twilio and ngrok
@app.route("/sms", methods=['POST'])
def get_sms():
    song_name = request.values.get('Body')
    print(song_name)
    curr_song.append(song_name)
    if len(curr_song) > 1:
        curr_song.pop(0)
    return ''
    #return get_song_link(song_name)


def get_song_link(song_title):
    spotify_url = 'https://api.spotify.com/v1/search'
    access_token_x = access_token[0]
    # requesting given song, providing access_token, and limiting results to 2 songs
    params = {'q': song_title, 'type': 'track', 'access_token' : access_token_x, 'limit' : '2'}
    spotify_api_response = requests.get(spotify_url, params=params).json()
    song_list = spotify_api_response['tracks']['items']
    # printing info about retreived songs
    for song in song_list:
        print(song['name'])
        print(song['artists'])
        print(song['preview_url'])
        print('-----')
    return 'done'







'''
@app.route("/sms", methods=['GET', 'POST'])
def sms_ahoy_reply():
    print('hello')

    """Respond to incoming messages with a friendly SMS."""
    # Start our response
    resp = MessagingResponse()

    # Add a message
    resp.message("Ahoy! Thanks so much for your message.")

    return str(resp)
'''




if __name__ == "__main__":
    app.run(port=5000, debug=True)
