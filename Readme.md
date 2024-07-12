# Music Recommendation System

![Python](https://img.shields.io/badge/Python-3.12.4-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-5.0.7-green?style=flat-square&logo=django)
![Spotipy](https://img.shields.io/badge/Spotipy-2.19.0-blue?style=flat-square&logo=spotify)
![GitHub](https://img.shields.io/badge/GitHub-Repo-blue?style=flat-square&logo=github)

This project implements a music recommendation system using the Spotify API, incorporating content-based and hybrid recommendation algorithms.

## Features

- **Content-Based Filtering:** Recommends songs based on similarity in music features.
- **Hybrid Filtering:** Combines content-based and popularity-based recommendations.
- **API Integration:** Utilizes the Spotify API for fetching music data and features.
- **Web Application:** Integrated with Django for a user-friendly interface.

## Installation

1. Clone the repository:

   
   ```console
   git clone https://github.com/your-username/music-recommendation-system.git
   cd music-recommendation-system

   ```
2. Install dependencies:

```console
pip install -r requirements.txt
Set up environment variables for Spotify API credentials (CLIENT_ID and CLIENT_SECRET).
```

3. Set up environment variables for Spotify API credentials (CLIENT_ID and CLIENT_SECRET).

## Usage

1. Run the Django development server:

```console

python manage.py runserver
```

2. Open your web browser and go to http://localhost:8000/ to access the application.