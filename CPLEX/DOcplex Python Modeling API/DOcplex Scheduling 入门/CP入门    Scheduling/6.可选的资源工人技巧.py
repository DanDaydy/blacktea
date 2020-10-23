#!/usr/bin/env python
# coding: utf-8

# # Chapter 6. Using alternative resources in the house building problem

# The following concepts are presented:
# 
#     use the constraints alternative and presence_of,
#     use the function optional.
# 
# 每个房子都有一个最大的完成日期。 此外，有三名工人，每个任务需要三名工人之一。 三名工人在各种任务上的技能水平各不相同； 如果工人没有完成特定任务的技能，则可能不会分配给他。 对于某些任务对，如果特定工人在房屋上执行一对作业中的一个，则必须将同一工人分配给该房屋中一对作业中的另一个。 目的是找到一种解决方案，以最大化分配给任务的工人的任务相关技能水平。

# Problem to be solved
# 
# 问题在于，以计划满足时间限制并最大化标准的方式，将开始日期分配给一组任务。 该问题的标准是使分配给任务的工人的任务相关技能水平最大化。
# 
# ask 	Duration 	Preceding tasks
# masonry 	35 	
# carpentry   15 	    masonry
# plumbing    40  	masonry
# ceiling 	15 	    masonry
# roofing 	5 	    carpentry
# painting 	10 	    ceiling
# windows 	5    	roofing
# facade  	10 	 roofing, plumbing
# garden  	5 	roofing, plumbing
# moving 	    5    windows, facade, garden,painting
# 
# 每个房子必须在300天内完成。 在这十项任务中，有三名工人的技能水平各不相同。 如果工人的一项任务技能水平为零，则可能不会被分配给该任务。
# 
# Task 	Joe 	Jack 	Jim
# masonry 	9 	5 	0
# carpentry   7 	0 	5
# plumbing    0 	7 	0
# ceiling 	5 	8 	0
# roofing 	6 	7 	0
# painting 	0 	9 	6
# windows 	8 	0 	5
# façade  	5 	5 	0
# garden  	5 	5 	9
# moving  	6 	0 	8
# 
# 对于杰克来说，如果他在房屋上执行屋顶任务或立面任务，则他必须在该房屋上执行其他任务。 对于Jim而言，如果他在房子上执行花园任务或移动任务，则他必须在该房子上执行其他任务。
# 对于Joe，如果他在房屋上执行砌石任务或木工任务，则他必须在该房屋上执行其他任务。 另外，如果Joe在房屋上执行木工任务或屋顶任务，则他必须在该房屋上执行其他任务。

# ----->Step 1: Describe the problem
# 
# 
# What is the known information in this problem ?
# 
#     三名工人将建造五栋房屋。 对于每个房屋，有十个房屋建造任务，每个任务都有给定的大小。 对于每个任务，都有一个必须启动的任务列表。 每个工人都有与每个任务相关的技能水平。 这五座房子的工作有一个总体截止日期。
#     
#     
# What are the decision variables or unknowns in this problem ?
# 
#     未知是每个任务将开始的时间点。 同样，未知哪个工人将被分配到每个任务。
#     
#     
# What are the constraints on these variables ?
# 
#     有一些约束条件指定特定任务可能要等到一个或多个给定任务完成后才能开始。 此外，还有一些约束条件指定每个任务必须分配一个工作人员，一次只能将一个工作人员分配给一个任务，并且只能将一个工作人员分配给他具有一定技能水平的任务。 。 有几对任务，如果房屋的一项任务是由特定工人完成的，则该房屋的另一项任务必须由同一工人完成。
#     
#     
# What is the objective ?
# 
#     目的是使所使用的技能水平最大化。

# ----->Step 2: Prepare data
# 
# 在相关的数据文件中，提供的数据包括房屋数量（NbHouses），工人的名称（Workers），任务的名称（Tasks），任务的大小（Durations），优先级关系（Precedences） ），以及房屋建造的总体截止日期（截止日期）。
# 
# 数据还包括一个元组，技能。 集合中的每个元组都包含一个工人，一个任务以及该工人对该任务具有的技能水平。 此外，还有一个元组集Continuities，它是一组三元组（一对任务和一个工人）。 如果一对工人中的两个任务中的一个是由工人为给定房屋执行的，那么一对中的另一个任务必须由该房屋中的同一工人来执行。
# 
# 

# In[1]:


NbHouses = 5
Deadline =  318

Workers = ["Joe", "Jack", "Jim"]

Tasks = ["masonry", "carpentry", "plumbing", "ceiling","roofing", "painting", "windows", "facade","garden", "moving"]

Durations =  [35, 15, 40, 15, 5, 10, 5, 10, 5, 5]


# In[2]:


Skills = [("Joe","masonry",9),("Joe","carpentry",7),("Joe","ceiling",5),("Joe","roofing",6), 
          ("Joe","windows",8),("Joe","facade",5),("Joe","garden",5),("Joe","moving",6),
          ("Jack","masonry",5),("Jack","plumbing",7),("Jack","ceiling",8),("Jack","roofing",7),
          ("Jack","painting",9),("Jack","facade",5),("Jack","garden",5),("Jim","carpentry",5),
          ("Jim","painting",6),("Jim","windows",5),("Jim","garden",9),("Jim","moving",8)]


# In[3]:


Precedences = [("masonry","carpentry"),("masonry","plumbing"),("masonry","ceiling"),
               ("carpentry","roofing"),("ceiling","painting"),("roofing","windows"),
               ("roofing","facade"),("plumbing","facade"),("roofing","garden"),
               ("plumbing","garden"),("windows","moving"),("facade","moving"),
               ("garden","moving"),("painting","moving")
              ]
 
