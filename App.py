from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
import speech_recognition as sr
import pyttsx3
import random  # For creativity

# Initialize Flask app and Socket.IO
app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database, migration, and Socket.IO
db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)

# Initialize recognizer and TTS engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Define a Command model for saving user interactions
class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    command_text = db.Column(db.String(255), nullable=False)
    response_text = db.Column(db.String(255), nullable=False)

# User database for recognition
user_data = {
    "0308025349802": "Sphiwe"  # Owner ID
}

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Voice command processing
@app.route('/voice-command', methods=['POST'])
def voice_command():
    data = request.get_json()
    command_text = data.get('command', '')
    user_id = data.get('user_id', '')

    user_name = user_data.get(user_id, "Unknown User")
    if user_name == "Unknown User":
        response_text = "Unrecognized ID. Please provide valid identification."
    else:
        if "hello" in command_text.lower():
            response_text = f"Hello {user_name}, how can I assist you today?"
        elif "identify" in command_text.lower():
            response_text = f"You are identified as {user_name}."
        elif "joke" in command_text.lower():  # Example of creative response
            response_text = random.choice([
                "Why don’t scientists trust atoms? Because they make up everything!",
                "Why did the scarecrow win an award? Because he was outstanding in his field!",
                "What do you call fake spaghetti? An impasta!"
            ])
        else:
            response_text = f"Saliver heard: {command_text}"

    # Speak the response
    engine.say(response_text)
    engine.runAndWait()

    # Save the command and response to the database
    new_command = Command(command_text=command_text, response_text=response_text)
    db.session.add(new_command)
    db.session.commit()

    return jsonify({"response": response_text})

# Remote control endpoint with expanded commands
@app.route('/remote-control', methods=['POST'])
def remote_control():
    data = request.get_json()
    command_text = data.get('command', '').lower()

    if "turn on lights" in command_text:
        response_text = "Turning on the lights."
    elif "turn off lights" in command_text:
        response_text = "Turning off the lights."
    elif "lock the door" in command_text:
        response_text = "Locking the door."
    elif "unlock the door" in command_text:
        response_text = "Unlocking the door."
    elif "play music" in command_text:
        response_text = "Playing your favorite playlist."
    else:
        response_text = "Command not recognized for remote control."

    # Emit response back to front end in real-time
    socketio.emit('remote_control_response', {"response": response_text})

    return jsonify({"response": response_text})

# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
