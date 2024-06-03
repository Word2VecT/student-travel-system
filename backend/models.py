from app import db


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Destination(db.Model):
    __tablename__ = "destination"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    popularity = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(10), nullable=True)
    region = db.Column(db.String(10), nullable=False)  # 地区字段
    address = db.Column(db.String(255), nullable=False)  # 详细地址字段
    description = db.Column(db.Text, nullable=False)
