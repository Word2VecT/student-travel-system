import heapq

# 保持排序算法不变，因为Python的内置排序已经非常高效
def sort_items(items, key="name", reverse=False):
    """对给定的列表进行排序。"""
    return sorted(items, key=lambda x: x.get(key, 0), reverse=reverse)


# 实现二分查找
def binary_search(items, key, value):
    """在有序列表中使用二分查找。"""
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_val = items[mid].get(key)
        if mid_val < value:
            low = mid + 1
        elif mid_val > value:
            high = mid - 1
        else:
            return items[mid]
    return None


# 改进的A*算法实现
def a_star(graph, start, goal, heuristic_func):
    """简化版A*算法。"""
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while open_set:
        current_cost, current = heapq.heappop(open_set)

        if current == goal:
            break

        for next, cost in graph.get(current, []):
            new_cost = cost_so_far[current] + cost
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic_func(goal, next)
                heapq.heappush(open_set, (priority, next))
                came_from[next] = current

    # Reconstruct the path
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from.get(current)
    path.append(start)
    path.reverse()
    return path


# 示例启发式函数
def heuristic(goal, next):
    """一个简单的启发式函数示例，假设goal和next都是坐标点。"""
    # 此处的实现需要根据实际情况定制，以下仅为占位符
    return abs(goal - next)
