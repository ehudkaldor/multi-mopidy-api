from flask import Flask, render_template
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def hello():
    # return "Hello pimps!"
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    print('Client connected')
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
    emit('my response', {'data': 'Disconnected'})


@socketio.on('my_event', namespace='/test')
def test_message(message):
  print(message)
  emit('my response', {'data' : 'screw you'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
