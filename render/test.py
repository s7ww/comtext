from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
import string

app = Flask(__name__)
socketio = SocketIO(app)

# Store sessions and users
sessions = {}

# Generate a random session ID
def generate_session_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('create_session')
def handle_create_session():
    session_id = generate_session_id()
    sessions[session_id] = []  # Create a new session
    emit('create_session', {'session_id': session_id}, broadcast=False)  # Send session ID back to the client

@socketio.on('join_session')
def handle_join_session(data):
    session_id = data['session_id']
    if session_id in sessions:
        sessions[session_id].append(request.sid)  # Add user to session
        emit('join_session', {'session_id': session_id}, room=request.sid)  # Inform the user they joined the session
    else:
        emit('error', {'msg': 'Session not found'}, room=request.sid)

@socketio.on('message')
def handle_message(data):
    session_id = data['session_id']
    msg = data['msg']
    if session_id in sessions:
        emit('message', {'msg': msg, 'session_id': session_id}, broadcast=True)
    else:
        emit('error', {'msg': 'Session not found'}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app,allow_unsafe_werkzeug=True)
