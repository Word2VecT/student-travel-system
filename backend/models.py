from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


class Location(db.Model):
    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # '景区' or '校园'
    popularity = db.Column(db.Float, default=0.0)  # 游学热度
    rating = db.Column(db.Float, default=0.0)  # 评价


class Facility(db.Model):
    __tablename__ = "facilities"
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 如 '商店', '洗手间', etc.
    coordinates = db.Column(db.String(100), nullable=False)  # 存储为字符串，如 "x,y"


class Road(db.Model):
    __tablename__ = "roads"
    id = db.Column(db.Integer, primary_key=True)
    start_facility_id = db.Column(
        db.Integer, db.ForeignKey("facilities.id"), nullable=False
    )
    end_facility_id = db.Column(
        db.Integer, db.ForeignKey("facilities.id"), nullable=False
    )
    distance = db.Column(db.Float, nullable=False)  # 距离
    ideal_speed = db.Column(db.Float, nullable=False)  # 理想速度
    congestion_level = db.Column(db.Float, nullable=False)  # 拥挤度


class Diary(db.Model):
    __tablename__ = "diaries"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)  # 游学日记内容
    popularity = db.Column(db.Integer, default=0)  # 浏览量即热度
    rating = db.Column(db.Float, default=0.0)  # 评分
