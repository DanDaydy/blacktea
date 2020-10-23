#!/usr/bin/env python
# coding: utf-8

# # Chapter 7. Using state functions: house building with state incompatibilities

# 这里有两个工人，每个任务需要两个工人中的一个。 一部分任务要求房子打扫干净，而其他任务则使房子变脏。 需要一个过渡时间才能将房屋的状态从脏到干净。

# Problem to be solved
# 
# 问题在于，以计划满足时间约束并使表达式最小化的方式，将开始日期分配给一组任务。 此问题的目的是最大程度地减少总的完成日期。
# 
# 对于房屋建筑项目中的每种任务类型，下表显示了以天为单位的任务工期以及任务期间的房屋状态。 一个工人一次只能完成一项任务。 每个任务一旦开始，就不会被打断。
# 
# Task 	Duration 	State 	Preceding tasks
# masonry 	35  	dirty 	
# carpentry 	15 	    dirty 	 masonry
# plumbing 	40 	    clean 	 masonry
# ceiling 	15 	    clean 	 masonry
# roofing 	5 	    dirty 	 carpentry
# painting 	10 	    clean    ceiling
# windows 	5 	    dirty 	 roofing
# facade 	    10 		         roofing, plumbing
# garden 	    5 		         roofing, plumbing
# moving   	5 		         windows, facade,garden, painting
# 
# 解决问题包括确定任务的开始日期，以使总的完成日期最小化。
# 

# ----->Step 1: Describe the problem
# 
# What is the known information in this problem ?
# 
#     两名工人要建造五栋房屋。 对于每个房屋，有十个房屋建造任务，每个任务都有给定的大小。 对于每个任务，都有一个必须启动的任务列表。 有两个工人。 与将房屋的状态由脏变到干净相关的过渡时间。
#     
# What are the decision variables or unknowns in this problem ?
# 
#     未知数是每个任务开始的日期。 费用由分配的开始日期确定。
#     
# What are the constraints on these variables ?
# 
#     有一些约束条件指定特定任务可能要等到一个或多个给定任务完成后才能开始。 每个任务都需要两个工人之一。 有些任务具有指定的房屋清洁状态。
#     
# What is the objective ?
# 
#     目的是最大程度地减少总体完成日期。
#     

# ----->Step 2: Prepare data
# 
# 在相关数据中，提供的数据包括房屋数量（NbHouses），工人数量（NbWorkers），任务名称（TaskNames），任务大小（Duration），优先级关系（Precedences）， 以及每个任务的清洁状态（AllStates）。
# 
# 

# In[1]:


NbHouses = 5
NbWorkers = 2
AllStates = ["clean", "dirty"]

TaskNames = ["masonry","carpentry", "plumbing", "ceiling","roofing","painting","windows","facade","garden","moving"]

Duration =  [35,15,40,15,5,10,5,10,5,5]

States = [("masonry","dirty"),("carpentry","dirty"),("plumbing","clean"),
          ("ceiling","clean"),("roofing","dirty"),("painting","clean"),
          ("windows","dirty")]

Precedences = [("masonry","carpentry"),("masonry","plumbing"),("masonry","ceiling"),
               ("carpentry","roofing"),("ceiling","painting"),("roofing","windows"),
               ("roofing","facade"),("plumbing","facade"),("roofing","garden"),
               ("plumbing","garden"),("windows","moving"),("facade","moving"),
               ("garden","moving"),("painting","moving")]


# In[ ]:


Houses = range(NbHouses)


# ----->Step 2Step 3: Create the interval variables

# In[ ]:


import sys
from docplex.cp.model import *


# In[ ]:


mdl6 = CpoModel()


# In[ ]:



task = {}
for h in Houses:
    for i,t in enumerate(TaskNames):
        task[(h,t)] = mdl6.interval_var(size = Duration[i])


# ----->Step 4: Declare the worker usage functions
# 
# 就像第5章“在房屋建筑问题中使用累积函数”一样，每个任务从任务间隔的开始到结束都需要一名工人。 为了表示任务需要工作人员这一事实，创建了一个累积函数表达式工作人员。 限制此功能在任何时间点都不能超过工人人数。 功能脉冲在间隔上以给定量调整表达式。 将所有间隔变量上的这些脉冲原子相加得到一个表达式，该表达式表示工人在建造房屋的整个时间范围内的使用情况。
# 

