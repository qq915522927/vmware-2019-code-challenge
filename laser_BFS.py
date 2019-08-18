from copy import copy
import os
import json

test_input = {
"obstructions": [],
"difficulty": "hard",
"rows": 200,
"cols": 200,
"mirrors": []
}

test_output = { "name": "Team Awesome",
  "solutions": [
    {
       "map": "m1",
       "shortestPath": [
         [0, 3, 0],
         [8, 3, 0],
         [8, 8, 1],
         [0, 8, 1]
       ],
       "invalid": False
    },
    {
       "map": "m2",
       "shortestPath": None,
       "invalid": False
    }
  ]
}
UP, DOWN, LEFT, RIGHT = "UP", "DOWN", "LEFT", "RIGHT"

EMPTY, MINNOR, OBSTRUCTIONS, SUCCEED, WALL = "EMPTY", "MINNOR", "OBSTRUCTIONS", "SUCCEED", "WALL"
SLASH, BACK_SLASH = 1, 0

class Grid(object):

    def __init__(self, row, col, minors, obstructions):
        self.row = row
        self.col = col
        self.grid = {}
        self.minors = [(y, x) for x,y in minors]
        self.total_mirror_n = len(self.minors)
        self.obstructions = [(y, x) for x,y in obstructions]
        for x,y in self.minors:
            self.set_object(x, y, MINNOR)
        for x,y in self.obstructions:
            self.set_object(x, y, OBSTRUCTIONS)

    def set_object(self, x, y, t):
        """
        t: type
        """
        pos = (x, y)
        self.grid[pos] = t

    def get_object(self, x, y):
        pos = (x, y)
        if y ==0 and x == self.col:
            return SUCCEED
        if y >= self.row or x >= self.col or x <0 or y <0:
            return WALL
        if pos not in self.minors and pos not in self.obstructions:
            return EMPTY
        else:
            return self.grid[pos]



next_pos_by_direction = {
    UP: lambda x,y: (x, y-1),
    DOWN: lambda x,y: (x, y+1),
    LEFT: lambda x,y: (x-1, y),
    RIGHT: lambda x,y: (x+1, y),
}

slash_next_d_map = {
    UP: RIGHT,
    DOWN: LEFT,
    LEFT: DOWN,
    RIGHT: UP,
}
back_slash_next_d_map = {
    UP: LEFT,
    DOWN: RIGHT,
    LEFT: UP,
    RIGHT: DOWN,
}
# two ways has been traversed
ALL_VISITED_MIRRORS = []

class State(object):

    def __init__(self, x, y, d, t, pre_minnor_states, step, pre_states):
        self.x = x
        self.y = y
        self.in_direction = d
        self.type = t
        self.pre_minnor_states = pre_minnor_states
        self.pre_states = pre_states
        # if step >= 50000:
        #     raise Exception("Too long step")
        self.step = step 
        self.minor_angle = None

    def get_remining_mirrors_n(self, grid):
        pre_mirror_n = len(self.pre_minnor_states)
        total_mirror_n = len(grid.minors)
        return total_mirror_n - pre_mirror_n

    def set_minnor_angle(self, angle):
        self.minor_angle = angle

    def is_duplicate_minnor(self):
        visited_m_pos = [(m.x, m.y) for m in self.pre_minnor_states]
        if (self.x,self.y) in visited_m_pos:
            return True
        else:
            return False

    def next_states(self, grid):
        """
        Get next state
        """
        if self.type == EMPTY:
            x, y = next_pos_by_direction[self.in_direction](self.x, self.y)
            next_state_type = grid.get_object(x, y)
            pre_minior = copy(self.pre_minnor_states)
            pre_states = copy(self.pre_states)
            pre_states.append(self)

            return [State(x, y, self.in_direction, next_state_type, pre_minior, self.step+1, pre_states)]
        elif self.type in [OBSTRUCTIONS, WALL]:
            return [None]

        elif self.is_duplicate_minnor():
            return [None]
        elif self.type == MINNOR and not (self.minor_angle in [SLASH, BACK_SLASH]):
            slash_s = self.copy()
            slash_s.set_minnor_angle(SLASH)
            slash_next_d = slash_next_d_map[slash_s.in_direction]
            slash_n_x, slash_n_y = next_pos_by_direction[slash_next_d](slash_s.x, slash_s.y)
            s_pre_minor = copy(slash_s.pre_minnor_states)
            s_pre_minor.append(slash_s)
            pre_states = copy(slash_s.pre_states)
            pre_states.append(slash_s)
            next_state_af_slash = State(
                slash_n_x,
                slash_n_y,
                slash_next_d,
                grid.get_object(slash_n_x, slash_n_y),
                s_pre_minor,
                slash_s.step+1,
                pre_states
            )


            back_slash_s = self.copy()
            back_slash_s.set_minnor_angle(BACK_SLASH)
            back_slash_next_d = back_slash_next_d_map[back_slash_s.in_direction]
            back_slash_n_x, back_slash_n_y = next_pos_by_direction[back_slash_next_d](back_slash_s.x, back_slash_s.y)
            b_slash_pre_minor = copy(back_slash_s.pre_minnor_states)
            b_slash_pre_minor.append(back_slash_s)
            pre_states = copy(back_slash_s.pre_states)
            pre_states.append(back_slash_s)
            next_state_af_back_slash = State(
                back_slash_n_x,
                back_slash_n_y,
                back_slash_next_d,
                grid.get_object(back_slash_n_x, back_slash_n_y),
                b_slash_pre_minor,
                back_slash_s.step+1,
                pre_states
            )
            return [next_state_af_slash, next_state_af_back_slash]


    def copy(self):
        pre_minior = copy(self.pre_minnor_states)
        pre_states = copy(self.pre_states)
        return State(
            self.x,
            self.y, 
            self.in_direction,
            self.type, pre_minior, self.step, pre_states)


    def __str__(self):
        return "<<type: {}, x:{}, y:{}, direction: {}, step: {}, pre_minior: {} angle: {}>>".format(
            self.type,
            self.x,
            self.y,
            self.in_direction,
            self.step,
            self.pre_minnor_states,
            self.minor_angle
        )

    def __repr__(self):
        return self.__str__()
        

