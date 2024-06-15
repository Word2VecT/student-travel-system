#B+树
class BPlusTreeNode:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []

class BPlusTree:
    def __init__(self, order=4):
        self.root = BPlusTreeNode(is_leaf=True)
        self.order = order

    def insert(self, key, value):
        root = self.root
        if len(root.keys) == (self.order - 1):
            new_root = BPlusTreeNode()
            new_root.children.append(self.root)
            self.split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key, value)

    def _insert_non_full(self, node, key, value):
        if node.is_leaf:
            insertion_index = 0
            while insertion_index < len(node.keys) and key > node.keys[insertion_index]:
                insertion_index += 1
            node.keys.insert(insertion_index, key)
            node.children.insert(insertion_index, value)
        else:
            insertion_index = 0
            while insertion_index < len(node.keys) and key > node.keys[insertion_index]:
                insertion_index += 1
            if len(node.children[insertion_index].keys) == (self.order - 1):
                self.split_child(node, insertion_index)
                if key > node.keys[insertion_index]:
                    insertion_index += 1
            self._insert_non_full(node.children[insertion_index], key, value)

    def split_child(self, parent, index):
        node = parent.children[index]
        median = self.order // 2

        new_node = BPlusTreeNode(is_leaf=node.is_leaf)
        parent.keys.insert(index, node.keys[median])
        parent.children.insert(index + 1, new_node)

        new_node.keys = node.keys[median + 1:]
        node.keys = node.keys[:median]

        if not node.is_leaf:
            new_node.children = node.children[median + 1:]
            node.children = node.children[:median + 1]

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        if node.is_leaf:
            for i, item in enumerate(node.keys):
                if item == key:
                    return node.children[i]
            return None
        else:
            insertion_index = 0
            while insertion_index < len(node.keys) and key > node.keys[insertion_index]:
                insertion_index += 1
            return self._search(node.children[insertion_index], key)

from flask import Flask, request, jsonify

app = Flask(__name__)

b_plus_tree = BPlusTree()

# 模拟插入数据
travel_notes = [
    {"id": 1, "destination_id": 1, "title": "Trip to Paris", "content": "A wonderful trip to Paris.", "views": 100, "rating": 4.5, "rate_cnt": 10, "username": "user1"},
    {"id": 2, "destination_id": 2, "title": "Visit to Rome", "content": "An amazing visit to Rome.", "views": 150, "rating": 4.8, "rate_cnt": 15, "username": "user2"},
    {"id": 3, "destination_id": 1, "title": "Paris Museum Tour", "content": "A tour of museums in Paris.", "views": 120, "rating": 4.6, "rate_cnt": 12, "username": "user3"},
    # 其他游学日记...
]

# 将游学日记插入到B+树中
for note in travel_notes:
    b_plus_tree.insert(note["title"], note)

@app.route('/search_by_title', methods=['GET'])
def search_notes_by_title():
    title = request.args.get('title')
    note = b_plus_tree.search(title)
    
    if note:
        result = {
            "id": note["id"],
            "destination_id": note["destination_id"],
            "title": note["title"],
            "content": note["content"],
            "views": note["views"],
            "rating": note["rating"],
            "rate_cnt": note["rate_cnt"],
            "username": note["username"]
        }
    else:
        result = {}

    return jsonify(result)

'''
B+树基本原理
节点结构:

内部节点:存储键和子节点的指针,用于引导查找过程。
叶子节点:存储键和值(数据),并通过指针相连,形成一个双向链表。
分支因子(order):

B+树的阶数(order)决定了每个节点最多可以有多少个子节点。一个B+树节点最多可以有 order 个子节点,至少有 order // 2 个子节点。
插入操作:

查找插入点:从根节点开始,逐层向下查找,找到应该插入的叶子节点。
插入键值对:将键值对插入到叶子节点中,如果叶子节点满了,就需要分裂(split)。
节点分裂:当节点中的键数量达到上限时,将节点分裂为两个节点,并将中间键提升到父节点。如果父节点也满了,继续分裂,直到根节点。
查找操作:

从根节点开始:从根节点开始,逐层向下查找,直到找到叶子节点。
在叶子节点中查找:在叶子节点中查找目标键值对。
'''