import flask
import flask_cors

from . import views
from .models import db


app = flask.Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.py")

flask_cors.CORS(app)

db.init_app(app)


@app.before_first_request
def before_first_request():
    db.create_all()
    with open("instance/data.sql", "r") as f:
        db.session.execute(f.read())
        db.session.commit()


app.register_blueprint(views.blueprint, url_prefix="/api")