class Manichie(object):

    def trans_states(self, states, grid):
        """
        return new states list
        """
        n = 0
        self.init_screen_data(grid)
        while True:
            # if n >= 3000:
            #     return None
            res = []
            for s in states:
                new_states = s.next_states(grid)
                res = res + new_states

            valid_res = []
            for s in res:
                if s is None:
                    continue
                elif s.type == SUCCEED:
                    self.finish_screen(s, grid)
                    return s
                valid_res.append(s)
            if not valid_res:
                return None
            # print('\r', len(valid_res), end="")
            # if len(valid_res) >= 3000:
            #     return None

            states = valid_res
            self.screen(states, grid)
            n += 1
            # print('\r', n, end="")
            if n>= 30000:
                return None
            # if n>= 3000:
            #     return None
            # self.screen(states[0], grid)

    def init_screen_data(self, grid):
        self.screen_data = [[ '.' for i in range(grid.col)] for c in range(grid.row) ]
        try:
            for x,y in grid.minors:
                try:
                    self.screen_data[y][x] = 'm'
                except IndexError:
                    print('Mirror %s,%s is not Valid' % (y,x))
            for x,y in grid.obstructions:
                self.screen_data[y][x] = '0'
        except Exception:
            print("Error for x, y: %s, %s"% (x,y))
            raise

    def finish_screen(self, cus_s, grid):
        res = ''
        if not (cus_s.y <0 or cus_s.x < 0 or cus_s.y >= grid.row or cus_s.x >= grid.col):
            self.screen_data[cus_s.y][cus_s.x] = "*"
        for pre_s in cus_s.pre_states:
            if not (pre_s.y <0 or pre_s.x < 0 or pre_s.y >= grid.row or pre_s.x >= grid.col):
                if pre_s.in_direction in [UP, DOWN]:
                    self.screen_data[pre_s.y][pre_s.x] = "|"
                if pre_s.in_direction in [LEFT, RIGHT]:
                    self.screen_data[pre_s.y][pre_s.x] = "_"

            
        for pre_m in cus_s.pre_minnor_states:
            if pre_m.minor_angle == SLASH:
                angle = "/"
            if pre_m.minor_angle == BACK_SLASH:
                angle = "\\"
            self.screen_data[pre_m.y][pre_m.x] = angle
        for row in self.screen_data:
            row = ''.join(row)
            res += row + '\n'
        print('\033[H\033[J')
        print(res, end='')

    def screen(self, states, grid):
        full = []
        for cus_s in states:
            res = ''
            if not (cus_s.y <0 or cus_s.x < 0 or cus_s.y >= grid.row or cus_s.x >= grid.col):
                self.screen_data[cus_s.y][cus_s.x] = "*"
            for pre_s in cus_s.pre_states:
                if not (pre_s.y <0 or pre_s.x < 0 or pre_s.y >= grid.row or pre_s.x >= grid.col):
                    if pre_s.in_direction in [UP, DOWN]:
                        self.screen_data[pre_s.y][pre_s.x] = "|"
                    if pre_s.in_direction in [LEFT, RIGHT]:
                        self.screen_data[pre_s.y][pre_s.x] = "_"

                
            for pre_m in cus_s.pre_minnor_states:
                if pre_m.minor_angle == SLASH:
                    angle = "/"
                if pre_m.minor_angle == BACK_SLASH:
                    angle = "\\"
                self.screen_data[pre_m.y][pre_m.x] = angle
            for row in self.screen_data:
                row = ' '.join(row)
                res += row + '\n'
            full.append(res)
        print('\033[H\033[J')
        print(res, end='')
        # reset back
        # if not (cus_s.y <0 or cus_s.x < 0 or cus_s.y >= grid.row or cus_s.x >= grid.col):
        #     self.screen_data[cus_s.y][cus_s.x] = "-"
        # for pre_m in cus_s.pre_minnor_states:
        #     if pre_m.minor_angle == SLASH:
        #         angle = "/"
        #     if pre_m.minor_angle == BACK_SLASH:
        #         angle = "\\"
        #     self.screen_data[pre_m.y][pre_m.x] = 'm'
        import time
        time.sleep(0.1)
        self.init_screen_data(grid)



        

