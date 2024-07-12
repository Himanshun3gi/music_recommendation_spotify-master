from django import forms

class PlaylistForm(forms.Form):
    playlist_id = forms.CharField(label='Spotify Playlist ID', max_length=50)

class SongForm(forms.Form):
    song_name = forms.CharField(label='Song Name', max_length=100)