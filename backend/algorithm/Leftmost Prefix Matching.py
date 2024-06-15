from flask import Flask, request, jsonify

app = Flask(__name__)

#����ǰ׺ƥ���㷨
class TrieNode:
    def __init__(self):
        self.children = {}
        self.notes = []

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, note):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.notes.append(note)

    def search(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return node.notes

# ģ�����ݽṹ��Trieʵ��
trie = Trie()

travel_notes = [
    {"id": 1, "destination_id": 1, "title": "Trip to Paris", "content": "A wonderful trip to Paris with a visit to the Eiffel Tower.", "views": 100, "rating": 4.5, "rate_cnt": 10, "username": "user1"},
    {"id": 2, "destination_id": 2, "title": "Visit to Rome", "content": "An amazing visit to Rome and the Colosseum.", "views": 150, "rating": 4.8, "rate_cnt": 15, "username": "user2"},
    {"id": 3, "destination_id": 1, "title": "Paris Museum Tour", "content": "A tour of museums in Paris, including the Louvre.", "views": 120, "rating": 4.6, "rate_cnt": 12, "username": "user3"},
    # ������ѧ�ռ�...
]

# ����ѧ�ռǲ��뵽Trie��
for note in travel_notes:
    for word in note["content"].lower().split():
        trie.insert(word, note)

@app.route('/search_by_content', methods=['GET'])
def search_notes_by_content():
    query = request.args.get('query')
    if not query:
        return jsonify([])

    # ʹ������ǰ׺ƥ���㷨����ȫ�ļ���
    filtered_notes = trie.search(query.lower())

    result = [
        {
            "id": note["id"],
            "destination_id": note["destination_id"],
            "title": note["title"],
            "content": note["content"],
            "views": note["views"],
            "rating": note["rating"],
            "rate_cnt": note["rate_cnt"],
            "username": note["username"]
        } for note in filtered_notes
    ]

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

'''
Trie(ǰ׺��)�Ļ���ԭ��
�ڵ�ṹ:

TrieNode:ÿ���ڵ����һ���ַ�,����һ���ֵ� children,���ڴ洢�ӽڵ�,�Լ�һ�� notes �б�,���ڴ洢���ǰ׺��ص���ѧ�ռǡ�
Trie�ṹ:

Trie:����һ�����ڵ� root,�Ӹ��ڵ㿪ʼ,���ַ����²������ҡ�
Trie�Ĳ���
����(Insert):

�Ӹ��ڵ㿪ʼ,���ַ���鵥�ʵ�ÿ���ַ���
����ַ��������ڵ�ǰ�ڵ���ӽڵ���,�򴴽�һ���µ�TrieNode��
�ƶ������ӽڵ�,����������һ���ַ���
�ظ���������,ֱ�����ʵ������ַ���������ɡ�
���,����õ�����ص���ѧ�ռǴ洢�����һ���ַ��ڵ�� notes �б��С�
����(Search):

�Ӹ��ڵ㿪ʼ,���ַ����ǰ׺��ÿ���ַ���
����ַ������ڵ�ǰ�ڵ���ӽڵ���,���ƶ������ӽڵ�,����������һ���ַ���
���ǰ׺�������ַ����ҵ�,�򷵻����һ���ַ��ڵ�� notes �б�,��ʾ�������ǰ׺ƥ�����ѧ�ռǡ�

TrieNode��:

self.children:һ���ֵ�,���ڴ洢�ӽڵ�,�����ַ�,ֵ��TrieNode����
self.notes:һ���б�,���ڴ洢�뵱ǰǰ׺��ص���ѧ�ռǡ�
Trie��:

self.root:��ʼ�����ڵ㡣
insert ����:
�Ӹ��ڵ㿪ʼ,���ַ����뵥�ʡ�
����ַ��������ڵ�ǰ�ڵ���ӽڵ���,�򴴽�һ���µ�TrieNode��
�ƶ������ӽڵ�,����������һ���ַ���
���,����õ�����ص���ѧ�ռǴ洢�����һ���ַ��ڵ�� notes �б��С�
search ����:
�Ӹ��ڵ㿪ʼ,���ַ�����ǰ׺��
����ַ������ڵ�ǰ�ڵ���ӽڵ���,���ƶ������ӽڵ�,����������һ���ַ���
���ǰ׺�������ַ����ҵ�,�򷵻����һ���ַ��ڵ�� notes �б�,��ʾ�������ǰ׺ƥ�����ѧ�ռǡ�
'''