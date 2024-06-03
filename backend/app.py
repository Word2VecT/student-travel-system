from config import Config
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # 允许所有域名的所有请求

db = SQLAlchemy(app)


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


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "message": "用户名已存在"})

    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True, "message": "用户注册成功"})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return jsonify({"success": True, "message": "登录成功"})
    else:
        return jsonify({"success": False, "message": "用户名或密码错误"})


@app.route("/recommendations", methods=["GET"])
def recommendations():
    sort_by = request.args.get("sortBy", "热度")
    categories = request.args.get("categories", "all")
    regions = request.args.get("regions", "all")
    query = request.args.get("query", "")

    query_obj = Destination.query

    if categories != "all":
        categories_list = categories.split(",")
        query_obj = query_obj.filter(Destination.category.in_(categories_list))

    if regions != "all":
        regions_list = regions.split(",")
        query_obj = query_obj.filter(Destination.region.in_(regions_list))

    if query:
        query_obj = query_obj.filter(Destination.name.like(f"%{query}%"))

    # Clear any existing order_by clauses
    query_obj = query_obj.order_by(None)

    # Apply sorting
    if sort_by == "评分":
        query_obj = query_obj.order_by(Destination.rating.desc())
    elif sort_by == "价格":
        query_obj = query_obj.order_by(Destination.price)
    else:  # 默认是 "热度"
        query_obj = query_obj.order_by(Destination.popularity.desc())

    recommendations = query_obj.limit(12).all()

    recommendations_data = [
        {
            "id": destination.id,
            "name": destination.name,
            "popularity": destination.popularity,
            "rating": destination.rating,
            "price": destination.price,
            "category": destination.category,
            "region": destination.region,
            "address": destination.address,
            "description": destination.description,
        }
        for destination in recommendations
    ]

    return jsonify(recommendations_data)


@app.route("/destination/<int:id>", methods=["GET"])
def get_destination(id):
    destination = Destination.query.get_or_404(id)
    return jsonify(
        {
            "id": destination.id,
            "name": destination.name,
            "popularity": destination.popularity,
            "rating": destination.rating,
            "price": destination.price,
            "category": destination.category,
            "region": destination.region,
            "address": destination.address,
            "description": destination.description,
        }
    )


@app.route("/destination/<int:id>/notes", methods=["GET"])
def get_travel_notes(id):
    sort_by = request.args.get("sortBy", "views")
    search_query = request.args.get("searchQuery", "")

    query = TravelNote.query.filter_by(destination_id=id)

    if search_query:
        query = query.filter(
            (TravelNote.title.like(f"%{search_query}%"))
            | (TravelNote.content.like(f"%{search_query}%"))
        )

    if sort_by == "评分":
        query = query.order_by(TravelNote.rating.desc())
    else:  # 默认是 "浏览量"
        query = query.order_by(TravelNote.views.desc())

    notes = query.all()

    return jsonify(
        [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "views": note.views,
                "rating": note.rating,
                "username": note.username,
            }
            for note in notes
        ]
    )


@app.route("/destination/<int:id>/notes", methods=["POST"])
def add_travel_note(id):
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    username = data.get("username")

    note = TravelNote(
        destination_id=id, title=title, content=content, username=username
    )
    db.session.add(note)
    db.session.commit()

    return jsonify({"success": True, "message": "游记发布成功"})


@app.route("/note/<int:id>/increment_views", methods=["POST"])
def increment_views(id):
    note = TravelNote.query.get_or_404(id)
    note.views += 1
    db.session.commit()
    return jsonify({"success": True})


@app.route("/note/<int:id>/rate", methods=["POST"])
def rate_travel_note(id):
    note = TravelNote.query.get_or_404(id)
    data = request.get_json()
    new_rating = data.get("rating")
    if new_rating is not None:
        # 更新评分次数
        note.rate_cnt += 1
        # 计算新的平均值
        if note.rating is not None:
            note.rating = (
                note.rating * (note.rate_cnt - 1) + new_rating
            ) / note.rate_cnt
        else:
            note.rating = new_rating
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "无效的评分"})


if __name__ == "__main__":
    app.run(debug=True)
