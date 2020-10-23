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


df = pd.read_csv(
    r'C:\Users\37176\Desktop\开始学习\从零开始的机器学习\蓝桥 机器学习\3.实验 决策树和K近邻分类/telecom_churn.csv')

# factorize函数可以将Series中的标称型数据映射称为一组数字，相同的标称型映射为相同的数字

df['International plan'] = pd.factorize(df['International plan'])[0]
df['Voice mail plan'] = pd.factorize(df['Voice mail plan'])[0]


df['Churn'] = df['Churn'].astype('int')
states = df['State']
y = df['Churn']
# 去掉了 state 和 离网率 这两列
df.drop(['State', 'Churn'], axis=1, inplace=True)



from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

# 将数据集的 70% 划分为训练集（X_train,y_train），30% 划分为留置集（X_holdout,y_holdout）
X_train, X_holdout, y_train, y_holdout = train_test_split(df.values, y, test_size=0.3,
                                                          random_state=17)

# 训练两个模型：决策树和 k-NN
# 使用随机参数方法，假定树深（max_dept）为 5，近邻数量（n_neighbors）为 10
tree = DecisionTreeClassifier(max_depth=5, random_state=17)
knn = KNeighborsClassifier(n_neighbors=10)

tree.fit(X_train, y_train)
knn.fit(X_train, y_train)

# 使用准确率（Accuracy）在留置集上评价模型预测的质量
from sklearn.metrics import accuracy_score

# 决策树的准确率
tree_pred = tree.predict(X_holdout)
accuracy_score(y_holdout, tree_pred)

# k-NN 的准确率
knn_pred = knn.predict(X_holdout)
accuracy_score(y_holdout, knn_pred)



'================================='

# 使用交叉验证确定树的参数，对每次分割的 max_dept（最大深度 h）和 max_features（最大特征数）进行调优
# GridSearchCV() 函数可以非常简单的实现交叉验证
# 下面程序对每一对 max_depth 和 max_features 的值使用 5 折验证计算模型的表现

from sklearn.model_selection import GridSearchCV, cross_val_score

tree_params = {'max_depth': range(5, 7),
               'max_features': range(16, 18)}

tree_grid = GridSearchCV(tree, tree_params,
                         cv=5, n_jobs=-1, verbose=True)

tree_grid.fit(X_train, y_train)

# 交叉验证得出的最佳参数
tree_grid.best_params_

# 相应的训练集准确率均值
tree_grid.best_score_

accuracy_score(y_holdout, tree_grid.predict(X_holdout))

# 绘制所得的决策树
dot_data = StringIO()
export_graphviz(tree_grid.best_estimator_, feature_names=df.columns,
                out_file=dot_data, filled=True)
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
Image(value=graph.create_png())



'========================='
# 再次使用交叉验证对 k-NN 的 k 值（即邻居数）进行调优

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

knn_pipe = Pipeline([('scaler', StandardScaler()),
                     ('knn', KNeighborsClassifier(n_jobs=-1))])

knn_params = {'knn__n_neighbors': range(6, 8)}

knn_grid = GridSearchCV(knn_pipe, knn_params,
                        cv=5, n_jobs=-1,
                        verbose=True)

knn_grid.fit(X_train, y_train)

knn_grid.best_params_, knn_grid.best_score_



accuracy_score(y_holdout, knn_grid.predict(X_holdout))



'====================================='
# 使用 RandomForestClassifier() 方法再训练一个随机森林

from sklearn.ensemble import RandomForestClassifier

forest = RandomForestClassifier(n_estimators=100, n_jobs=-1,
                                random_state=17)
np.mean(cross_val_score(forest, X_train, y_train, cv=5))





forest_params = {'max_depth': range(8, 10),
                 'max_features': range(5, 7)}

forest_grid = GridSearchCV(forest, forest_params,
                           cv=5, n_jobs=-1, verbose=True)

forest_grid.fit(X_train, y_train)
forest_grid.best_params_, forest_grid.best_score_




accuracy_score(y_holdout, forest_grid.predict(X_holdout))