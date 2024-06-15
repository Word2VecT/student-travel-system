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


def greedy_tsp(graph, current_location, points):
    path = [current_location]
    current_point = current_location
    remaining_points = points.copy()

    while remaining_points:
        min_distance = float('inf')
        nearest_point = None
        for point in remaining_points:
            distance = graph[current_point][point]
            if distance < min_distance:
                min_distance = distance
                nearest_point = point
        path.append(nearest_point)
        remaining_points.remove(nearest_point)
        current_point = nearest_point

    path.append(current_location)
    return path


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

# 旅行商问题路由，接受当前位置和途经点参数，返回旅行商问题路径信息
@app.route('/tsp/<current_location>/<points>')
def tsp_route(current_location, points):
    points = points.split(',')
    graph = {
        'A': {'B': 1, 'C': 3, 'D': 7},
        'B': {'A': 1, 'C': 1, 'D': 2},
        'C': {'A': 3, 'B': 1, 'D': 3},
        'D': {'A': 7, 'B': 2, 'C': 3}
    }
    tsp_path = greedy_tsp(graph, current_location, points)
    return jsonify({'path': tsp_path})

if __name__ == '__main__':
    app.run(debug=True)
