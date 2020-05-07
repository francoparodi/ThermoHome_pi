from flask import Flask, render_template
from config import Config

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    from flaskr.models import db
    db.init_app(app)

    from flaskr.routes import socketio
    socketio.init_app(app)

    from flaskr.routes import view
    app.register_blueprint(view)

    return app