# In[ ]:



workers = step_at(0, 0)
for h in Houses:
    for t in TaskNames:
        workers += mdl6.pulse(task[h,t], 1)


# ----->Step 5: Create the transition times
# 
# 从脏状态到清洁状态的过渡时间对于所有房屋都是相同的。 如示例第3章“为房屋建筑问题添加工人和过渡时间”中所示，创建了元组ttime来表示清洁状态之间的过渡时间。
# 

# In[2]:


Index = {s : i for i,s in enumerate(AllStates)}


# In[ ]:


ttvalues = [[0, 0], [0, 0]]
ttvalues[Index["dirty"]][Index["clean"]] = 1
ttime = transition_matrix(ttvalues, name='TTime')


# ----->Step 6: Declare the state function
# 某些任务要求房子清洁，而其他任务则使房子脏。 为了对房屋的可能状态建模，状态函数用于表示时间上不相交的状态。
#     
# 状态函数是描述环境给定特征的演变的函数。 此功能的可能演变受到问题间隔变量的限制。 例如，调度问题可能包含状态随时间变化的资源。 资源状态可能由于计划的活动或外部事件而改变； 计划中的某些活动可能需要特定的资源状态才能执行。 区间变量对状态函数有绝对影响，要求该函数值等于特定状态或可能状态集。

# In[ ]:


state = { h : state_function(ttime, name="house"+str(h)) for h in Houses}


# ----->Step 7: Add the constraints
# 
# 为了对任务要求或施加的状态进行建模，将创建一个约束来指定代表该任务的整个时间间隔变量中房屋的状态。
# 
# 约束always_equal（）指定间隔变量上的状态函数的值。 约束将状态函数，间隔变量和状态值作为参数。 只要存在间隔变量，就在间隔变量的开始和结束之间的任何位置定义状态函数，并且在此间隔内，状态函数将保持等于指定的状态值。 在要求房屋处于特定状态的任务期间，状态函数被约束为采用适当的值。 为了增加在给定时间只能有两个工作人员的约束，代表工作人员使用情况的累积函数表达式被限制为不大于值NbWorkers。

# In[ ]:


for h in Houses:
    for p in Precedences:
        mdl6.add( mdl6.end_before_start(task[h,p[0]], task[h,p[1]]) )

    for s in States:
        mdl6.add( mdl6.always_equal(state[h], task[h,s[0]], Index[s[1]]) )

mdl6.add( workers <= NbWorkers )


# ----->Step 8: Add the objective

# In[ ]:


mdl6.add(mdl6.minimize( mdl6.max( mdl6.end_of(task[h,"moving"]) for h in Houses )))


# ----->Step 9: Solve the model

# In[ ]:


# Solve the model
print("\nSolving model....")
msol6 = mdl6.solve(FailLimit=30000)
print("done")


# In[ ]:


if msol6:
    print("Cost will be " + str( msol6.get_objective_values()[0] ))

    import docplex.cp.utils_visu as visu
    import matplotlib.pyplot as plt
    get_ipython().run_line_magic('matplotlib', 'inline')
    #Change the plot size
    from pylab import rcParams
    rcParams['figure.figsize'] = 15, 3

    workers_function = CpoStepFunction()
    for h in Houses:
        for t in TaskNames:
            itv = msol6.get_var_solution(task[h,t])
            workers_function.add_value(itv.get_start(), itv.get_end(), 1)

    visu.timeline('Solution SchedState')
    visu.panel(name="Schedule")
    for h in Houses:
        for t in TaskNames:
            visu.interval(msol6.get_var_solution(task[h,t]), h, t)


    visu.panel(name="Houses state")
    for h in Houses:
        f = state[h]
        visu.sequence(name=f.get_name(), segments=msol6.get_var_solution(f))
    visu.panel(name="Nb of workers")
    visu.function(segments=workers_function, style='line')
    visu.show()
else:
    print("No solution found")

