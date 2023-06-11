import pandas as pd
from collections import Counter
import json
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from flask import send_file
font = ImageFont.truetype('static/Montserrat-Black.ttf', 55)

def get_all_top_tracks(sp):
    data = {'songs': [], 'uri': [], 'artists': []}
    offset = 0
    all_artists = []
    while True:
        results = sp.current_user_top_tracks(time_range='long_term', limit=50, offset=offset)
        
        if not results['items']: 
            break

        for item in (results['items']):
            data['uri'].append(item['uri'])
            try:
                image = item['album']['images'][0]['url']
            except:
                image = 'https://cdn-icons-png.flaticon.com/512/26/26805.png'
            song = {
                    'name': item['name'], 
                    'url': item['external_urls']['spotify'], 
                    'artists': ', '.join([i['name'] for i in item['album']['artists']]),
                    'images': image
                    }
            all_artists.extend(i['name'] for i in item['album']['artists'])
            data['songs'].append(song)
        
        offset+=49

    all_artists = [{'x': i[0], 'y': i[1]} for i in Counter(all_artists).most_common()]
    data['songs'] = data['songs'][:10]
    data['uri'] = data['uri']
    data['all_artists'] = all_artists  #dict(Counter(all_artists))

    return data

def get_playlist_songs(playlist_id):
    songs = []
    offset = 0
    while True:
        playlist = sp.playlist_items(playlist_id, limit=100, offset=offset)
   
        if not playlist['items']: 
            break

        for item in (playlist['items']):
            songs.append(item['track']['uri'])

        offset+=100
    print(json.dumps(songs, indent=2))
    return songs

def get_all_top_artists(sp):
    data = {'artists': [], 'genres': []}
    genres = []
    offset = 0

    while True:
        results = sp.current_user_top_artists(time_range='long_term', limit=50, offset=offset)

        if not results['items']: 
            break

        for item in results['items']:
            try:
                image = item['images'][0]['url']
            except:
                image = 'https://cdn-icons-png.flaticon.com/512/26/26805.png'
            artist = {
                    'name': item['name'], 
                    'followers': item['followers']['total'], 
                    'images': image, 
                    'url': item['external_urls']['spotify']
                    }

            data['artists'].append(artist)

            genres.extend(item['genres'])
        
        offset += 50

    genres = list(dict.fromkeys(sorted(genres, key=genres.count, reverse=True)))[:5]
    data['genres'] = genres

    data['artists'] = data['artists'][:10]
    
    return data

def get_audio_features(sp, songs):
    audio_features = []
    offset=0

    while True:
        feature = sp.audio_features(songs[offset:offset+100])
        if not feature[0]:
            break
        
        audio_features.extend(feature)

        offset+=100
    features_list = []

    columns=['energy', 'liveness',
             'tempo', 'speechiness',
             'acousticness', 'instrumentalness',
             'danceability', 'valence', 'duration_ms']

    for features in audio_features:
        try:
            features_list.append([features['energy'], features['liveness'],
                                  features['tempo'], features['speechiness'],
                                  features['acousticness'], features['instrumentalness'],
                                  features['danceability'], features['valence'], features['duration_ms']]
                                )
        except:
            pass

    data = pd.DataFrame(features_list, columns=columns)
    tempo = [data['tempo'].max(), data['tempo'].mean(axis=0), data['tempo'].min()]
    tempo = [float(f'{i: .2f}')/2 for i in tempo] #Limiting to 2 decimal places
    duration = [data['duration_ms'].max(), data['duration_ms'].mean(axis=0), data['duration_ms'].min()]
    duration_str = []
    for time in duration:
        seconds=(time/1000)%60
        seconds = int(seconds)
        minutes=(time/(1000*60))%60
        minutes = int(minutes)

        duration_str.append(f'{minutes} minutes {seconds} seconds' if minutes > 1 else f'{minutes} minute {seconds} seconds')

    duration = [float(f'{i/1000: .2f}') for i in duration]

    plot_columns = columns
    plot_columns.remove('tempo')

    means = [float(f'{i: .2f}') for i in list(data.mean(axis=0)) if 0<=i<=1] # -1 index to remove 'mode'
  
    return {'attributes': plot_columns, 'values': means, 'tempo': tempo, 'duration': [duration_str, duration]}

