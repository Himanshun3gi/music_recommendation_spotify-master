from django.shortcuts import render
from .forms import PlaylistForm, SongForm
from django.http import HttpResponse
import base64
import requests
from .spotify_recommendations import get_trending_playlist_data, hybrid_recommendations

CLIENT_ID = 'b30cfad2cfe84fc9bacd89d84415da71'
CLIENT_SECRET = 'b7f776f23d87418493c5f0e0fe0245f0'

def get_access_token():
    client_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    client_credentials_base64 = base64.b64encode(client_credentials.encode())
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {client_credentials_base64.decode()}'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_url, data=data, headers=headers)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        return None
from sklearn.preprocessing import MinMaxScaler

def preprocess_music_features(music_df):
    scaler = MinMaxScaler()
    music_features = music_df[['Danceability', 'Energy', 'Key', 
                               'Loudness', 'Mode', 'Speechiness', 'Acousticness',
                               'Instrumentalness', 'Liveness', 'Valence', 'Tempo']].values
    music_features_scaled = scaler.fit_transform(music_features)
    return music_features_scaled

def index(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        song_form = SongForm(request.POST)
        if form.is_valid() and song_form.is_valid():
            playlist_id = form.cleaned_data['playlist_id']
            song_name = song_form.cleaned_data['song_name']
            access_token = get_access_token()
            if access_token:
                music_df = get_trending_playlist_data(playlist_id, access_token)
                music_features_scaled = preprocess_music_features(music_df)  # Example function to preprocess features
                recommendations = hybrid_recommendations(song_name, music_df, music_features_scaled, num_recommendations=5)
                return render(request, 'recommendations/results.html', {'recommendations': recommendations, 'song_name': song_name})
            else:
                return HttpResponse("Error obtaining access token.")
    else:
        form = PlaylistForm()
        song_form = SongForm()

    return render(request, 'recommendations/index.html', {'form': form, 'song_form': song_form})

def home(request):
    return render(request,'recommendations/layout.html')