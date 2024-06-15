from flask import Flask, request, jsonify

app = Flask(__name__)

#最左前缀匹配算法
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

# 模拟数据结构和Trie实例
trie = Trie()

travel_notes = [
    {"id": 1, "destination_id": 1, "title": "Trip to Paris", "content": "A wonderful trip to Paris with a visit to the Eiffel Tower.", "views": 100, "rating": 4.5, "rate_cnt": 10, "username": "user1"},
    {"id": 2, "destination_id": 2, "title": "Visit to Rome", "content": "An amazing visit to Rome and the Colosseum.", "views": 150, "rating": 4.8, "rate_cnt": 15, "username": "user2"},
    {"id": 3, "destination_id": 1, "title": "Paris Museum Tour", "content": "A tour of museums in Paris, including the Louvre.", "views": 120, "rating": 4.6, "rate_cnt": 12, "username": "user3"},
    # 其他游学日记...
]

# 将游学日记插入到Trie中
for note in travel_notes:
    for word in note["content"].lower().split():
        trie.insert(word, note)

@app.route('/search_by_content', methods=['GET'])
def search_notes_by_content():
    query = request.args.get('query')
    if not query:
        return jsonify([])

    # 使用最左前缀匹配算法进行全文检索
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
Trie(前缀树)的基本原理
节点结构:

TrieNode:每个节点代表一个字符,包含一个字典 children,用于存储子节点,以及一个 notes 列表,用于存储与该前缀相关的游学日记。
Trie结构:

Trie:包含一个根节点 root,从根节点开始,逐字符向下插入或查找。
Trie的操作
插入(Insert):

从根节点开始,逐字符检查单词的每个字符。
如果字符不存在于当前节点的子节点中,则创建一个新的TrieNode。
移动到该子节点,继续处理下一个字符。
重复上述步骤,直到单词的所有字符都插入完成。
最后,将与该单词相关的游学日记存储在最后一个字符节点的 notes 列表中。
查找(Search):

从根节点开始,逐字符检查前缀的每个字符。
如果字符存在于当前节点的子节点中,则移动到该子节点,继续处理下一个字符。
如果前缀的所有字符都找到,则返回最后一个字符节点的 notes 列表,表示所有与该前缀匹配的游学日记。

TrieNode类:

self.children:一个字典,用于存储子节点,键是字符,值是TrieNode对象。
self.notes:一个列表,用于存储与当前前缀相关的游学日记。
Trie类:

self.root:初始化根节点。
insert 方法:
从根节点开始,逐字符插入单词。
如果字符不存在于当前节点的子节点中,则创建一个新的TrieNode。
移动到该子节点,继续处理下一个字符。
最后,将与该单词相关的游学日记存储在最后一个字符节点的 notes 列表中。
search 方法:
从根节点开始,逐字符查找前缀。
如果字符存在于当前节点的子节点中,则移动到该子节点,继续处理下一个字符。
如果前缀的所有字符都找到,则返回最后一个字符节点的 notes 列表,表示所有与该前缀匹配的游学日记。
'''