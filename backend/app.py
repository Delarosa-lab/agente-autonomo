# backend/app.py
from flask import Flask, request, jsonify, send_file, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import logging

# importe models e tasks do mesmo pacote
from models import Base, Channel, Task, Content, Finance
import settings
from tasks import create_planner_job, execute_task
from finance import FinanceTracker
from flask import abort

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = settings.SECRET_KEY
logging.basicConfig(level=logging.INFO)

# DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
# cria tabelas (em dev; em prod use migrations)
Base.metadata.create_all(bind=engine)

# Simple admin auth (header X-ADMIN-TOKEN) — em produção use OAuth2/SSO
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'admin-token')

def admin_required(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get('X-ADMIN-TOKEN')
        if token != ADMIN_TOKEN:
            return jsonify({'error':'unauthorized'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status':'ok'}), 200

@app.route('/channels', methods=['POST'])
@admin_required
def create_channel():
    data = request.json
    db = SessionLocal()
    # enforce max channels
    from sqlalchemy import func
    cnt = db.query(func.count(Channel.id)).scalar()
    if cnt >= settings.MAX_CHANNELS:
        return jsonify({'error':'max channels reached'}), 400
    ch = Channel(
        name=data.get('name'),
        youtube_client_secrets=data.get('client_secrets_path'),
        youtube_token_file=data.get('token_file_path'),
        description=data.get('description','')
    )
    db.add(ch); db.commit(); db.refresh(ch)
    return jsonify({'id':ch.id,'name':ch.name})

@app.route('/channels', methods=['GET'])
@admin_required
def list_channels():
    db = SessionLocal()
    channels = db.query(Channel).all()
    out = [{'id':c.id,'name':c.name,'active':c.active,'description':c.description} for c in channels]
    return jsonify(out)

@app.route('/objectives', methods=['POST'])
@admin_required
def create_objective():
    """Create high-level objective like '1 long every 3 days + 5 shorts/d' for a channel"""
    data = request.json
    channel_id = data.get('channel_id')
    objective = data.get('objective')
    db = SessionLocal()
    ch = db.query(Channel).get(channel_id)
    if not ch:
        return jsonify({'error':'channel not found'}), 404
    job = create_planner_job.delay(channel_id, objective)
    return jsonify({'scheduled':True,'job_id': str(job.id)})

@app.route('/tasks', methods=['GET'])
@admin_required
def list_tasks():
    db = SessionLocal()
    tasks = db.query(Task).order_by(Task.created_at.desc()).limit(200).all()
    out = []
    for t in tasks:
        out.append({'id':t.id,'type':t.type,'channel_id':t.channel_id,'status':t.status,'meta':t.meta})
    return jsonify(out)

@app.route('/tasks/<int:task_id>/approve', methods=['POST'])
@admin_required
def approve_task(task_id):
    db = SessionLocal()
    t = db.query(Task).get(task_id)
    if not t:
        return jsonify({'error':'task not found'}), 404
    # marcar como pendente (worker irá processar)
    t.status = 'pending'
    db.commit()
    # opcional: enfileirar execução imediata
    execute_task.delay(task_id)
    return jsonify({'ok':True})

@app.route('/contents/<int:content_id>/download', methods=['GET'])
@admin_required
def download_content(content_id):
    db = SessionLocal()
    c = db.query(Content).get(content_id)
    if not c:
        return jsonify({'error':'not found'}),404
    # segurança: verifique path se necessário
    try:
        return send_file(c.storage_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview/<int:content_id>', methods=['GET'])
@admin_required
def preview_content(content_id):
    # renderiza template simples com player que chama /contents/<id>/download
    return render_template('preview.html', content_id=content_id, approve_url=f"/tasks/{content_id}/approve")

@app.route('/finance', methods=['GET'])
@admin_required
def get_finance():
    db = SessionLocal()
    entries = db.query(Finance).order_by(Finance.ts.desc()).limit(100).all()
    out = [{'ts':e.ts.isoformat(),'amount':e.amount,'source':e.source,'reinvest':e.reinvest,'net':e.net} for e in entries]
    return jsonify(out)

# internal endpoint for tests: upload mock content (admin only)
@app.route('/internal/upload-mock', methods=['POST'])
@admin_required
def upload_mock():
    # aceita um arquivo e cria Content row (usado para testes locais)
    if 'file' not in request.files:
        return jsonify({'error':'no file'}), 400
    f = request.files['file']
    filename = f.filename
    storage = os.getenv('STORAGE_PATH','storage')
    os.makedirs(storage, exist_ok=True)
    path = os.path.join(storage, filename)
    f.save(path)
    db = SessionLocal()
    # create a dummy content entry (channel_id must be provided via form)
    channel_id = request.form.get('channel_id')
    if not channel_id:
        return jsonify({'error':'channel_id required'}), 400
    c = Content(task_id=None, channel_id=int(channel_id), type='mock', storage_path=path, status='pending_approval')
    db.add(c); db.commit()
    return jsonify({'ok':True,'content_id':c.id,'path':path})

if __name__ == '__main__':
    # roda para desenvolvimento
    app.run(host='0.0.0.0', port=int(os.getenv('PORT',5000)))

