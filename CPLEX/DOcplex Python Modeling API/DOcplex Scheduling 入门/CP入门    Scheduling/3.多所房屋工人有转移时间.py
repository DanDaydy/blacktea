import sys
import sys
from docplex.cp.model import *

mdl2 = CpoModel()

'''  ==========data=========='''
NbHouses = 5

WorkerNames = ["Joe", "Jim"]

TaskNames = ["masonry", "carpentry", "plumbing",
             "ceiling", "roofing", "painting",
             "windows", "facade", "garden", "moving"]

Duration =  [35, 15, 40, 15, 5, 10, 5, 10, 5, 5]

Worker = {"masonry"  : "Joe" ,
          "carpentry": "Joe" ,
          "plumbing" : "Jim" ,
          "ceiling"  : "Jim" ,
          "roofing"  : "Joe" ,
          "painting" : "Jim" ,
          "windows"  : "Jim" ,
          "facade"   : "Joe" ,
          "garden"   : "Joe" ,
          "moving"   : "Jim"}

ReleaseDate = [  0,     0,   151,    59,   243]
DueDate     = [120,   212,   304,   181,   425]
Weight      = [100.0, 100.0, 100.0, 200.0, 100.0]

Precedences = [("masonry", "carpentry"),("masonry", "plumbing"),
               ("masonry", "ceiling"), ("carpentry", "roofing"),
               ("ceiling", "painting"), ("roofing", "windows"),
               ("roofing", "facade"), ("plumbing", "facade"),
               ("roofing", "garden"), ("plumbing", "garden"),
               ("windows", "moving"), ("facade", "moving"),
               ("garden", "moving"), ("painting", "moving")]

Houses = range(NbHouses)

'''==================================='''


# 房子的区间变量              开始时间是  [最早可以开始时间，+无穷)      名字是    house i
houses = [mdl2.interval_var(start=(ReleaseDate[i], INTERVAL_MAX), name="house"+str(i)) for i in Houses]

#任务的区间变量
#任务的区间变量的矩阵itvs   size = 任务的持续时间，  名字 =  （例如   0_carpentry)
TaskNames_ids = {}
itvs = {}
for h in Houses:
    for i,t in enumerate(TaskNames):
        _name = str(h)+"_"+str(t)
        itvs[(h,t)] = mdl2.interval_var(size=Duration[i], name=_name)
        TaskNames_ids[_name] = i

#任务的优先级约束
#某个任务结束之后另一个任务才能开始
for h in Houses:
    for p in Precedences:
        mdl2.add(mdl2.end_before_start(itvs[(h, p[0])], itvs[(h, p[1])]))

#跨度约束   房屋的区间变量要跨越它包含任务的区间变量
for h in Houses:
    mdl2.add( mdl2.span(houses[h], [itvs[(h,t)] for t in TaskNames] ) )

#转移的时间矩阵           这里其实是简单的说转移时间是房子编号之间的绝对值
transitionTimes = transition_matrix([[int(abs(i - j)) for j in Houses] for i in Houses])

'''
这个矩阵实际上是
#numpy
for i in Houses:
    for j in Houses:
        matrix[i][j] = int(abs(i-j))
'''


#工人任务的序列变量  （区间变量的列表）
#三个参数   vars(区间变量的列表)    类型     名字
workers = {w : mdl2.sequence_var([ itvs[(h,t)] for h in Houses for t in TaskNames if Worker[t]==w ],
                                types=[h for h in Houses for t in TaskNames if Worker[t]==w ], name="workers_"+w)
           for w in WorkerNames}

#无重叠约束   参数：一个时间序列   转移的时间矩阵
#这个约束会限制这个时间序列在时间线上不重叠，如果给出来转移的时间矩阵它会在两个区间变量之间
#加上必须经过的最短时间。不存在的时间间隔会自动删了
#所以说这个约束是非常强大的...
for w in WorkerNames:
    mdl2.add( mdl2.no_overlap(workers[w], transitionTimes) )

# create the obj and add it.
#sum(    每个房屋的滞期成本（单位滞期成本*天数）  +  工期  )    似乎看上去不是很靠谱
mdl2.add(
    mdl2.minimize(
        mdl2.sum(Weight[h] * mdl2.max([0, mdl2.end_of(houses[h])-DueDate[h]]) + mdl2.length_of(houses[h]) for h in Houses)
    )
)

# Solve the model
print("\nSolving model....")
msol2 = mdl2.solve(FailLimit=30000)
print("done")

if msol2:
    print("Cost will be " + str(msol2.get_objective_values()[0]))
else:
    print("No solution found")

# Viewing the results of sequencing problems in a Gantt chart
# (double click on the gantt to see details)
import docplex.cp.utils_visu as visu
import matplotlib.pyplot as plt
#matplotlib inline
#Change the plot size
from pylab import rcParams
rcParams['figure.figsize'] = 15, 3

def showsequence(msol, s, setup, tp):
    seq = msol.get_var_solution(s)
    visu.sequence(name=s.get_name())
    vs = seq.get_value()
    for v in vs:
        nm = v.get_name()
        visu.interval(v, tp[TaskNames_ids[nm]], nm)
    for i in range(len(vs) - 1):
        end = vs[i].get_end()
        tp1 = tp[TaskNames_ids[vs[i].get_name()]]
        tp2 = tp[TaskNames_ids[vs[i + 1].get_name()]]
        visu.transition(end, end + setup.get_value(tp1, tp2))
if msol2:
    visu.timeline("Solution for SchedSetup")
    for w in WorkerNames:
        types=[h for h in Houses for t in TaskNames if Worker[t]==w]
        showsequence(msol2, workers[w], transitionTimes, types)
    visu.show()


