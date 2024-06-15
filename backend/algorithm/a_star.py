import math
from flask import Flask, jsonify

app = Flask(__name__)

class Facility:
    def __init__(self, name, category, x, y):
        self.name = name
        self.category = category
        self.x = x
        self.y = y

    def distance_to(self, other_x, other_y):
        # 计算当前设施到另一个位置的欧几里得距离
        return math.sqrt((self.x - other_x) ** 2 + (self.y - other_y) ** 2)


class CustomPriorityQueue:
    def __init__(self):
        self.elements = []

    def is_empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        self.elements.append((priority, item))
        self.elements.sort(key=lambda x: x[0])

    def get(self):
        return self.elements.pop(0)[1]


def heuristic(a, b):
    # 启发式函数，计算两个点之间的欧几里得距离
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def a_star(graph, start, goal):
    open_list = CustomPriorityQueue()
    open_list.put(start, 0)
    came_from = {}
    cost_so_far = {start: 0}

    while not open_list.is_empty():
        current = open_list.get()

        if current == goal:
            break

        for neighbor in graph[current]:
            new_cost = cost_so_far[current] + graph[current][neighbor]
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(neighbor, goal)
                open_list.put(neighbor, priority)
                came_from[neighbor] = current

    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()

    return cost_so_far[goal], path



def find_shortest_path(graph, start, end):
    small_graph = {}
    for node in [start, end]:
        small_graph[node] = {}
        for neighbor in graph[node]:
            if neighbor in [start, end]:
                small_graph[node][neighbor] = graph[node][neighbor]

    distance, path = a_star(small_graph, start, end)
    return distance, path

# 根路由，返回欢迎信息
@app.route('/')
def index():
    return "Welcome to the Route Planning API!"

# 最短路径路由，接受起点和终点参数，返回最短路径信息
@app.route('/shortest_path/<start>/<end>')
def shortest_path_route(start, end):
    # 示例图
    graph = {
        'A': {'B': 1, 'C': 3, 'D': 7},
        'B': {'A': 1, 'C': 1, 'D': 2},
        'C': {'A': 3, 'B': 1, 'D': 3},
        'D': {'A': 7, 'B': 2, 'C': 3}
    }
    distance, path = find_shortest_path(graph, start, end)
    return jsonify({'distance': distance, 'path': path})


if __name__ == '__main__':
    app.run(debug=True)
