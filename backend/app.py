import os
import zlib
import base64
import networkx as nx
import random
from config import Config
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # 允许所有域名的所有请求

db = SQLAlchemy(app)

UPLOAD_FOLDER = "/Users/tang/Pictures/travel"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


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

    # 解压缩内容
    notes_data = []
    for note in notes:
        try:
            decompressed_content = zlib.decompress(
                base64.b64decode(note.content)
            ).decode("utf-8")
        except Exception as e:
            decompressed_content = note.content  # 如果解压失败，保持原内容
        notes_data.append(
            {
                "id": note.id,
                "title": note.title,
                "content": decompressed_content,
                "views": note.views,
                "rating": note.rating,
                "username": note.username,
            }
        )

    return jsonify(notes_data)


@app.route("/destination/<int:id>/notes", methods=["POST"])
def add_travel_note(id):
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    username = data.get("username")

    # 压缩内容
    compressed_content = base64.b64encode(
        zlib.compress(content.encode("utf-8"))
    ).decode("utf-8")

    note = TravelNote(
        destination_id=id, title=title, content=compressed_content, username=username
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


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def upload():
    if "uploadedImage" not in request.files:
        return jsonify({"errno": 1, "message": "没有找到文件"})

    file = request.files["uploadedImage"]
    if file.filename == "":
        return jsonify({"errno": 1, "message": "没有选择文件"})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return jsonify(
            {"errno": 0, "data": {"url": f"http://127.0.0.1:5000/uploads/{filename}"}}
        )

    return jsonify({"errno": 1, "errmsg": "File not allowed"})


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/calculate-route", methods=["POST"])
def calculate_route():
    data = request.get_json()
    length = int(data["length"])
    cost = [[int(x) for x in sublist] for sublist in data["cost"]]

    G = nx.DiGraph()

    for i in range(length):
        for j in range(length):
            if i != j:  # 避免自环
                G.add_edge(i, j, weight=cost[i][j])

    # 使用networkx的近似算法求解TSP，指定起点
    tsp_path = nx.approximation.traveling_salesman_problem(G, cycle=False)

    if 0 in tsp_path:
        zero_index = tsp_path.index(0)
        tsp_path = tsp_path[zero_index:] + tsp_path[:zero_index]

    tsp_path.append(0)

    return jsonify({"path": tsp_path})


@app.route("/generate_image", methods=["POST"])
def generate_image():
    data = request.get_json()
    content = data.get("content")

    # 调用 mobius.py 脚本生成图片
    os.system(f"python3 mobius.py '{content}'")

    # 假设生成的图片保存在 'generated_image.png'
    filename = "generated_image.png"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(filepath):
        image_url = f"http://127.0.0.1:5000/uploads/{filename}"
        return jsonify({"success": True, "imageUrl": image_url})
    else:
        return jsonify({"success": False, "message": "生成图片失败"})


@app.route("/generate_video", methods=["POST"])
def generate_video():
    data = request.get_json()
    content = data.get("content", "")
    if not content:
        return jsonify({"success": False, "message": "内容不能为空"}), 400

    command = f'python animate_diff_lightning.py "{content}"'
    os.system(command)

    filename = "animation.gif"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(filepath):
        video_url = f"http://127.0.0.1:5000/uploads/{filename}"
        return jsonify({"success": True, "videoUrl": video_url})
    else:
        return jsonify({"success": False, "message": "生成视频失败"})


def calculate_similarity():
    with app.app_context():
        destinations = Destination.query.all()
        contents = [destination.description for destination in destinations]
        ids = [destination.id for destination in destinations]

        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(contents)
        cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

        return ids, cosine_similarities


destination_ids, destination_similarities = calculate_similarity()


@app.route("/destination/<int:id>/similar", methods=["GET"])
def get_similar_destinations(id):
    try:
        idx = destination_ids.index(id)
    except ValueError:
        return jsonify([])

    sim_scores = list(enumerate(destination_similarities[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:7]  # 取前5个相似的景点

    similar_destinations = []
    for i in sim_scores:
        similar_destination = Destination.query.get(destination_ids[i[0]])
        similar_destinations.append(
            {
                "id": similar_destination.id,
                "name": similar_destination.name,
                "popularity": similar_destination.popularity,
                "rating": similar_destination.rating,
                "price": similar_destination.price,
                "category": similar_destination.category,
                "region": similar_destination.region,
                "address": similar_destination.address,
                "description": similar_destination.description,
            }
        )

    return jsonify(similar_destinations)


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
