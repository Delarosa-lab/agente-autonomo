# backend/scheduler.py

import time
import random
from datetime import datetime
from backend.models import VideoTask, get_engine, create_tables
from backend.youtube_integration import upload_video
from sqlalchemy.orm import sessionmaker

# Cria engine e sessão
engine = get_engine()
Session = sessionmaker(bind=engine)
create_tables()

def gerar_titulo_e_descricao(video_type, niche):
    """Gera título e descrição simples com base no tipo de vídeo."""
    if video_type == "short":
        title = f"Dica rápida sobre {niche} #{random.randint(100,999)}"
        description = f"Confira esta dica essencial de {niche}! 💡"
    else:
        title = f"Guia completo sobre {niche} ({datetime.utcnow().year})"
        description = f"Neste vídeo, exploramos {niche} em detalhes. 🚀"
    return title, description

def processar_videos():
    """Procura vídeos pendentes e faz o upload."""
    session = Session()
    pendentes = session.query(VideoTask).filter_by(status="pending").all()

    for task in pendentes:
        title, description = gerar_titulo_e_descricao(task.video_type, task.niche)
        print(f"🎬 Enviando vídeo: {title}")

        # Aqui entraria a parte de renderização real
        file_path = f"videos/{task.video_type}_{task.id}.mp4"

        try:
            video_id = upload_video(file_path, title, description)
            task.status = "uploaded"
            task.updated_at = datetime.utcnow()
            session.commit()
            print(f"✅ Vídeo {video_id} enviado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao enviar vídeo {task.id}: {e}")
            task.status = "error"
            session.commit()

    session.close()

def iniciar_agendador(intervalo_minutos=60):
    """Roda continuamente, verificando novas tarefas a cada X minutos."""
    while True:
        print(f"\n⏰ Verificando novas tarefas ({datetime.now().strftime('%H:%M:%S')})")
        processar_videos()
        time.sleep(intervalo_minutos * 60)

if __name__ == "__main__":
    print("🚀 Agendador iniciado!")
    iniciar_agendador(intervalo_minutos=30)
