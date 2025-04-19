import os
import sys
import yt_dlp
import spotipy
import urllib.parse
import requests
import threading
import tkinter as tk
from tkinter import scrolledtext
from spotipy.oauth2 import SpotifyClientCredentials
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
import subprocess
import ttkbootstrap as ttk
from dotenv import load_dotenv

load_dotenv()

def recurso_path(rel_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS  # cuando se ejecuta como .exe
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, rel_path)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
))

# Carpeta destino de la música
carpeta_destino = os.path.join(os.getcwd(), "songs")
os.makedirs(carpeta_destino, exist_ok=True)

# Función para loggear en la interfaz
def log_message(message):
    text_log.insert(tk.END, message + "\n")
    text_log.yview(tk.END)

# Obtener canciones de una playlist de Spotify
def obtener_canciones_playlist(playlist_url):
    try:
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        results = sp.playlist_tracks(playlist_id)

        playlist_name = sp.playlist(playlist_id)["name"]
        canciones = []

        for item in results["items"]:
            track = item["track"]
            canciones.append({
                "titulo": track["name"],
                "artista": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "caratula": track["album"]["images"][0]["url"] if track["album"]["images"] else None
            })
        
        return canciones, playlist_name

    except spotipy.exceptions.SpotifyException:
        log_message(f"❌ URL de Spotify invalida")

# Buscar en YouTube
def buscar_en_youtube(query):
    query_string = urllib.parse.urlencode({"search_query": query})
    url = f"https://www.youtube.com/results?{query_string}"
    response = requests.get(url).text
    inicio = response.find('/watch?v=') + 9
    fin = response.find('"', inicio)

    return f"https://www.youtube.com/watch?v={response[inicio:fin]}"

# Descargar audio desde YouTube
def descargar_audio(url, nombre_archivo):
    ffmpeg_path = recurso_path('ffmpeg\\bin')
    print(ffmpeg_path)

    opciones = {
        'format': 'bestaudio/best',
        # 'outtmpl': os.path.join(carpeta_destino, nombre_archivo),
        'outtmpl': recurso_path(f'{carpeta_destino}\\{nombre_archivo}'),
        'ffmpeg_location': ffmpeg_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        ydl.download([url])

# Descargar carátula
def descargar_caratula(url, nombre_archivo):
    if url:
        response = requests.get(url)
        if response.status_code == 200:
            # ruta_caratula = os.path.join(carpeta_destino, f"{nombre_archivo}.jpg")
            ruta_caratula = recurso_path(f"{carpeta_destino}\\{nombre_archivo}.jpg")
            with open(ruta_caratula, "wb") as file:
                file.write(response.content)
            return ruta_caratula
    return None

# Agregar metadatos al MP3
def agregar_metadatos(mp3_path, titulo, artista, album, caratula_path):
    audio = MP3(mp3_path + ".mp3", ID3=ID3)
    audio.tags.add(TIT2(encoding=3, text=titulo))
    audio.tags.add(TPE1(encoding=3, text=artista))
    audio.tags.add(TALB(encoding=3, text=album))
    if caratula_path and os.path.exists(caratula_path):
        with open(caratula_path, "rb") as img:
            audio.tags.add(APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=img.read()
            ))
    audio.save()

# Descargar playlist
def descargar_playlist():
    playlist_url = entry_url.get()

    if not playlist_url:
        log_message("⚠️ Ingresa una URL de playlist de Spotify")
        return
    
    log_message("🔎 Obteniendo canciones...")
    canciones, playlist_name = obtener_canciones_playlist(playlist_url)
    log_message(f"✅ {len(canciones)} canciones encontradas.")
    
    global carpeta_destino
    carpeta_destino = os.path.join(os.getcwd(), f"songs\\{playlist_name}")
    os.makedirs(carpeta_destino, exist_ok=True)
    
    for cancion in canciones:
        nombre_archivo = f"{cancion['titulo']} - {cancion['artista']}"
        #  ruta_mp3 = os.path.join(carpeta_destino, nombre_archivo)
        ruta_mp3 = recurso_path(f"{carpeta_destino}\\{nombre_archivo}")
        
        if os.path.exists(ruta_mp3 + ".mp3"):
            log_message(f"✅ {nombre_archivo} ya existe. Saltando...")
            continue
        
        log_message(f"🔍 Buscando en YouTube: {cancion['titulo']} - {cancion['artista']}...")
        url_youtube = buscar_en_youtube(f"{cancion['titulo']} {cancion['artista']} audio")
        
        if "watch?v=" in url_youtube:
            log_message(f"🎵 Descargando: {cancion['titulo']}")
            descargar_audio(url_youtube, nombre_archivo)
            
            log_message("📀 Descargando carátula...")
            caratula_path = descargar_caratula(cancion["caratula"], nombre_archivo)
            
            log_message("📝 Agregando metadatos...")
            agregar_metadatos(ruta_mp3, cancion["titulo"], cancion["artista"], cancion["album"], caratula_path)
            
            if caratula_path and os.path.exists(caratula_path):
                os.remove(caratula_path)
        else:
            log_message(f"⚠️ No se encontró la canción: {cancion['titulo']}")
    
    log_message("✅ ¡Descarga completa!")

def abrir_carpeta():
    subprocess.Popen(f'explorer "{carpeta_destino}"' if os.name == 'nt' else f'xdg-open "{carpeta_destino}"', shell=True)


# Interfaz gráfica con Tkinter
root = ttk.Window(themename="darkly")
root.title("Spotify Playlist Downloader")
root.geometry("500x400")
root.iconbitmap(recurso_path("assets\\icon.ico"))

label = tk.Label(root, text="Ingresa la URL de la playlist de Spotify:")
label.pack(pady=5)

entry_url = tk.Entry(root, width=50)
entry_url.pack(pady=5)

btn_descargar = tk.Button(root, text="Descargar Playlist", command=lambda: threading.Thread(target=descargar_playlist).start())
btn_descargar.pack(pady=10)

btn_abrir_carpeta = tk.Button(root, text="Abrir Carpeta de Descargas", command=abrir_carpeta)
btn_abrir_carpeta.pack(pady=10)

text_log = scrolledtext.ScrolledText(root, width=60, height=15)
text_log.pack(pady=5)

root.mainloop()