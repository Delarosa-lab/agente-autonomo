from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Importando os modelos corretamente
from backend.models import Channel, Task, Content, Finance, Base

app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///autonomous_agent.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Inicializa o banco de dados
with app.app_context():
    engine = db.engine
    Base.metadata.create_all(engine)

# Rota inicial
@app.route('/')
def index():
    return jsonify({
        "message": "Agente Autônomo ativo e rodando!",
        "status": "online",
        "time": datetime.utcnow().isoformat()
    })

# Criar novo canal
@app.route('/channels', methods=['POST'])
def create_channel():
    data = request.get_json()
    new_channel = Channel(name=data['name'], niche=data['niche'])
    db.session.add(new_channel)
    db.session.commit()
    return jsonify({"message": "Canal criado com sucesso!"}), 201

# Listar canais
@app.route('/channels', methods=['GET'])
def list_channels():
    channels = db.session.query(Channel).all()
    output = []
    for c in channels:
        output.append({
            "id": c.id,
            "name": c.name,
            "niche": c.niche,
            "subscribers": c.subscribers,
            "created_at": c.created_at.isoformat()
        })
    return jsonify(output)

# Criar tarefa (shorts, vídeos, e-books)
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    new_task = Task(channel_id=data['channel_id'], type=data['type'])
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Tarefa criada com sucesso!"}), 201

# Listar tarefas
@app.route('/tasks', methods=['GET'])
def list_tasks():
    tasks = db.session.query(Task).all()
    output = []
    for t in tasks:
        output.append({
            "id": t.id,
            "channel_id": t.channel_id,
            "type": t.type,
            "status": t.status,
            "created_at": t.created_at.isoformat()
        })
    return jsonify(output)

# Atualizar status de tarefa
@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = db.session.query(Task).get(id)
    if not task:
        return jsonify({"error": "Tarefa não encontrada"}), 404
    data = request.get_json()
    task.status = data.get('status', task.status)
    db.session.commit()
    return jsonify({"message": "Status atualizado com sucesso!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
