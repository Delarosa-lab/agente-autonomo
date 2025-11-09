# backend/youtube_integration.py

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import base64
import tempfile

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    """Autentica com o YouTube e salva token para reuso."""
    creds = None

    # Verifica se há token salvo
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)

    # Se não houver credenciais válidas, pede login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Lê credenciais do arquivo client_secrets.json
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES)
            creds = flow.run_local_server(port=8080)

        # Salva token para reutilização
        with open("token.pkl", "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title, description, tags=None, privacy="public"):
    """Envia um vídeo para o canal autenticado."""
    youtube = get_authenticated_service()

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": privacy
        }
    }

    media_file = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    upload_request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = upload_request.execute()
    print(f"✅ Vídeo enviado com sucesso: https://youtu.be/{response['id']}")
    return response["id"]

if __name__ == "__main__":
    # Teste rápido (troque o caminho por um vídeo real)
    upload_video("video_teste.mp4", "Vídeo de Teste", "Enviado automaticamente!")
