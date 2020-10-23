

# first import the Model class from docplex.mp
from docplex.mp.model import Model

# create one model instance, with a name
m = Model(name='telephone_production')


#决策变量
# by default, all variables in Docplex have a lower bound of 0 and infinite upper bound
desk = m.integer_var(name='desk')
cell = m.integer_var(name='cell')

#目标函数
m.maximize(12 * desk + 20 * cell)


# 约束条件
# constraint #1: desk production is greater than 100
m.add_constraint(desk >= 100, "desk")

# constraint #2: cell production is greater than 100
m.add_constraint(cell >= 100, "cell")

# constraint #3: assembly time limit
ct_assembly = m.add_constraint( 0.2 * desk + 0.4 * cell <= 400, "assembly_limit")

# constraint #4: paiting time limit
ct_painting = m.add_constraint( 0.5 * desk + 0.4 * cell <= 490, "painting_limit")



m.print_information()
msol = m.solve()

assert msol is not None, "model can't solve"
m.print_solution()



#==============================

#开始修改模型     改变最大生产数量，改变最小生产数量限制
# Access by name
m.get_var_by_name("desk").ub = 2000
# acess via the object
cell.ub = 1000


m.get_constraint_by_name("desk").rhs = 350
m.get_constraint_by_name("cell").rhs = 350

msol = m.solve()
assert msol is not None, "model can't solve"
m.print_solution()



#==================================
#添加一种新的  “混合型”电话

hybrid = m.integer_var(name='hybrid')

m.add_constraint(hybrid >= 350)

m.get_objective_expr().add_term(hybrid, 10)

m.get_constraint_by_name("assembly_limit").lhs.add_term(hybrid, 0.2)
ct_painting.lhs.add_term(hybrid, 0.2)

msol = m.solve()
assert msol is not None, "model can't solve"
m.print_solution()


#=======================================
#批量改变了   涂装约束里左边的系数
ct_painting.lhs.set_coefficients([(desk, 0.1), (cell, 0.1), (hybrid, 0.1)])

msol = m.solve()
assert msol is not None, "model can't solve"
m.print_solution()

#========================================
#添加一个抛光时间约束

ct_polishing = m.add_constraint( 0.6 * desk + 0.6 * cell + 0.3 * hybrid <= 290, "polishing_limit")

msol = m.solve()
if msol is None:
    print("model can't solve")

#这里就是无解的了

#=======================================
#引入 relaxer       按照某些规则来放松约束条件

ct_polishing.name = "high_"+ct_polishing.name
ct_assembly.name = "low_"+ct_assembly.name
ct_painting.name = "medium_"+ct_painting.name

# if a name contains "low", it has priority LOW
# if a ct name contains "medium" it has priority MEDIUM
# same for HIGH
# if a constraint has no name or does not match any, it is not relaxable.
from docplex.mp.relaxer import Relaxer
relaxer = Relaxer(prioritizer='match', verbose=True)

relaxed_sol = relaxer.relax(m)
relaxed_ok = relaxed_sol is not None
assert relaxed_ok, "relaxation failed"
relaxer.print_information()

m.print_solution()

ct_polishing_relax = relaxer.get_relaxation(ct_polishing)
print("* found slack of {0} for polish ct".format(ct_polishing_relax))
ct_polishing.rhs+= ct_polishing_relax
m.solve()
m.report()
m.print_solution()