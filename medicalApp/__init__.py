from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_babelex import Babel
from urllib.parse import quote
from flask_login import LoginManager
from datetime import date


app = Flask(__name__)
app.secret_key = '0123456789!@#$%^&*'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/medicalappdb?charset=utf8mb4" % quote(
    'Nhat@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

login = LoginManager(app=app)


# babel = Babel(app)


# @babel.localeselector
# def get_locale():
#     return 'vi'