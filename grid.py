import os
import json
import gc
from pprint import pprint

UP, DOWN, LEFT, RIGHT = "U", "D", "L", "R"

EMPTY, MINNOR, OBSTRUCTIONS, SUCCEED, WALL = 0, 1, 2, 3, 4
SLASH, BACK_SLASH = "/", "\\"

class InvalidSetGridError(Exception):
    pass

class Grid(object):

    def __init__(self, row, col, minors, obstructions):
        self.row = row
        self.col = col
        self.grid = [[ EMPTY for i in range(self.row)] for j in range(self.col)]
        self.minors = [(x, y) for y,x in minors]
        self.obstructions = [(x, y) for y,x in obstructions]
        for x,y in self.minors:
            self.set_object(x, y, MINNOR)
        for x,y in self.obstructions:
            self.set_object(x, y, OBSTRUCTIONS)

    def set_object(self, x, y, t):
        """
        t: type
        """
        if y >= self.row or x >= self.col or x <0 or y <0:
            raise InvalidSetGridError(f"x: {x}, y: {y}, col: {self.col} row: {self.row}, ")
        self.grid[x][y] = t

    def get_object(self, x, y):
        if x == self.col and y == 0:
            return SUCCEED
        if y >= self.row or x >= self.col or x <0 or y <0:
            return WALL
        return self.grid[x][y]

    def __str__(self):
        readable_data = []
        for y in range(self.row):
            row = []
            for x in range(self.col):
                row.append(self.grid[x][y])
            readable_data.append(row)
        pprint(readable_data)
        return ""


def get_grid_from_data(data):
    row = data['rows']
    col = data['cols']
    obstructions = data['obstructions']
    mirrors = data['mirrors']
    del data
    return Grid(row, col, mirrors, obstructions)

def peek_maps():
    dir_path = 'maps'
    fn = os.listdir(dir_path)
    datas = []
    for f in fn:
        data = get_single_data_from_file(f)
        if not data:
            continue
        data['name'] = f
        datas.append(data)
    for data in sorted(datas, key=lambda v: v["difficulty"]):
        print(f"{data['name']} - {data['difficulty']} - row: {data['rows']}, col: {data['cols']}, mirror: {len(data['mirrors'])}")

def get_solutions(solution_func):
    dir_path = 'maps'
    fs = os.listdir(dir_path)
    output = {}
    output['solutions'] = []
    output['name'] = 'tommy'
    skip_list = ['m29.json', 'm30.json']
    # skip_list = []
    for filename in fs:
        gc.collect()
        print("####################")
        print("Processing ", filename)
        if filename in skip_list:
            continue
        with open(os.path.join(dir_path, filename), 'r') as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                print("Invalid json for:", filename)
                continue
        print(f"row: {data['rows']}, col {data['cols']}, M: {len(data['mirrors'])}")
        result = None
        try:
            result = solution_func(data)
            del data
        except Exception as e:
            print(e)
        if result:
            print(f"Shoutpath dist: {result[1]}")
        else:
            print("Invalid")



def get_single_data_from_file(filename):
    dir_path = 'maps'
    with open(os.path.join(dir_path, filename), 'r') as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError as e:
            print("Error decode:", filename)
            return None
    return data
