# -*- coding: utf-8 -*-
'''
试着来写一下这个问题
一个背包有7种资源（例如体积、重量），每个资源的总量为(18209, 7692, 1333, 924, 26638, 61188, 13360 )。
有12种物品，每个物品对应的价格为(96, 76, 56, 11, 86, 10, 66, 86, 83, 12, 9, 81 )。
一个物品放入背包时，所占用的资源不同（见表）。问题是如何放置，使总的价格最多。

资源集合   R    j  \in R
物品集合   I     i   \in  I

资源r的总量     L_j
物品i的价格      P_i
物品i放入背包时占用资源j的量     C_ij

决策变量
物品i放入背包的个数    U_i

目标函数
\max  \sum_i  (U_i \cdot P_i)

约束条件
\sum_i(U_i \cdot C_ij) \le L_j   ， \forall j
'''

import cplex
from cplex.exceptions import CplexError

#data
items = list(range(12))
resources = list(range(7))
capacity = [18209, 7692, 1333, 924, 26638, 61188, 13360]
value = [96, 76, 56, 11, 86, 10, 66, 86, 83, 12, 9, 81]

use = [
      [ 19,   1,  10,  1,   1,  14, 152, 11,  1,   1, 1, 1 ],
      [  0,   4,  53,  0,   0,  80,   0,  4,  5,   0, 0, 0 ],
      [  4, 660,   3,  0,  30,   0,   3,  0,  4,  90, 0, 0],
      [  7,   0,  18,  6, 770, 330,   7,  0,  0,   6, 0, 0],
      [  0,  20,   0,  4,  52,   3,   0,  0,  0,   5, 4, 0],
      [  0,   0,  40, 70,   4,  63,   0,  0, 60,   0, 4, 0],
      [  0,  32,   0,  0,   0,   5,   0,  3,  0, 660, 0, 9]];

my_obj = value
my_ub = [max(capacity) for i in range(len(items))]
my_lb = [0.0 for i in range(len(items))]
my_ctype = "I" * len(items)
my_colnames = ["x%s" %i for i in range(1,len(items)+1)]
my_rhs = capacity
my_rownames = ["r%s" %i for i in range(1,len(capacity)+1)]
my_sense = "L" * len(capacity)

rows = [[0]*2 for i in range(len(capacity))]
for i in range(len(capacity)):
    rows[i][0] = my_colnames
    rows[i][1] = use[i]


def populatebyrow(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)

    prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype,
                       names=my_colnames)

    prob.linear_constraints.add(lin_expr=rows, senses=my_sense,
                                rhs=my_rhs, names=my_rownames)

try:
    my_prob = cplex.Cplex()
    handle = populatebyrow(my_prob)
    my_prob.solve()

except CplexError as exc:
    print(exc)

print()
# solution.get_status() returns an integer code
print("Solution status = ", my_prob.solution.get_status(), ":", end=' ')
# the following line prints the corresponding string
print(my_prob.solution.status[my_prob.solution.get_status()])
print("Solution value  = ", my_prob.solution.get_objective_value())

numcols = my_prob.variables.get_num()
numrows = my_prob.linear_constraints.get_num()

slack = my_prob.solution.get_linear_slacks()
x = my_prob.solution.get_values()

print('x: ')
print(x)
