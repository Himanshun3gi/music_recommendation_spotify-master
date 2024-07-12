import requests
import base64
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

# Replace with your own Client ID and Client Secret
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

def get_trending_playlist_data(playlist_id, access_token, limit_tracks=50):
    sp = spotipy.Spotify(auth=access_token)
    music_data = []
    offset = 0
    limit = 100

    total_tracks = sp.playlist_tracks(playlist_id, fields='total')['total']
    if limit_tracks:
        total_tracks = min(total_tracks, limit_tracks)

    with tqdm(total=total_tracks, desc="Processing tracks") as pbar:
        while len(music_data) < total_tracks:
            playlist_tracks = sp.playlist_tracks(playlist_id, fields='items(track(id, name, artists, album(id, name)))', offset=offset, limit=limit)
            if not playlist_tracks['items']:
                break

            for track_info in playlist_tracks['items']:
                track = track_info['track']
                if track is None:
                    continue

                track_name = track['name']
                artists = ', '.join([artist['name'] for artist in track['artists']])
                album_name = track['album']['name']
                album_id = track['album']['id']
                track_id = track['id']
                audio_features = sp.audio_features(track_id)[0] if track_id else None

                try:
                    album_info = sp.album(album_id) if album_id else None
                    release_date = album_info['release_date'] if album_info else None
                except Exception as e:
                    release_date = None

                try:
                    track_info = sp.track(track_id) if track_id else None
                    popularity = track_info['popularity'] if track_info else None
                except Exception as e:
                    popularity = None

                track_data = {
                    'Track_Name': track_name,
                    'Artists': artists,
                    'Album_Name': album_name,
                    'Album ID': album_id,
                    'Track ID': track_id,
                    'Popularity': popularity,
                    'Release_Date': release_date,
                    'Duration (ms)': audio_features['duration_ms'] if audio_features else None,
                    'Explicit': track_info.get('explicit', None) if track_info else None,
                    'External URLs': track_info.get('external_urls', {}).get('spotify', None) if track_info else None,
                    'Danceability': audio_features['danceability'] if audio_features else None,
                    'Energy': audio_features['energy'] if audio_features else None,
                    'Key': audio_features['key'] if audio_features else None,
                    'Loudness': audio_features['loudness'] if audio_features else None,
                    'Mode': audio_features['mode'] if audio_features else None,
                    'Speechiness': audio_features['speechiness'] if audio_features else None,
                    'Acousticness': audio_features['acousticness'] if audio_features else None,
                    'Instrumentalness': audio_features['instrumentalness'] if audio_features else None,
                    'Liveness': audio_features['liveness'] if audio_features else None,
                    'Valence': audio_features['valence'] if audio_features else None,
                    'Tempo': audio_features['tempo'] if audio_features else None,
                }

                music_data.append(track_data)
                pbar.update(1)
                
                if len(music_data) >= total_tracks:
                    break
            
            offset += limit

    df = pd.DataFrame(music_data)
    return df

def calculate_weighted_popularity(release_date):
    release_date = datetime.strptime(release_date, '%Y-%m-%d')
    time_span = datetime.now() - release_date
    weight = 1 / (time_span.days + 1)
    return weight

"""def content_based_recommendations(music_df, input_song_name, num_recommendations=5):
    if input_song_name not in music_df['Track_Name'].values:
        return pd.DataFrame()

    input_song_index = music_df[music_df['Track_Name'] == input_song_name].index[0]
    scaler = MinMaxScaler()
    music_features = music_df[['Danceability', 'Energy', 'Key', 
                               'Loudness', 'Mode', 'Speechiness', 'Acousticness',
                               'Instrumentalness', 'Liveness', 'Valence', 'Tempo']].values
    music_features_scaled = scaler.fit_transform(music_features)
    similarity_scores = cosine_similarity([music_features_scaled[input_song_index]], music_features_scaled)
    similar_song_indices = similarity_scores.argsort()[0][::-1][1:num_recommendations + 1]
    content_based_recommendations = music_df.iloc[similar_song_indices][['Track_Name', 'Artists', 'Album_Name', 'Release_Date', 'Popularity']]
    return content_based_recommendations


def hybrid_recommendations(input_song_name, music_df, music_features_scaled, num_recommendations=5, alpha=0.5):
    if input_song_name not in music_df['Track_Name'].values:
        print(f"'{input_song_name}' not found in the dataset. Please enter a valid song name.")
        return []

    # Get the index of the input song in the music DataFrame
    input_song_index = music_df[music_df['Track_Name'] == input_song_name].index[0]

    # Calculate the similarity scores based on music features (cosine similarity)
    similarity_scores = cosine_similarity([music_features_scaled[input_song_index]], music_features_scaled)

    # Get the indices of the most similar songs
    similar_song_indices = similarity_scores.argsort()[0][::-1][1:num_recommendations + 1]

    # Get the recommendations based on content-based filtering
    content_based_rec = music_df.iloc[similar_song_indices][['Track_Name', 'Artists', 'Album_Name', 'Release_Date', 'Popularity']]

    # Get the popularity score of the input song
    popularity_score = music_df.loc[input_song_index, 'Popularity']

    # Calculate the weighted popularity score
    weighted_popularity_score = popularity_score * calculate_weighted_popularity(music_df.loc[input_song_index, 'Release_Date'])

    # Combine content-based and popularity-based recommendations based on weighted popularity
    hybrid_recommendations = pd.concat([content_based_rec, pd.DataFrame([{
        'Track_Name': input_song_name,
        'Artists': music_df.loc[input_song_index, 'Artists'],
        'Album_Name': music_df.loc[input_song_index, 'Album_Name'],
        'Release_Date': music_df.loc[input_song_index, 'Release_Date'],
        'Popularity': weighted_popularity_score
    }])], ignore_index=True)

    # Sort the hybrid recommendations based on weighted popularity score
    hybrid_recommendations = hybrid_recommendations.sort_values(by='Popularity', ascending=False)

    # Remove the input song from the recommendations
    hybrid_recommendations = hybrid_recommendations[hybrid_recommendations['Track_Name'] != input_song_name]

    return hybrid_recommendations.to_dict('records')"""
