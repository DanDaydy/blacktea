import warnings
import pydotplus
from io import StringIO
from IPython.display import SVG
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
import warnings
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
sns.set()
warnings.filterwarnings('ignore')




# 第一类
np.random.seed(17)
# 随机数，正态分布，100行2列，默认的正态分布中心0
train_data = np.random.normal(size=(100, 2))
train_labels = np.zeros(100)



# 第二类
# r_按列连接两个矩阵，loc参数指的是正态分布的中心
train_data = np.r_[train_data, np.random.normal(size=(100, 2), loc=2)]
train_labels = np.r_[train_labels, np.ones(100)]


#绘制数据。通俗地讲，这种情况下的分类问题就是构造一个「边界」，能够较好的分开两个类别（红点和黄点）
plt.figure(figsize=(10, 8))
#散点图，x，y;c是颜色，这里按照标签0或1上色;s...;camp,Colormap;edgecolors,点的描边颜色;linewidth,描边宽度
plt.scatter(train_data[:, 0], train_data[:, 1], c=train_labels, s=100,
            cmap='autumn', edgecolors='black', linewidth=1.5)
plt.plot(range(-2, 5), range(4, -3, -1))


from sklearn.tree import DecisionTreeClassifier

# 编写一个辅助函数，返回之后的可视化网格
def get_grid(data):
    x_min, x_max = data[:, 0].min() - 1, data[:, 0].max() + 1
    y_min, y_max = data[:, 1].min() - 1, data[:, 1].max() + 1
    #np.meshgrid,生成网格点坐标矩阵
    return np.meshgrid(np.arange(x_min, x_max, 0.01), np.arange(y_min, y_max, 0.01))


#  标准用信息熵;max_depth参数限制决策树的深度;随机数种子17
clf_tree = DecisionTreeClassifier(criterion='entropy', max_depth=3,
                                  random_state=17)

# 训练决策树
clf_tree.fit(train_data, train_labels)

# 可视化
xx, yy = get_grid(train_data)
# ravel()将多维数组转化为一维数组
predicted = clf_tree.predict(np.c_[xx.ravel(),
                                   yy.ravel()]).reshape(xx.shape)
plt.pcolormesh(xx, yy, predicted, cmap='autumn')
plt.scatter(train_data[:, 0], train_data[:, 1], c=train_labels, s=100,
            cmap='autumn', edgecolors='black', linewidth=1.5)



'''
通过 pydotplus 和 export_graphviz 库我们可以方便的看到决策树本身是怎样的。
使用 StringIO() 函数开辟一个缓存空间保存决策树，
通过 export_graphviz() 函数以 DOT 格式导出决策树的 GraphViz 表示，
然后将其写入 out_file 中。使用 graph_from_dot_data() 函数读入数据
并通过 Image() 函数显示决策树。
'''
from ipywidgets import Image
from io import StringIO
import pydotplus
from sklearn.tree import export_graphviz


dot_data = StringIO()
export_graphviz(clf_tree, feature_names=['x1', 'x2'],
                out_file=dot_data, filled=True)
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
Image(value=graph.create_png())




'============================'


#小例子
data = pd.DataFrame({'Age': [17, 64, 18, 20, 38, 49, 55, 25, 29, 31, 33],
                     'Loan Default': [1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1]})

#按照年龄升序排列
data.sort_values('Age')

#训练一个决策树模型
age_tree = DecisionTreeClassifier(random_state=17)
age_tree.fit(data['Age'].values.reshape(-1, 1), data['Loan Default'].values)

#可视化
dot_data = StringIO()
export_graphviz(age_tree, feature_names=['Age'],
                out_file=dot_data, filled=True)
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
Image(value=graph.create_png())


'==================='
#把薪水加进去的例子
data2 = pd.DataFrame({'Age':  [17, 64, 18, 20, 38, 49, 55, 25, 29, 31, 33],
                      'Salary': [25, 80, 22, 36, 37, 59, 74, 70, 33, 102, 88],
                      'Loan Default': [1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1]})

#如果根据年龄排序，目标变量（Loan Default）将切换（从 1 到 0 或从 0 到 1）5 次
data2.sort_values('Age')
#如果根据薪水排序，它将切换 7 次
data2.sort_values('Salary')

#训练决策树
age_sal_tree = DecisionTreeClassifier(random_state=17)
age_sal_tree.fit(data2[['Age', 'Salary']].values, data2['Loan Default'].values)

#可视化
dot_data = StringIO()
export_graphviz(age_sal_tree, feature_names=['Age', 'Salary'],
                out_file=dot_data, filled=True)
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
Image(value=graph.create_png())


'=================================='


#带噪声的数据

from sklearn.tree import DecisionTreeRegressor
n_train = 150
n_test = 1000
noise = 0.1

#函数
def f(x):
    x = x.ravel()
    return np.exp(-x ** 2) + 1.5 * np.exp(-(x - 2) ** 2)

#生成函数
def generate(n_samples, noise):
    X = np.random.rand(n_samples) * 10 - 5
    X = np.sort(X).ravel()
    y = np.exp(-X ** 2) + 1.5 * np.exp(-(X - 2) ** 2) + \
        np.random.normal(0.0, noise, n_samples)
    X = X.reshape((n_samples, 1))
    return X, y

#数据
X_train, y_train = generate(n_samples=n_train, noise=noise)
X_test, y_test = generate(n_samples=n_test, noise=noise)

#训练决策树模型
reg_tree = DecisionTreeRegressor(max_depth=5, random_state=17)

reg_tree.fit(X_train, y_train)
reg_tree_pred = reg_tree.predict(X_test)

#可视化
plt.figure(figsize=(10, 6))
plt.plot(X_test, f(X_test), "b")
plt.scatter(X_train, y_train, c="b", s=20)
plt.plot(X_test, reg_tree_pred, "g", lw=2)
plt.xlim([-5, 5])
plt.title("Decision tree regressor, MSE = %.2f" %
          (np.sum((y_test - reg_tree_pred) ** 2) / n_test))
plt.show()