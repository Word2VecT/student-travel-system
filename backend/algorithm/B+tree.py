#B+��
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

# ģ���������
travel_notes = [
    {"id": 1, "destination_id": 1, "title": "Trip to Paris", "content": "A wonderful trip to Paris.", "views": 100, "rating": 4.5, "rate_cnt": 10, "username": "user1"},
    {"id": 2, "destination_id": 2, "title": "Visit to Rome", "content": "An amazing visit to Rome.", "views": 150, "rating": 4.8, "rate_cnt": 15, "username": "user2"},
    {"id": 3, "destination_id": 1, "title": "Paris Museum Tour", "content": "A tour of museums in Paris.", "views": 120, "rating": 4.6, "rate_cnt": 12, "username": "user3"},
    # ������ѧ�ռ�...
]

# ����ѧ�ռǲ��뵽B+����
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
B+������ԭ��
�ڵ�ṹ:

�ڲ��ڵ�:�洢�����ӽڵ��ָ��,�����������ҹ��̡�
Ҷ�ӽڵ�:�洢����ֵ(����),��ͨ��ָ������,�γ�һ��˫������
��֧����(order):

B+���Ľ���(order)������ÿ���ڵ��������ж��ٸ��ӽڵ㡣һ��B+���ڵ��������� order ���ӽڵ�,������ order // 2 ���ӽڵ㡣
�������:

���Ҳ����:�Ӹ��ڵ㿪ʼ,������²���,�ҵ�Ӧ�ò����Ҷ�ӽڵ㡣
�����ֵ��:����ֵ�Բ��뵽Ҷ�ӽڵ���,���Ҷ�ӽڵ�����,����Ҫ����(split)��
�ڵ����:���ڵ��еļ������ﵽ����ʱ,���ڵ����Ϊ�����ڵ�,�����м�����������ڵ㡣������ڵ�Ҳ����,��������,ֱ�����ڵ㡣
���Ҳ���:

�Ӹ��ڵ㿪ʼ:�Ӹ��ڵ㿪ʼ,������²���,ֱ���ҵ�Ҷ�ӽڵ㡣
��Ҷ�ӽڵ��в���:��Ҷ�ӽڵ��в���Ŀ���ֵ�ԡ�
'''