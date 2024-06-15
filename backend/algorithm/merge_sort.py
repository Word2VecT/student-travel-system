import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

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


class BPlusTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.children = []

    def insert_non_full(self, key, value):
        if self.leaf:
            self.keys.append(key)
            self.children.append(value)
            self.keys, self.children = self.sort(self.keys, self.children)
        else:
            i = len(self.keys) - 1
            while i >= 0 and key < self.keys[i]:
                i -= 1
            i += 1
            if len(self.children[i].keys) == 2 * self.degree - 1:
                self.split_child(i)
                if key > self.keys[i]:
                    i += 1
            self.children[i].insert_non_full(key, value)

    def split_child(self, i):
        y = self.children[i]
        z = BPlusTreeNode(y.leaf)
        self.children.insert(i + 1, z)
        self.keys.insert(i, y.keys[self.degree - 1])

        z.keys = y.keys[self.degree:(2 * self.degree - 1)]
        y.keys = y.keys[0:(self.degree - 1)]

        if not y.leaf:
            z.children = y.children[self.degree:(2 * self.degree)]
            y.children = y.children[0:self.degree]

    def sort(self, keys, children):
        for i in range(len(keys)):
            for j in range(0, len(keys) - i - 1):
                if keys[j] > keys[j + 1]:
                    keys[j], keys[j + 1] = keys[j + 1], keys[j]
                    children[j], children[j + 1] = children[j + 1], children[j]
        return keys, children

class BPlusTree:
    def __init__(self, degree):
        self.root = BPlusTreeNode(True)
        self.degree = degree

    def insert(self, key, value):
        root = self.root
        if len(root.keys) == 2 * self.degree - 1:
            new_root = BPlusTreeNode()
            new_root.children.append(root)
            new_root.split_child(0)
            self.root = new_root
            new_root.insert_non_full(key, value)
        else:
            root.insert_non_full(key, value)

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return node.children[i]
        elif node.leaf:
            return None
        else:
            return self._search(node.children[i], key)

    def range_search(self, prefix):
        results = []
        self._range_search(self.root, prefix, results)
        return results

    def _range_search(self, node, prefix, results):
        for i, key in enumerate(node.keys):
            if key.startswith(prefix):
                results.append(node.children[i])
        if not node.leaf:
            for child in node.children:
                self._range_search(child, prefix, results)

def mergesort(arr, key_func):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid], key_func)
    right = mergesort(arr[mid:], key_func)
    return merge(left, right, key_func)

def merge(left, right, key_func):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key_func(left[i]) < key_func(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


@app.route('/search', methods=['GET'])
def search():
    name = request.args.get('name')
    category = request.args.get('category')
    keyword = request.args.get('keyword')

    spots = Destination.query.all()
    tree = BPlusTree(degree=3)
    for spot in spots:
        tree.insert(spot.name.lower(), spot)

    query_results = []
    if name:
        query_results += tree.range_search(name.lower())
    if category:
        for spot in spots:
            if spot.category.lower().startswith(category.lower()):
                query_results.append(spot)
    if keyword:
        for spot in spots:
            if keyword.lower() in spot.description.lower():
                query_results.append(spot)

    top_spots = quicksort(query_results, key_func=lambda x: (x.popularity, x.rating))
    top_spots = top_spots[:10] if len(top_spots) > 10 else top_spots

    result = [
        {
            'name': spot.name,
            'category': spot.category,
            'popularity': spot.popularity,
            'rating': spot.rating,
            'description': spot.description
        }
        for spot in top_spots
    ]

    return jsonify(result)


@app.route('/search_mergesort', methods=['GET'])
def search_mergesort():
    name = request.args.get('name')
    category = request.args.get('category')
    keyword = request.args.get('keyword')

    spots = Destination.query.all()
    tree = BPlusTree(degree=3)
    for spot in spots:
        tree.insert(spot.name.lower(), spot)

    query_results = []
    if name:
        query_results += tree.range_search(name.lower())
    if category:
        for spot in spots:
            if spot.category.lower().startswith(category.lower()):
                query_results.append(spot)
    if keyword:
        for spot in spots:
            if keyword.lower() in spot.description.lower():
                query_results.append(spot)

    top_spots = mergesort(query_results, key_func=lambda x: (x.popularity, x.rating))
    top_spots = top_spots[:10] if len(top_spots) > 10 else top_spots

    result = [
        {
            'name': spot.name,
            'category': spot.category,
            'popularity': spot.popularity,
            'rating': spot.rating,
            'description': spot.description
        }
        for spot in top_spots
    ]

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
