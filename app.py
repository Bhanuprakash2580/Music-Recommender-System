import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import pandas as pd

st.set_page_config(layout="wide")

# --- LOGIN SYSTEM ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login(username, password):
    if username == "Divya" and password == "12345":
        st.session_state.logged_in = True
    else:
        st.error("Invalid username or password")

def logout():
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            login(username, password)
    st.stop()

# --- MAIN APP ---
st.markdown("<h1 style='text-align: center; color: #1DB954;'>🎵 Music Recommender System</h1>", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/727/727245.png", width=80)
    st.title("Navigation")
    nav_option = st.radio(
        "Choose an option:",
        [
            "🎶 Recommend Songs",
            "🏆 Top 20 Popular Songs",
            "📄 Show Dataset"
        ]
    )
    st.markdown("---")
    if st.button("🔓 Logout"):
        logout()
        st.rerun()

load_dotenv()
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")
    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        return album_cover_url
    else:
        return "https://i.pcmag.com/imagery/articles/01uUtdvBJd0VNaZlw5H1Qid-1..v1723632784.jpg"

def recommend(song, n=5):
    try:
        index = music[music['song'] == song].index[0]
    except IndexError:
        return [], []
    distances = sorted(list(enumerate(similarity[index])), key=lambda x: x[1], reverse=True)
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:n+1]:
        artist = music.iloc[i[0]].artist
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].song, artist))
        recommended_music_names.append(music.iloc[i[0]].song)
    return recommended_music_names, recommended_music_posters

# --- DATA LOADING ---
music = pickle.load(open("D:\\Divya\\Music-Recommender-System-with-Spotify-million-dataset-main\\df", "rb"))
similarity = pickle.load(open("D:\\Divya\\Music-Recommender-System-with-Spotify-million-dataset-main\\similarity", "rb"))
music_list = music['song'].values

# --- MAIN CONTENT ---
if nav_option == "🎶 Recommend Songs":
    st.header("🎶 Get Song Recommendations")
    selected_song = st.selectbox("Type or select a song from the dropdown", music_list)
    if st.button("Show Recommendation"):
        with st.spinner("Fetching recommendations..."):
            recommended_music_names, recommended_music_posters = recommend(selected_song, n=5)
        if not recommended_music_names:
            st.error("Sorry, no recommendations found for this song.")
        else:
            st.subheader("Top 5 Recommended Songs")
            cols = st.columns(5)
            for idx, (name, poster) in enumerate(zip(recommended_music_names, recommended_music_posters)):
                col = cols[idx % len(cols)]
                col.text(name)
                col.image(poster)

elif nav_option == "🏆 Top 20 Popular Songs":
    st.header("🏆 Top 20 Popular Songs in the Dataset")
    top_20 = music['song'].value_counts().head(20)
    top_20_songs = top_20.index.tolist()
    top_20_artists = [music[music['song'] == song]['artist'].iloc[0] for song in top_20_songs]
    st.write("Top 20 Songs with Album Covers:")
    cols = st.columns(5)
    for idx, (song, artist) in enumerate(zip(top_20_songs, top_20_artists)):
        col = cols[idx % len(cols)]
        col.text(song)
        col.image(get_song_album_cover_url(song, artist))

elif nav_option == "📄 Show Dataset":
    st.header("🎼 Full Dataset")
    st.dataframe(music)

st.markdown("---")
st.markdown("<div style='text-align: center;'>"
            "<b>Music Recommender System</b> | Built with ❤️ using Streamlit"
            "</div>", unsafe_allow_html=True)