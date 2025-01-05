import json
from threading import Thread
from flask import Flask
from flask_login import LoginManager
from auth import auth
from models import db, User
from addn_data import broadcast_additional_info_updates
from modify_battery_data import publish_battery_data
from publisher import publish_data

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth)

# Function to start battery data publishing
def start_battery_data_publishing():
    publish_battery_data()

# Function to start MQTT publishing
def start_publishing():
    publish_data()

# Main function
if __name__ == "__main__":
    # Start the battery data publishing thread
    battery_thread = Thread(target=start_battery_data_publishing)
    battery_thread.daemon = True
    battery_thread.start()

    # Start the MQTT publishing thread
    mqtt_thread = Thread(target=start_publishing)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # Initialize the database if necessary
    with app.app_context():
        db.create_all()

    try:
        # Start the Flask app
        app.run(debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received - sending final broadcast...")
        broadcast_additional_info_updates()
        print("Final broadcast completed")
