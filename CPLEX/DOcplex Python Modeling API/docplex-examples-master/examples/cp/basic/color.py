# --------------------------------------------------------------------------
# Source file provided under Apache License, Version 2.0, January 2004,
# http://www.apache.org/licenses/
# (c) Copyright IBM Corp. 2015, 2016
# --------------------------------------------------------------------------

"""
The problem involves choosing colors for the countries on a map in
such a way that at most four colors (blue, white, yellow, green) are
used and no neighboring countries are the same color. In this exercise,
you will find a solution for a map coloring problem with six countries:
Belgium, Denmark, France, Germany, Luxembourg, and the Netherlands.

问题涉及为地图上的国家/地区选择颜色
这样最多可以显示四种颜色（蓝色，白色，黄色，绿色）
使用过，并且没有邻国使用相同的颜色。 在本练习中，您将找到六个国家/地区的地图着色问题的解决方案：
比利时，丹麦，法国，德国，卢森堡和荷兰。


Please refer to documentation for appropriate setup of solving configuration.
"""

from docplex.cp.model import CpoModel

# Create CPO model
mdl = CpoModel()

# Create model variables containing colors of the countries
#创建包含国家/地区颜色的模型变量  创建了6个整数变量，后面依次是  下界   上界   名字
Belgium     = mdl.integer_var(0, 3, "Belgium")
Denmark     = mdl.integer_var(0, 3, "Denmark")
France      = mdl.integer_var(0, 3, "France")
Germany     = mdl.integer_var(0, 3, "Germany")
Luxembourg  = mdl.integer_var(0, 3, "Luxembourg")
Netherlands = mdl.integer_var(0, 3, "Netherlands")
ALL_COUNTRIES = (Belgium, Denmark, France, Germany, Luxembourg, Netherlands)
        
# Create constraints
#直接写成数学约束的形式    比利时跟法国不一样，比利时跟德国不一样 等等
mdl.add(Belgium != France)
mdl.add(Belgium != Germany)
mdl.add(Belgium != Netherlands)
mdl.add(Belgium != Luxembourg)
mdl.add(Denmark != Germany)
mdl.add(France  != Germany)
mdl.add(France  != Luxembourg)
mdl.add(Germany != Luxembourg)
mdl.add(Germany != Netherlands)

# Solve model
print("\nSolving model....")
msol = mdl.solve(TimeLimit=10)

if msol:
    print("Solution status: " + msol.get_solve_status())
    colors = ("Yellow", "Red", "Green", "Blue")
    for country in ALL_COUNTRIES:
        print("   " + country.get_name() + ": " + colors[msol[country]])
else:
    print("No solution found")

# Print solver log
# print("\nSolver log:")
# print(msol.get_solver_log())
