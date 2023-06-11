from flask import Flask, redirect, render_template, url_for, request, session, flash, jsonify, abort
import spotipy
import os
import time
import json
from utils import get_all_top_tracks, get_all_top_artists, get_audio_features, get_recommended_artists, get_recommendations, get_user, create_playlist, create_image, serve_image

app = Flask(__name__)
app.secret_key = 'secretverysecret'

SCOPE = 'user-top-read user-read-private playlist-modify-public'

@app.errorhandler(500)
def internal_error(e):
    return '<h1>Sorry Something went wrong, data from your account cannot be extracted.</h1>', 500

@app.before_request
def before_request():
    if os.path.exists(".cache"):
        os.remove(".cache")

@app.route('/verify')
def verify():
    sp_auth = spotipy.oauth2.SpotifyOAuth(scope=SCOPE)
    auth_url = sp_auth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_auth = spotipy.oauth2.SpotifyOAuth(scope=SCOPE)
    session.clear()
    code = request.args.get('code')
    
    token_info = sp_auth.get_access_token(code=code)
    session['token_info'] = token_info

    return redirect(url_for('info'))

@app.route('/info')
def info():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        flash("Please Login with your Spotify Account")
        return redirect('/')

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    user = get_user(sp)
    songs = get_all_top_tracks(sp)
    artists = get_all_top_artists(sp)
    audio_features = get_audio_features(sp, songs['uri'])
    recommended_artists = get_recommended_artists(sp, artists['artists'][0]['url'][32:])
    recommended_songs = get_recommendations(sp, artists, songs['uri'], artists['genres'][0], audio_features['values'])
    
    session['songs_5'] = [i['images'] for i in songs['songs'][:5]]
    session['artists_5'] = [i['images'] for i in artists['artists'][:5]]
    session['username'] = user['name']
    
    return render_template('info.html', songs=songs, artists=artists, similar=recommended_artists, tracks=recommended_songs, audio=audio_features, user=user)

@app.route('/')
def index():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    return render_template('index.html', auth=authorized)

@app.route('/create')
def create():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        flash("Please Login with your Spotify Account")
        return redirect('/')

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    user = get_user(sp)
    songs = get_all_top_tracks(sp)

    playlist = create_playlist(sp,songs['uri'],user['id'])

    return render_template('create.html', playlist=playlist)

@app.route('/share')
def share():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        flash("Please Login with your Spotify Account")
        return redirect('/')
    return serve_image(create_image(songs=session['songs_5'], artists=session['artists_5'], username=session['username']))

@app.route('/logout')
def logout():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        flash('You are already Logged out!')
        return redirect('/')
    
    session.pop('token_info')
    flash('You have successfully Logged Out!')
    return redirect('/')

@app.route('/temp')
def temp():
    abort(500)
    return 'hello'

# Checks to see if token is valid and gets a new token if not
def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = spotipy.oauth2.SpotifyOAuth(scope = SCOPE)
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

'''if __name__ == "__main__":
    app.run(debug=True)
'''
