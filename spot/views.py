from django.http import HttpResponse, Http404
from django.shortcuts import render
import sys
import spotipy
import spotipy.util as util
import configparser

def index(request):
    return render(request, 'spot/index.html', None)

def setup_spot():
    try:
        config = configparser.ConfigParser()
        config.read('/home/mick/.spot.txt')
        client_id = config['DEFAULT']['ClientID']
        client_secret = config['DEFAULT']['ClientSecret']
        redirect_uri= config['DEFAULT']['Redirect']
        scope = 'user-read-recently-played user-top-read'
        token = util.prompt_for_user_token('mickmcdonnal', scope, client_id=client_id,
            client_secret=client_secret,redirect_uri=redirect_uri)
        if token:
            sp = spotipy.Spotify(auth=token)
            return sp
        else:
            return None
    except:
        return None

def top_tracks(request, term):
    top_tracks = []
    sp = setup_spot()
    if sp:
        counter = 0
        offset = 0
        while counter < 5:
            results = sp.current_user_top_tracks(limit=20, offset=offset, time_range=term)
            offset += 20
            counter += 1
            if len(results) == 0:
                break
            for item in results['items']:
                top_tracks.append(item)

        context = {'term': term, 'top_tracks_list': top_tracks}
        return render(request, 'spot/top_tracks.html', context)
    else:
        raise Http404('<h1>Spotify authorization failed.</h1>')

def top_artists(request, term):
    top_artists = []
    sp = setup_spot()
    if sp:
        counter = 0
        offset = 0
        while counter < 5:
            results = sp.current_user_top_artists(limit=20, offset=offset, time_range=term)
            offset += 20
            counter += 1
            if len(results) == 0:
                break
            for item in results['items']:
                top_artists.append(item)

        context = {'term': term, 'top_artists_list': top_artists}
        return render(request, 'spot/top_artists.html', context)
    else:
        raise Http404('<h1>Spotify authorization failed.</h1>')
    


def recent_tracks(request):
    # as of October 2018, pip install spotipy does not install the latest
    # version, and it does not include current_user_recently_played. Download
    # the latest from github to fix it.
    recently_played = []
    sp = setup_spot()
    if sp:
        results = sp.current_user_recently_played(limit=20)
        for item in results['items']:
            recently_played.append(item)
        context = {'recent_tracks_list': recently_played}
        return render(request, 'spot/recent_tracks.html', context)
    else:
        raise Http404('<h1>Spotify authorization failed.</h1>')


def artist_detail(request, id):
    top_tracks = []
    sp = setup_spot()
    if sp:
        artist = sp.artist(id)
        results = sp.artist_top_tracks(id)
        for track in results['tracks']:
            top_tracks.append(track)

        context = {'artist': artist['name'], 'top_tracks_list': top_tracks}
        return render(request, 'spot/artist_detail.html', context)
    else:
        raise Http404('<h1>Spotify authorization failed.</h1>')


