from flask import Blueprint, request, jsonify
from .models import (
    db,
    User,
    Location,
    Facility,
    Road,
    Diary,
)  # 确保从models.py正确导入模型
from werkzeug.security import check_password_hash
from .utils import a_star

api = Blueprint("api", __name__)


@api.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "请提供用户名和密码"}), 400

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        # 登录成功
        # 在实际应用中，这里应该返回一个token
        return jsonify({"message": "登录成功", "username": username}), 200
    else:
        # 登录失败
        return jsonify({"error": "无效的用户名或密码"}), 401


@api.route("/recommendations", methods=["GET"])
def get_recommendations():
    sorted_locations = sorted(Location.name, key=lambda x: x.popularity, reverse=True);

    # 假设我们只推荐前3个地点
    recommendations = sorted_locations[:3]

    return jsonify(recommendations), 200


@api.route('/route_planning', methods=['POST'])
def route_planning():
    data = request.get_json()
    start = data['start']
    end = data['end']
    
    # 假设我们已经有了一个图结构 'graph'，这里只是为了演示
    graph = {...}
    
    path, cost = a_star(graph, start, end)
    if path:
        return jsonify({'path': path, 'cost': cost}), 200
    else:
        return jsonify({'error': "未找到路径"}), 404


@api.route("/facilities", methods=["GET"])
def search_facilities():
    # 从查询字符串获取参数
    name = request.args.get('name')
    category = request.args.get('category')
    # 假设用户可以根据location_id搜索
    location_id = request.args.get('location_id')

    # 构建基础查询
    query = Facility.query

    # 根据提供的参数动态添加过滤条件
    if name:
        query = query.filter(Facility.name.ilike(f'%{name}%'))
    if category:
        query = query.filter(Facility.category.ilike(f'%{category}%'))
    if location_id:
        query = query.filter_by(location_id=location_id)

    # 执行查询
    facilities = query.all()

    # 将查询结果序列化为字典列表
    facilities_list = [{
        'id': facility.id,
        'name': facility.name,
        'category': facility.category,
        'coordinates': facility.coordinates,
        'location_id': facility.location_id
    } for facility in facilities]

    return jsonify(facilities_list), 200


@api.route("/diaries", methods=["GET", "POST"])
def manage_diaries():
    if request.method == "POST":
        # 从请求体中获取数据
        user_id = request.json.get("user_id")
        location_id = request.json.get("location_id")
        content = request.json.get("content")

        if not user_id or not location_id or not content:
            return jsonify({"error": "缺少必要的日记信息"}), 400

        # 创建新的日记实例，popularity和rating使用默认值
        new_diary = Diary(user_id=user_id, location_id=location_id, content=content)
        db.session.add(new_diary)
        db.session.commit()

        return jsonify({"message": "游学日记创建成功", "diary_id": new_diary.id}), 201
    else:
        # 查询所有游学日记，包括它们的热度和评分
        diaries = Diary.query.all()
        diaries_list = [
            {
                "id": diary.id,
                "user_id": diary.user_id,
                "location_id": diary.location_id,
                "content": diary.content,
                "popularity": diary.popularity,
                "rating": diary.rating,
            }
            for diary in diaries
        ]

        return jsonify(diaries_list), 200
