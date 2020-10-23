

#随机交换两个城市,最多产生max_num个解
def find_neighbour_zero(path, weights, max_num):
    solution_neighbours = []
    for i in range(0, max_num):
        exchange = random.sample(range(1, len(path)-1), 2)
        temp_path = copy.deepcopy(path)
        temp_path[exchange[0]] = path[exchange[1]]
        temp_path[exchange[1]] = path[exchange[0]]

        if temp_path not in solution_neighbours:
            cost = fitness(temp_path, weights)
            solution_neighbours.append([temp_path, cost])
    return solution_neighbours

#随机翻转某个区间,产生最多max_num个邻居解
def find_neighbour_one(path, weights, max_num):
    solution_neighbours = []
    for i in range(0, max_num):
        # 随机选择两个端点, 不改变先后顺序
        endpoints = random.sample(range(1, len(path)-1), 2)
        endpoints.sort()
        temp_path = copy.deepcopy(path)
        temp_path[endpoints[0]:endpoints[1]] = list(reversed(temp_path[endpoints[0]:endpoints[1]]))
        if temp_path not in solution_neighbours:
            cost = fitness(temp_path, weights)
            solution_neighbours.append([temp_path, cost])
    return solution_neighbours

#随机找两个城市放到序列最前面,产生最多max_num个邻居解
def find_neighbour_two(path, weights, max_num):
    solution_neighbours = []
    for i in range(0, max_num):
        # 随机选择两个city, 不改变先后顺序
        endpoints = random.sample(range(1, len(path)-1), 2)
        endpoints.sort()
        temp_path = copy.deepcopy(path)
        temp_path.pop(endpoints[0])
        temp_path.pop(endpoints[1] - 1)
        temp_path.insert(1, path[endpoints[0]])
        temp_path.insert(2, path[endpoints[1]])
        if temp_path not in solution_neighbours:
            cost = fitness(temp_path, weights)
            solution_neighbours.append([temp_path, cost])
    return solution_neighbours





















def variable_neighbourhood_search(edge_points, weights, iters, neighbour_num, neighbour_func_sets, k_max=3, l_max=3):

    #绘图部分
    pyplot.close()
    fig = pyplot.figure()
    path_fig = fig.add_subplot(1, 2, 1)
    cost_fig = fig.add_subplot(1, 2, 2)
    path_fig.axis("equal")
    path_fig.set_title('Best Path')
    cost_fig.set_title('Best Cost')
    cost_fig.set_xlabel('iterations')
    cost_fig.set_ylabel('fitness')
    pyplot.subplots_adjust(wspace= 0.5)
    pyplot.ion()#打开交互
    path_fig.scatter([i[0] for i in edge_points], [i[1] for i in edge_points], s=2 ,color='red')
    pyplot.pause(0.001)

    first_path = [i for i in range(0, len(weights))]
    first_path.append(0)
    best_solution = [first_path, fitness(first_path,weights)]

    cost_history = list()
    cost_history.append(best_solution[1])
    for it in range(0, iters):

        #更新绘图
        cost_fig.plot(cost_history, color='b')
        path_fig.plot([edge_points[p][0] for p in best_solution[0]], [edge_points[p][1] for p in best_solution[0]], color='b', linewidth=1)
        pyplot.pause(0.001)
        path_fig.lines.pop(0)

        k = 0
        while k < k_max:

            #shaking
            s_1 = random.sample(neighbour_func_sets[k](best_solution[0], weights, neighbour_num), 1)[0]

            #local_search return x_0
            x_0 = copy.deepcopy(s_1)
            l = 0
            while l < l_max:
                neighbour_solution = neighbour_func_sets[l](x_0[0], weights, neighbour_num)
                neighbour_solution.sort(key= lambda x: x[1])
                x_1 = neighbour_solution[0] #findbestsolution
                if x_1[1] < x_0[1]:
                    x_0 = x_1
                    l = 1
                else:
                    l = l + 1
            
            #move or not
            if x_0[1] < best_solution[1]:
                best_solution = x_0
                k = 1
            else:
                k = k + 1

        cost_history.append(best_solution[1])
        print("iterations: %d, best cost:%.2f"%(it, best_solution[1]))
    path_fig.plot([edge_points[p][0] for p in best_solution[0]], [edge_points[p][1] for p in best_solution[0]], color='b', linewidth=1)
    pyplot.savefig('result.jpg')
    return best_solution







neighbourhood_funcs = [find_neighbour_zero, find_neighbour_one, find_neighbour_two]
variable_neighbourhood_search(edge, weights, opt.iters, opt.num, neighbourhood_funcs)