def get_grid_from_data(data):
    row = data['rows']
    col = data['cols']
    obstructions = data['obstructions']
    mirrors = data['mirrors']
    return Grid(row, col, mirrors, obstructions)

def get_single_solution(data):
    # if data['difficulty'] == "hard":
    #     return None
    print("##############################")
    print(data['difficulty'])
    print('rows:', data['rows'])
    print('cols:', data['cols'])
    print('mirror_n:', len(data['mirrors']))
    grid = get_grid_from_data(data)
    m = Manichie()
    init_s = State(-1, 0, RIGHT, EMPTY, [], 0, [])
    try:
        succeed = m.trans_states([init_s], grid)
    except Exception as e:
        import traceback
        print('TimeOut ')
        traceback.print_exc()
        succeed = None
    if succeed:
        result = [ [m.y, m.x, m.minor_angle]for m in succeed.pre_minnor_states]
    else:
        result = None
    if not result:
        result = None
    if result is None:
        print("result:", "None")
    return result
    

def get_solutions():
    import os
    dir_path = 'maps'
    fs = os.listdir(dir_path)
    output = {}
    output['solutions'] = []
    output['name'] = 'tommy'
    for filename in fs:
        print("Processing ", filename)
        with open(os.path.join(dir_path, filename), 'r') as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                print(filename)
        result = get_single_solution(data)
        if result:
            short_path = result
            sol = {}
            sol['map'] = filename.split('.')[0]
            sol['shortestPath'] = short_path 
            sol['invalid'] = False
        else:
            sol = {}
            sol['map'] = filename.split('.')[0]
            sol['shortestPath'] =  None
            sol['invalid'] = True
        output['solutions'].append(sol)
    with open('tommy_result.json', 'w') as f:
        f.write(json.dumps(output, indent=2))

def get_single_solution_from_file(filename):
    dir_path = 'maps'
    print("Processing ", filename)
    with open(os.path.join(dir_path, filename), 'r') as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError as e:
            print("Error decode:", filename)
            raise
    result = get_single_solution(data)
    return result

if __name__ == "__main__":
    data = {
        "rows": 10,
        "cols": 10,
        "mirrors": [[0, 3], [8, 3], [8, 8], [0, 8], [8, 1]],
        "obstructions": [[4, 4], [5, 5]],
        "difficulty": "easy"
    }
    data2 = {
        "rows": 10,
        "cols": 10,
        "mirrors": [[0, 5], [3, 5], [3 ,9], [0, 9]],
        # "mirrors": [[0, 3], [2, 7]],
        "obstructions": [],
        "difficulty": "easy"
    }
    # result = get_single_solution(data2)
    # print(result)

    # get_solutions()

    # m04, m05
    result = get_single_solution_from_file('ui_input.json')
    # print(result)