def content_based_recommendations(music_df, input_song_name, num_recommendations=5):
    input_song_name_lower = input_song_name.lower()  # Convert input to lowercase
    if input_song_name_lower not in music_df['Track_Name'].str.lower().values:
        return pd.DataFrame()

    input_song_index = music_df[music_df['Track_Name'].str.lower() == input_song_name_lower].index[0]
    scaler = MinMaxScaler()
    music_features = music_df[['Danceability', 'Energy', 'Key', 
                               'Loudness', 'Mode', 'Speechiness', 'Acousticness',
                               'Instrumentalness', 'Liveness', 'Valence', 'Tempo']].values
    music_features_scaled = scaler.fit_transform(music_features)
    similarity_scores = cosine_similarity([music_features_scaled[input_song_index]], music_features_scaled)
    similar_song_indices = similarity_scores.argsort()[0][::-1][1:num_recommendations + 1]
    content_based_recommendations = music_df.iloc[similar_song_indices][['Track_Name', 'Artists', 'Album_Name', 'Release_Date', 'Popularity']]
    return content_based_recommendations

def hybrid_recommendations(input_song_name, music_df, music_features_scaled, num_recommendations=5, alpha=0.5):
    input_song_name_lower = input_song_name.lower()  # Convert input to lowercase
    if input_song_name_lower not in music_df['Track_Name'].str.lower().values:
        print(f"'{input_song_name}' not found in the dataset. Please enter a valid song name.")
        return []

    # Get the index of the input song in the music DataFrame
    input_song_index = music_df[music_df['Track_Name'].str.lower() == input_song_name_lower].index[0]

    # Calculate the similarity scores based on music features (cosine similarity)
    similarity_scores = cosine_similarity([music_features_scaled[input_song_index]], music_features_scaled)

    # Get the indices of the most similar songs
    similar_song_indices = similarity_scores.argsort()[0][::-1][1:num_recommendations + 1]

    # Get the recommendations based on content-based filtering
    content_based_rec = music_df.iloc[similar_song_indices][['Track_Name', 'Artists', 'Album_Name', 'Release_Date', 'Popularity']]

    # Get the popularity score of the input song
    popularity_score = music_df.loc[input_song_index, 'Popularity']

    # Calculate the weighted popularity score
    weighted_popularity_score = popularity_score * calculate_weighted_popularity(music_df.loc[input_song_index, 'Release_Date'])

    # Combine content-based and popularity-based recommendations based on weighted popularity
    hybrid_recommendations = pd.concat([content_based_rec, pd.DataFrame([{
        'Track_Name': input_song_name,
        'Artists': music_df.loc[input_song_index, 'Artists'],
        'Album_Name': music_df.loc[input_song_index, 'Album_Name'],
        'Release_Date': music_df.loc[input_song_index, 'Release_Date'],
        'Popularity': weighted_popularity_score
    }])], ignore_index=True)

    # Sort the hybrid recommendations based on weighted popularity score
    hybrid_recommendations = hybrid_recommendations.sort_values(by='Popularity', ascending=False)

    # Remove the input song from the recommendations
    hybrid_recommendations = hybrid_recommendations[hybrid_recommendations['Track_Name'].str.lower() != input_song_name_lower]

    return hybrid_recommendations.to_dict('records')