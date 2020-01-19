
from unittest.mock import Mock
from pprint import pprint
from grid import *
from heapq import heappush, heappop

import sys
import resource
soft, hard = 5 * 10**9, 5 * 10**9
# soft, hard = 10**8, 10**8   # uncommenting this allows program to finish
resource.setrlimit(resource.RLIMIT_AS,(soft, hard))

class Solution:

    MIRROR_DIRECTION_MAP = {
        UP: [RIGHT, LEFT],
        DOWN: [LEFT, RIGHT],
        LEFT: [UP, DOWN],
        RIGHT: [UP, DOWN]
    }
    def __init__(self, debug=True):
        self.debug = debug

    def get_minnor_position(self, p1, p2, p3):
        assert (p1['x'] == p2['x']) ^ (p1['y'] == p2['y'])
        assert (p2['x'] == p3['x']) ^ (p2['y'] == p3['y'])
        if p2['x'] > p1['x']: #right
            if p3['y'] > p2['y']:
                return BACK_SLASH
            if p3['y'] < p2['y']:
                return SLASH
        if p2['x'] < p1['x']: # left
            if p3['y'] > p2['y']:
                return SLASH
            if p3['y'] < p2['y']:
                return BACK_SLASH
        if p2['y'] < p1['y']: # up
            if p3['x'] < p2['x']:
                return BACK_SLASH
            if p3['x'] > p2['x']:
                return SLASH
        if p2['y'] > p1['y']: # down
            if p3['x'] < p2['x']:
                return SLASH
            if p3['x'] > p2['x']:
                return BACK_SLASH
        raise Exception(f"{p1}\n{p2}\n{p3}")

    def solve(self, grid):
        self.grid = grid
        self.graph = Graph( 4 * len(self.grid.minors) + 2)
        self.generate_graph()
        end_p = (self.grid.col, 0, RIGHT)
        if  end_p not in self.nodes_by_x_y:
            return None
        start = self.nodes_by_x_y[(-1, 0, RIGHT)]
        path, min_dist = self.graph.shorest_path(start, self.nodes_by_x_y[end_p])

        grid_path = []
        last_node = None
        for i, p in enumerate(path):
            node = self.nodes[p.w]
            if i != 0:
                node['minnor'] = self.get_minnor_position(last_node, node, self.nodes[p.v])
            grid_path.append(node)
            if i == len(path) - 1:
                grid_path.append(self.nodes[p.v])
            last_node = node

        return grid_path, min_dist

    def generate_graph(self):
        point = {
            'x': -1,
            'y': 0,
            'd': RIGHT,
            'type': EMPTY
        }
        self.visited_path = set()
        self.mirror_stack = []
        self.mirror_stack.append(point)
        self.visited_mirror_by_xy = {}
        self.visited_mirror_by_xy[(point['x'],point['y'])] = point
        self.nodes = []
        self.nodes_by_x_y = {}
        for m in self.grid.minors:
            for d in [UP, DOWN, LEFT, RIGHT]:
                self.nodes.append(
                    {'x': m[0], 'y': m[1], 'd': d}
                )
                self.nodes_by_x_y[(m[0], m[1], d)] = len(self.nodes) - 1
        self.nodes.append(point)
        self.nodes_by_x_y[(point['x'], point['y'], point['d'])] = len(self.nodes) - 1
        self.nodes.append({'x': self.grid.col, 'y': 0, 'd': RIGHT})
        self.nodes_by_x_y[(self.grid.col, 0, RIGHT)] = len(self.nodes) - 1
        self.stack = []
        self.stack.append(point)
        while self.stack:
            point = self.stack.pop()
            if point['type'] == MINNOR or point['type'] == SUCCEED:
                if self.mirror_stack:
                    last_mirror = self.mirror_stack[-1]
                    try:
                        edge = self.cal_edge(self.mirror_stack[-2], last_mirror, point)
                        self.graph.add_edge(edge)
                    except IndexError:
                        edge = self.cal_edge(None, last_mirror, point)
                        self.graph.add_edge(edge)
                self.mirror_stack.append(point)
                self.visited_mirror_by_xy[(point['x'], point['y'])] = True
            next_points = self.get_next_points(point['x'], point['y'], point['d'])
            if not next_points:
                self.backward()


            for p in next_points:
                self.stack.append(p)


    def check_graph(self, p):
        if not self.debug:
            return
        start = self.nodes_by_x_y[(-1, 0)]
        c = self.nodes_by_x_y[(p['x'], p['y'])]
        path, min_dist = self.graph.shorest_path(start, c)

        grid_path = []
        last_node = None
        for i, p in enumerate(path):
            node = self.nodes[p.w]
            if i != 0:
                node['minnor'] = self.get_minnor_position(last_node, node, self.nodes[p.v])
            grid_path.append(node)
            if i == len(path) - 1:
                grid_path.append(self.nodes[p.v])
            last_node = node

    def check_mirro_stack(self):
        if not self.debug:
            return
        if len(self.mirror_stack) >=3:
            for i in range(len(self.mirror_stack) - 2):
                p1 = self.mirror_stack[i]
                p2 = self.mirror_stack[i+1]
                p3 = self.mirror_stack[i+2]
                if ((p1['x'] == p2['x'] == p3['x']) or (p1['y'] == p2['y'] == p3['y'])):
                    raise Exception("Check error")

    def backward(self):
        last_m = self.mirror_stack.pop()
        self.visited_mirror_by_xy.pop((last_m['x'], last_m['y']))
        if self.stack:
            back_point = self.stack[-1]
            if back_point['x'] != last_m['x'] or back_point["y"] != last_m["y"]:
                while True:
                    last_m = self.mirror_stack.pop()
                    self.visited_mirror_by_xy.pop((last_m['x'], last_m['y']))
                    if last_m['x'] == back_point['x'] and last_m['y'] == back_point['y']:
                        break

    def cal_edge(self, p0, p1, p2):
        assert (p1['x'] == p2['x']) ^ (p1['y'] == p2['y']), f"p1 {p1}, p2 {p2}"
        if p0:
            assert (p0['x'] == p1['x']) ^ (p0['y'] == p1['y']), f"p1 {p0}, p2 {p1}"
            if (p0['x'] == p1['x'] == p2['x']) or (p0['y'] == p1['y'] == p2['y']):
                raise Exception(f"Error: {p0} {p1} {p2}")
        if p1['x'] == p2['x']:
            wt = abs(p2['y'] - p1['y'])
        else:
            wt = abs(p2['x'] - p1['x'])
        return Edge(self.nodes_by_x_y[(p1['x'], p1['y'], p1['d'])], self.nodes_by_x_y[(p2['x'], p2['y'], p2['d'])], wt)

    def get_next_points(self, x, y, direction):
        while True:
            if direction == UP:
                y -= 1
            if direction == DOWN:
                y += 1
            if direction == LEFT:
                x -= 1
            if direction == RIGHT:
                x += 1
            state = self.grid.get_object(x, y)
            if state == MINNOR:
                if (x, y) in self.visited_mirror_by_xy:
                    return []
                if (x, y, direction) not in self.visited_path:
                    self.visited_path.add((x, y, direction))
                    directs = self.MIRROR_DIRECTION_MAP[direction]
                    p1 = (x, y, directs[0])
                    p2 = (x, y, directs[1])
                    res = []
                    res.append({'x':x , 'y': y, 'd': p1[2], 'type': MINNOR})
                    res.append({'x':x , 'y': y, 'd': p2[2], 'type': MINNOR})
                    return res
                else:
                    return []
            if state == SUCCEED:
                return [{'x':x , 'y': y, 'd': direction, 'type': SUCCEED}]

            if state == WALL:
                return []
            if state == OBSTRUCTIONS:
                return []