Continuities = [("Joe","masonry","carpentry"),("Jack","roofing","facade"), 
                ("Joe","carpentry", "roofing"),("Jim","garden","moving")]


# In[4]:


nbWorkers = len(Workers)
Houses = range(NbHouses)


# ----->Step 3: Create the interval variables
# 区间变量
# 
#     在此模型中创建了两个区间变量矩阵。 第一个任务是在房屋和任务上建立索引，并且必须安排在[0..Deadline]间隔内。 
#     间隔变量的另一个矩阵在房屋和Skills元组上索引。 这些间隔变量是可选的，在解决方案中可能存在也可能不存在。 执行的间隔将代表哪个工作人员执行哪个任务。

# In[5]:


import sys
from docplex.cp.model import *


# In[6]:


mdl5 = CpoModel()


# In[7]:


tasks = {}
wtasks = {}
for h in Houses:
    for i,t in enumerate(Tasks):
        tasks[(h,t)] = mdl5.interval_var(start=[0,Deadline], size=Durations[i])
    for s in Skills:
        wtasks[(h,s)] = mdl5.interval_var(optional=True)


# Step 4: Add the temporal constraints
# 
#     优先级约束

# In[8]:


for h in Houses:
    for p in Precedences:
        mdl5.add( mdl5.end_before_start(tasks[h,p[0]], tasks[h,p[1]]) )


# ----->Step 5: Add the alternative constraints
# 
# 使用专门的约束Alternative（）约束解决方案，以便在解决方案中确切存在与给定房屋的给定任务相关联的区间变量任务之一
# 
# 约束Alternative（）在一个interval和一组interval之间创建一个约束，该约束指定如果解决方案中存在给定interval，then exactly one interval variable of the set is present in the solution.
# 
# 换句话说，考虑使用间隔变量a和间隔变量bs数组创建的替代约束。 如果解决方案中存在a，则将恰好存在bs中的间隔变量之一，并且a与该选定间隔一起开始和结束。
# 
# 
# 大白话，任务的区间变量，必须在第二个参数的这个区间变量集里面选一个
# 

# In[9]:


for h in Houses:
    for t in Tasks:
        mdl5.add( mdl5.alternative(tasks[h,t], [wtasks[h,s] for s in Skills if s[1]==t]) )


# 表达式presentation_of（）用于表示任务是否由工作人员执行。 如果存在区间变量，则约束presentation_of（）为true，如果解决方案中不存在区间变量，则约束为false。
# 
# For each house and each given pair of tasks and worker that must have continuity, a constraint states that if the interval variable for one of the two tasks for the worker is present, the interval variable associated with that worker and the other task must also be present.

# In[10]:




for h in Houses:
    for c in Continuities:
        for (worker1, task1, l1) in Skills:
            if worker1 == c[0] and task1 == c[1]:
                for (worker2, task2, l2) in Skills:
                    if worker2 == c[0] and task2 == c[2]:
                           mdl5.add(
                               mdl5.presence_of(wtasks[h,(c[0], task1, l1)]) 
                               == 
                               mdl5.presence_of(wtasks[h,(c[0], task2, l2)])
                           )


# ----->Step 7: Add the no overlap constraints
# 
#     约束no_overlap（）允许指定给定的工作人员在给定的时间只能分配一个任务。
# 

# In[11]:


for w in Workers:
    mdl5.add( mdl5.no_overlap([wtasks[h,s] for h in Houses for s in Skills if s[0]==w]) )


# ----->Step 8: Add the objective
# 
#     在解决方案中必须考虑到区间变量的存在。 因此，对于这些可能的任务中的每一个，成本都由技能水平与表示解决方案中存在区间变量的表达式的乘积来增加。 这个问题的目的是使用于所有任务的技能水平最大化，然后使表达最大化。

# In[12]:


mdl5.add(
    mdl5.maximize(
        mdl5.sum( s[2] * mdl5.presence_of(wtasks[h,s]) for h in Houses for s in Skills)
    )
)


# ----->Step 9: Solve the model

# In[13]:


# Solve the model
print("\nSolving model....")
msol5 = mdl5.solve(FailLimit=30000)
print("done")


# In[14]:


if msol5:
    print("Cost will be "+str( msol5.get_objective_values()[0] ))

    worker_idx = {w : i for i,w in enumerate(Workers)}
    worker_tasks = [[] for w in range(nbWorkers)]  # Tasks assigned to a given worker
    for h in Houses:
        for s in Skills:
            worker = s[0]
            wt = wtasks[(h,s)]
            worker_tasks[worker_idx[worker]].append(wt)

    import docplex.cp.utils_visu as visu
    import matplotlib.pyplot as plt
    #%matplotlib inline
    #Change the plot size
    from pylab import rcParams
    rcParams['figure.figsize'] = 15, 3

    visu.timeline('Solution SchedOptional', 0, Deadline)
    for i,w in enumerate(Workers):
        visu.sequence(name=w)
        for t in worker_tasks[worker_idx[w]]:
            wt = msol5.get_var_solution(t)
            if wt.is_present():
                #if desc[t].skills[w] == max(desc[t].skills):
                    # Green-like color when task is using the most skilled worker
                #    color = 'lightgreen'
                #else:
                        # Red-like color when task does not use the most skilled worker
                #    color = 'salmon'
                color = 'salmon'
                visu.interval(wt, color, wt.get_name())
    visu.show()
else:
    print("No solution found")

