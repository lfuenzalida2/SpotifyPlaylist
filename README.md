# Spotify Playlist

This is a minimal app that let's you download a Spotify playlist via Youtube using only the URL of the playlist.

The dependencies and versions used are on the file <code>requirements.txt</code> and used Python 3.8.9 for this proyect and is stable.

## Usage

1) Clone the repository
2) Create a proyect on [Spotify Developers](https://developer.spotify.com/)
3) Add the .env with the credentials
4) Run <code>py -m venv env</code> to create a virtual enviroments
4) Run <code>pip install -r requirements.txt</code> to install the dependencies
5) Run <code>python main.py</code>
6) Insert the Spotify Playlist URL start the download

Once the download end, it will create a folder named <code>/songs</code> on the root of the repository with all the songs.

## .env

SPOTIFY_CLIENT_ID=Spotify proyect credentials<br>
SPOTIFY_CLIENT_SECRET=Spotify proyect credentials


### Terms and conditions
The author is not legally binded or responsable of the usage given to the tool
Dedicated to AVB