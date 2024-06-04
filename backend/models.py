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


class TravelNote(db.Model):
    __tablename__ = "travel_note"
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(
        db.Integer, db.ForeignKey("destination.id"), nullable=False
    )
    title = db.Column(db.String(120), nullable=False)  # 游记标题
    content = db.Column(db.Text, nullable=False)
    views = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0)
    rate_cnt = db.Column(db.Integer, default=0)
    username = db.Column(db.String(120), nullable=False)  # 添加用户名字段

    destination = db.relationship(
        "Destination", backref=db.backref("travel_notes", lazy=True)
    )
