from flask import Flask, redirect, request, render_template, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import requests
from credentials import CLIENT_ID, CLIENT_SECRET
from song import Song

app = Flask(__name__)

# variables to keep track of current settings
user_auth_code = []
access_token = []
curr_song = []
curr_device = []
curr_playlist = []

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/go")
def start_app():
    if(user_auth_code == []):
        # user is not already authorized
        return  redirect('https://accounts.spotify.com/authorize?client_id=' + CLIENT_ID + '&response_type=code&scope=streaming+user-read-birthdate+playlist-read-private+user-read-email+user-read-private+playlist-modify-public+playlist-modify-private+user-read-playback-state+user-modify-playback-state+user-read-currently-playing&redirect_uri=http%3A%2F%2Flocalhost:5000%2Frequestauth')
    else:
        return redirect('/choosedevice')

# need to have authorization from Spotify
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
        if(len(access_token) > 1):
            access_token.pop(0)
        return redirect('/choosedevice')
    else:
        # user denied authorization
        return redirect('/noauth')

# route for choosing device
@app.route('/choosedevice', methods=['GET'])
def choose_device():
    spotify_url = 'https://api.spotify.com/v1/me/player/devices'
    if(len(access_token)<1):
        return redirect('/')
    params = {'access_token' : access_token[0]}
    spotify_api_response = requests.get(spotify_url, params=params).json()
    devices = spotify_api_response['devices']
    return render_template('choose_device.html', devices=devices)

# route for choosing playlist
@app.route('/chooseplaylist', methods=['GET'])
def choose_playlist():
    device_id = request.args.get('device_id')
    curr_device.append(device_id)
    if(len(curr_device) > 1):
        curr_device.pop(0)
    spotify_url ='https://api.spotify.com/v1/me/playlists'
    params = {'access_token' : access_token[0], 'limit' : '50'}
    spotify_api_response = requests.get(spotify_url, params=params).json()
    playlists = spotify_api_response['items']
    for playlist in playlists:
        print(playlist)
    return render_template('choose_playlist.html', playlists=playlists)




@app.route('/app',  methods=['GET'])
def main_app():
    # check if user is currently verified
    if(user_auth_code == []):
        return redirect('/')
    playlist_id = request.args.get('playlist_id')
    user_uri = request.args.get('user_uri')
    curr_playlist.append(playlist_id)
    if(len(curr_playlist) > 1):
        curr_playlist.pop(0)
    spotify_url ='https://api.spotify.com/v1/me'
    params = {'access_token' : access_token[0]}
    spotify_api_response = requests.get(spotify_url, params=params).json()
    print(spotify_api_response)
    return render_template("song_list.html", token=access_token[0], device_id=curr_device[0], playlist_id=curr_playlist[0], user_uri=user_uri)

@app.route('/noauth',  methods=['GET'])
def not_authorized():
    return render_template('no_auth.html')


# route for receiving sms via Twilio and ngrok
@app.route("/sms", methods=['POST'])
def get_sms():
    song_name = '\"' + request.values.get('Body') +'\"'
    song_info = get_song_link(song_name)
    return ''


def get_song_link(song_name):
    spotify_url = 'https://api.spotify.com/v1/search'
    # requesting given song, providing access_token, and limiting results to 2 songs
    params = {'q': song_name, 'type': 'track', 'access_token' : access_token[0], 'limit' : '2'}
    spotify_api_response = requests.get(spotify_url, params=params).json()
    song_list = spotify_api_response['tracks']['items']

    song_info = {}

    if song_list:
        song_info['name'] = song_list[0]['name']
        song_info['artist'] = song_list[0]['artists'][0]['name']
        song_info['preview_url'] = song_list[0]['preview_url']
        song_info['uri'] = song_list[0]['uri']

    # storing songs in Song class
    my_song = Song(song_info['name'], song_info['artist'], song_info['preview_url'], song_info['uri'])
    print(my_song.get_name())
    print(my_song.get_artist())
    print(my_song.get_url())
    print(my_song.get_uri())

    r = requests.post('https://api.spotify.com/v1/playlists/'+ curr_playlist[0] +'/tracks?uris='+ song_info["uri"], headers={'Authorization': 'Bearer ' + access_token[0]}).json()

    return song_info

@app.route("/getsong", methods=['GET'])
def get_song():
    if(len(curr_song) == 1):
        return jsonify(curr_song)
    else:
        return jsonify([])


if __name__ == "__main__":
    app.run(port=5000, debug=True)