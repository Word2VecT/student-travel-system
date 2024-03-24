from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)

# 配置数据库
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "db", "travel_system.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 导入你的模型，以确保它们在Migrate对象创建之后被注册
from .models import User, Location, Facility, Road, Diary
from backend.api.routes import api as api_blueprint

app.register_blueprint(api_blueprint, url_prefix="/api")


@app.route("/")
def hello():
    return "Welcome to the Student Travel System API!"


if __name__ == "__main__":
    app.run(debug=True)
