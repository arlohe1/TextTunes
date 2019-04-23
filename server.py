from flask import Flask, redirect, request, render_template, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import requests
from credentials import CLIENT_ID, CLIENT_SECRET

app = Flask(__name__)

user_auth_code = []
access_token = []
curr_song = []
curr_device = []
curr_playlist = []

@app.route("/")
def start_app():
    print(user_auth_code)
    if(user_auth_code == []):
        # user is not already authorized
        return  redirect('https://accounts.spotify.com/authorize?client_id=' + CLIENT_ID + '&response_type=code&scope=streaming+user-read-birthdate+playlist-read-private+user-read-email+user-read-private+playlist-modify-public+playlist-modify-private+user-read-playback-state+user-modify-playback-state+user-read-currently-playing&redirect_uri=http%3A%2F%2Flocalhost:5000%2Frequestauth')
    else:
        print('hello')
        return redirect('/choosedevice')


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
        print(access_token)
        return redirect('/choosedevice')
    else:
        # user denied authorization
        return redirect('/noauth')


@app.route('/choosedevice', methods=['GET'])
def choose_device():
    spotify_url = 'https://api.spotify.com/v1/me/player/devices'
    if(len(access_token)<1):
        return redirect('/')
    params = {'access_token' : access_token[0]}
    spotify_api_response = requests.get(spotify_url, params=params).json()
    devices = spotify_api_response['devices']
    print(devices)
    return render_template('choose_device.html', devices=devices)
    # printing info about retreived songs

@app.route('/chooseplaylist', methods=['GET'])
def choose_playlist():
    device_id = request.args.get('device_id')
    print(device_id)
    curr_device = [device_id]
    print('----')
    print(curr_device)
    print('-----')
    spotify_url =' https://api.spotify.com/v1/me/playlists'
    params = {'access_token' : access_token[0], 'limit' : '50'}
    spotify_api_response = requests.get(spotify_url, params=params).json()
    playlists = spotify_api_response['items']
    for playlist in playlists:
        print(playlist['name'])

    return render_template('choose_playlist.html', playlists=playlists)




@app.route('/app',  methods=['GET'])
def main_app():
    # check if user is currently verified
    if(user_auth_code == []):
        return redirect('/')
    playlist_id = request.args.get('playlist_id')
    curr_playlist = [playlist_id]
    print('-----------------------------------------------')
    print(curr_playlist)
    # WHY IS THIS LIST EMPTY
    print(curr_device)
    print('--------------------------------------------------------')
    # hardcoding the device id because i have no clue why it isnt being passed on
    device_id = 'dd3cc946431f8b0ae482c5e38abe84f01e0c785c'
    return render_template("song_list.html", token=access_token[0], device_id=device_id)

@app.route('/noauth',  methods=['GET'])
def not_authorized():
    return render_template('no_auth.html')


# route for receiving sms via Twilio and ngrok
@app.route("/sms", methods=['POST'])
def get_sms():
    song_name = '\"' + request.values.get('Body') +'\"'
    song_info = get_song_link(song_name)
    print('done---------------------------------------------------------------------------------')
    return ''


def get_song_link(song_name):
    spotify_url = 'https://api.spotify.com/v1/search'
    # requesting given song, providing access_token, and limiting results to 2 songs
    params = {'q': song_name, 'type': 'track', 'access_token' : access_token[0], 'limit' : '2'}
    spotify_api_response = requests.get(spotify_url, params=params).json()
    song_list = spotify_api_response['tracks']['items']
    # printing info about retreived songs
    for song in song_list:
        print(song['name'])
        print(song['artists'])
        print(song['preview_url'])
        print(song['uri'])
        print('-----')

    song_info = {}

    if song_list:
        song_info['name'] = song_list[0]['name']
        song_info['artist'] = song_list[0]['artists'][0]['name']
        song_info['preview_url'] = song_list[0]['preview_url']
        song_info['uri'] = song_list[0]['uri']

    print('-----------------------------------------------')
    print(curr_playlist)
    print(access_token)
    print('--------------------------------------------------------')
    r = requests.post('https://api.spotify.com/v1/playlists/4Oz5McF8P1WSppLomN8D5Q/tracks?uris='+ song_info["uri"], headers={'Authorization': 'Bearer ' + access_token[0]}).json()
    # r = requests.post('https://api.spotify.com/v1/playlists/'+curr_playlist[0]+'/tracks', data=payload).json()
    print('---11111111--------')
    print(r)
    print('---11111111--------')


    return song_info



@app.route("/getsong", methods=['GET'])
def get_song():
    print('---')
    print(curr_song)
    if(len(curr_song) == 1):
        return jsonify(curr_song)
    else:
        return jsonify([])



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