from laser import *
g = Grid(100,100,[[3,4],[7,8]], [[5,9], [99, 33]])


# s = State(3, 4, RIGHT, MINNOR, [], 1)
# print(s)
# for s in s.next_states(g):
#     print(s)

m = Manichie()
init_s = State(-1, 0, RIGHT, EMPTY, [], 0)
print(m.trans_states([init_s], g))