def get_user(sp):
    temp = sp.current_user()
    
    return {'name': temp['display_name'], 'id':temp['id'], 'followers': temp['followers']['total'], 'image': temp['images']}

def get_recommended_artists(sp, id):
    artists = sp.artist_related_artists(id)
    data = []
    for artist in artists['artists'][:5]:
        try:
            image = artist['images'][0]['url']
        except:
            image = 'https://cdn-icons-png.flaticon.com/512/26/26805.png'
        temp = {
                'name': artist['name'], 
                'followers': artist['followers']['total'], 
                'images': image, 
                'url': artist['external_urls']['spotify']
                }
        data.append(temp)
    
    return data

def get_recommendations(sp, artists, songs, genre, audio_features):

    artist_ids = []
    for i in artists['artists'][:2]:
        artist_ids.append(i['url'][32:])
    song_list=[]
    data = sp.recommendations(seed_artists=artist_ids, seed_tracks=songs[:2], seed_genres=[genre], 
    target_energy=audio_features[0],
    target_liveness=audio_features[1],
    target_speechiness=audio_features[2],
    target_acousticness=audio_features[3],
    target_instrumentalness=audio_features[4],
    target_danceability=audio_features[5],
    target_valence=audio_features[6],
    )

    for item in data['tracks']:
        artists = [j['name'] for j in item['artists']]
        try:
            image = item['album']['images'][0]['url']
        except:
            image = 'https://cdn-icons-png.flaticon.com/512/26/26805.png'
        song_list.append({
            'name': item['name'],
            'url': item['external_urls']['spotify'],
            'artists': ', '.join(artists),
            'images': image
        })

    return song_list[:5]

def create_playlist(sp,songs,uid):
    playlist = sp.user_playlist_create(uid, 'Spotify Stats: Your Top Songs!', description='Your Top Songs of all time!')
    playlist_id = playlist['id']
    tracks_add = sp.user_playlist_add_tracks(uid, playlist_id, songs)
    playlist_image = sp.playlist_cover_image(playlist_id)[0]['url']
    return {'name': playlist['name'], 'id': playlist_id, 'url': playlist['external_urls']['spotify'], 'image': playlist_image}

def create_image(songs, artists, username):
    artists_list = []
    songs_list = []
    for i in artists:
        response = requests.get(i)
        img = Image.open(BytesIO(response.content))
        artists_list.append(img)
    for i in songs:
        response = requests.get(i)
        img = Image.open(BytesIO(response.content))
        songs_list.append(img)
    bg = Image.open('static/template.png')

    d = ImageDraw.Draw(bg)
    d.text((33,26), username, font=font, fill=(255,255,255))

    artists_list[0] = artists_list[0].resize((550,550))
    artists_list[1] = artists_list[1].resize((337,337))
    artists_list[2] = artists_list[2].resize((213,213))
    artists_list[3] = artists_list[3].resize((213,213))

    bg.paste(artists_list[0], (0, 156))
    bg.paste(artists_list[1], (550, 156))
    bg.paste(artists_list[2], (550, 493))
    bg.paste(artists_list[3], (763, 493))

    songs_list[0] = songs_list[0].resize((550,550))
    songs_list[1] = songs_list[1].resize((337,337))
    songs_list[2] = songs_list[2].resize((213,213))
    songs_list[3] = songs_list[3].resize((213,213))

    bg.paste(songs_list[0], (474, 706))
    bg.paste(songs_list[1], (137, 707))
    bg.paste(songs_list[2], (261, 1045))
    bg.paste(songs_list[3], (48, 1043))

    return bg

def serve_image(img):
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='SpotifyStats.png')
