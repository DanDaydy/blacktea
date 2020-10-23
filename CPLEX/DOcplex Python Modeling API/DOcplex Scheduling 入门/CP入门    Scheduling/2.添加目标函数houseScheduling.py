import sys
from docplex.cp.model import *
import docplex.cp.utils_visu as visu
import matplotlib.pyplot as plt
#Change the plot size
from pylab import rcParams
rcParams['figure.figsize'] = 15, 3

mdl1 = CpoModel()

masonry = mdl1.interval_var(size=35)
carpentry = mdl1.interval_var(size=15)
plumbing = mdl1.interval_var(size=40)
ceiling = mdl1.interval_var(size=15)
roofing = mdl1.interval_var(size=5)
painting = mdl1.interval_var(size=10)
windows = mdl1.interval_var(size=5)
facade = mdl1.interval_var(size=10)
garden = mdl1.interval_var(size=5)
moving = mdl1.interval_var(size=5)

mdl1.add( mdl1.end_before_start(masonry, carpentry) )
mdl1.add( mdl1.end_before_start(masonry, plumbing) )
mdl1.add( mdl1.end_before_start(masonry, ceiling) )
mdl1.add( mdl1.end_before_start(carpentry, roofing) )
mdl1.add( mdl1.end_before_start(ceiling, painting) )
mdl1.add( mdl1.end_before_start(roofing, windows) )
mdl1.add( mdl1.end_before_start(roofing, facade) )
mdl1.add( mdl1.end_before_start(plumbing, facade) )
mdl1.add( mdl1.end_before_start(roofing, garden) )
mdl1.add( mdl1.end_before_start(plumbing, garden) )
mdl1.add( mdl1.end_before_start(windows, moving) )
mdl1.add( mdl1.end_before_start(facade, moving) )
mdl1.add( mdl1.end_before_start(garden, moving) )
mdl1.add( mdl1.end_before_start(painting, moving) )

obj = mdl1.minimize(  400 * mdl1.max([mdl1.end_of(moving) - 100, 0])
                    + 200 * mdl1.max([25 - mdl1.start_of(masonry), 0])
                    + 300 * mdl1.max([75 - mdl1.start_of(carpentry), 0])
                    + 100 * mdl1.max([75 - mdl1.start_of(ceiling), 0]) )
mdl1.add(obj)

# Solve the model
print("\nSolving model....")
msol1 = mdl1.solve(TimeLimit=20)
print("done")

if msol1:
    print("Cost will be " + str(msol1.get_objective_values()[0]))

    var_sol = msol1.get_var_solution(masonry)
    print("Masonry : {}..{}".format(var_sol.get_start(), var_sol.get_end()))
    var_sol = msol1.get_var_solution(carpentry)
    print("Carpentry : {}..{}".format(var_sol.get_start(), var_sol.get_end()))
    var_sol = msol1.get_var_solution(plumbing)
    print("Plumbing : {}..{}".format(var_sol.get_start(), var_sol.get_end()))
    var_sol = msol1.get_var_solution(ceiling)
    print("Ceiling : {}..{}".format(var_sol.get_start(), var_sol.get_end()))
    var_sol = msol1.get_var_solution(roofing)
    print("Roofing : {}..{}".format(var_sol.get_start(), var_sol.get_end()))
    var_sol = msol1.get_var_solution(painting)
    print("Painting : {}..{}".format(var_sol.get_start(), var_sol.get_end()))
    var_sol = msol1.get_var_solution(windows)
    print("Windows : {}..{}".format(var_sol.get_start(), var_sol.get_end()))
    var_sol = msol1.get_var_solution(facade)
    print("Facade : {}..{}".format(var_sol.get_start(), var_sol.get_end()))
    var_sol = msol1.get_var_solution(moving)
    print("Moving : {}..{}".format(var_sol.get_start(), var_sol.get_end()))
else:
    print("No solution found")

if msol1:
    wt = msol1.get_var_solution(masonry)
    visu.interval(wt, 'lightblue', 'masonry')
    wt = msol1.get_var_solution(carpentry)
    visu.interval(wt, 'lightblue', 'carpentry')
    wt = msol1.get_var_solution(plumbing)
    visu.interval(wt, 'lightblue', 'plumbing')
    wt = msol1.get_var_solution(ceiling)
    visu.interval(wt, 'lightblue', 'ceiling')
    wt = msol1.get_var_solution(roofing)
    visu.interval(wt, 'lightblue', 'roofing')
    wt = msol1.get_var_solution(painting)
    visu.interval(wt, 'lightblue', 'painting')
    wt = msol1.get_var_solution(windows)
    visu.interval(wt, 'lightblue', 'windows')
    wt = msol1.get_var_solution(facade)
    visu.interval(wt, 'lightblue', 'facade')
    wt = msol1.get_var_solution(moving)
    visu.interval(wt, 'lightblue', 'moving')
    visu.show()