class Edge:

    def __init__(self, w, v, wt):
        self.w = w
        self.v = v
        self.wt = wt

    def __hash__(self):
        return self.w * 20 +  self.v + 3  + self.wt *14

    def __eq__(self, other):
        return self.w == other.w and self.v == other.v and self.wt == other.wt

    def __str__(self):
        return f"({self.w}->{self.v}: {self.wt})"

    def __repr__(self):
        return self.__str__()

    def __le__(self, other):
        return self.wt <= other.wt

    def __lt__(self, other):
        return self.wt < other.wt

    def __gt__(self, other):
        return self.wt > other.wt

    def __ge__(self, other):
        return self.wt >= other.wt


class Graph:

    def __init__(self, v):
        self.v = v
        self.g = [set() for i in range(v)]

    def add_edge(self, edge):

        self.g[edge.w].add(edge)

    def __str__(self):
        pprint(self.g)
        return ""

    def __repr__(self):
        return self.__str__()

    def shorest_path(self, start, dest):
        heap = []
        dist_to = [0 for i in range(self.v)]
        from_edge = [-1 for i in range(self.v)]
        visited = [False for i in range(self.v)]
        s_edge = Edge(start, start, 0)
        s_path = Path(start, start)
        dist_to[start] = 0
        from_edge[start] = s_edge
        heappush(heap, s_path)
        assert self.g[start], 'at least one edge'
        while heap:
            p = heappop(heap)
            if (not dist_to[p.to]) or (p.wt < dist_to[p.to]):
                dist_to[p.to] = p.wt
                visited[p.to] = True
                if p.to == dest:
                    break
            for adj in self.g[p.to]:
                if not visited[adj.v]:
                    from_edge[adj.v] = adj
                    heappush(heap, Path(adj.v, dist_to[adj.w] + adj.wt))

        stack =[]
        edge = from_edge[dest]
        if(isinstance(edge, int)):
            raise Exception("No shortest path")
        while edge.v != edge.w:
            stack.append(edge)
            edge = from_edge[edge.w]
        stack.reverse()
        return stack, dist_to[dest]

class Path:
    def __init__(self, to, wt):
        self.to = to
        self.wt = wt

    def __le__(self, other):
        return self.wt <= other.wt

    def __lt__(self, other):
        return self.wt < other.wt

    def __gt__(self, other):
        return self.wt > other.wt

    def __ge__(self, other):
        return self.wt >= other.wt




def solve(data):
    grid = get_grid_from_data(data)
    sol = Solution(debug=False)
    try:
        res = sol.solve(grid)
    except InvalidSetGridError as e:
        print(e)
        print("Invalid set grid")
    return res

if __name__ == '__main__':
    # peek_maps()
    # fn = "m14.json"
    # data = get_single_data_from_file(fn)
    # print(solve(data))


    get_solutions(solve)
