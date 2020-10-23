import docplex.mp
# 存储每个公共图书馆位置的经度，纬度和街道交叉口名称。
class XPoint(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return "P(%g_%g)" % (self.x, self.y)

class NamedPoint(XPoint):
    def __init__(self, name, x, y):
        XPoint.__init__(self, x, y)
        self.name = name
    def __str__(self):
        return self.name


#使用geopy这个包
#geopy使python开发人员能够使用第三方地理编码程序和其他数据源轻松定位全球各地的地址、城市、国家和地标的坐标。

import geopy.distance
from geopy.distance import great_circle
def get_distance(p1, p2):
    return great_circle((p1.y, p1.x), (p2.y, p2.x)).miles


#从下面的url获取所需的图书馆信息
def build_libraries_from_url(url):
    import requests
    import json
    from six import iteritems

    r = requests.get(url)
    myjson = json.loads(r.text, parse_constant='utf-8')

    # find columns for name and location
    columns = myjson['meta']['view']['columns']
    name_col = -1
    location_col = -1
    for (i, col) in enumerate(columns):
        if col['name'].strip().lower() == 'name':
            name_col = i
        if col['name'].strip().lower() == 'location':
            location_col = i
    if (name_col == -1 or location_col == -1):
        raise RuntimeError("Could not find name and location columns in data. Maybe format of %s changed?" % url)

    # get library list
    data = myjson['data']

    libraries = []
    k = 1
    for location in data:
        uname = location[name_col]
        try:
            latitude = float(location[location_col][1])
            longitude = float(location[location_col][2])
        except TypeError:
            latitude = longitude = None
        try:
            name = str(uname)
        except:
            name = "???"
        name = "P_%s_%d" % (name, k)
        if latitude and longitude:
            cp = NamedPoint(name, longitude, latitude)
            libraries.append(cp)
            k += 1
    return libraries

libraries = build_libraries_from_url('https://data.cityofchicago.org/api/views/x8fc-8rcq/rows.json?accessType=DOWNLOAD')


print("There are %d public libraries in Chicago" % (len(libraries)))

#建5个咖啡店
nb_shops = 5
print("We would like to open %d coffee shops" % nb_shops)


#folium可以使用Python语言调用Leaflet的地图可视化能力
import folium
map_osm = folium.Map(location=[41.878, -87.629], zoom_start=11)
for library in libraries:
    lt = library.y
    lg = library.x
    folium.Marker([lt, lg]).add_to(map_osm)
map_osm



from docplex.mp.environment import Environment
env = Environment()
env.print_information()

from docplex.mp.model import Model
mdl = Model("coffee shops")




BIGNUM = 999999999

# Ensure unique points
libraries = set(libraries)
# For simplicity, let's consider that coffee shops candidate locations are the same as libraries locations.
# That is: any library location can also be selected as a coffee shop.
coffeeshop_locations = libraries

# Decision vars
# Binary vars indicating which coffee shop locations will be actually selected
#dict形式的var集合，  keys是咖啡店的位置，  name是...
coffeeshop_vars = mdl.binary_var_dict(coffeeshop_locations, name="is_coffeeshop")
#
# Binary vars representing the "assigned" libraries for each coffee shop
#matrix形式的var集合，    key1是咖啡店位置    key2是图书馆位置
link_vars = mdl.binary_var_matrix(coffeeshop_locations, libraries, "link")

#如果咖啡店的位置距离图书馆位置太远，就把它们之间的LINK  0-1 变量设置为0
for c_loc in coffeeshop_locations:
    for b in libraries:
        if get_distance(c_loc, b) >= BIGNUM:
            mdl.add_constraint(link_vars[c_loc, b] == 0, "ct_forbid_{0!s}_{1!s}".format(c_loc, b))

#如果咖啡店不在这个地方选址，那么跟它相关的所有link都变成0
#如果咖啡店在这个地方选址，那么跟它相关的所有link可能是1  也可能是0
mdl.add_constraints(link_vars[c_loc, b] <= coffeeshop_vars[c_loc]
                   for b in libraries
                   for c_loc in coffeeshop_locations)
mdl.print_information()


#对于每一个图书馆来说，它跟所有咖啡店的link加起来最多只能是1
#也就是一家图书馆只能link一家咖啡店，且必须link一家咖啡店
mdl.add_constraints(mdl.sum(link_vars[c_loc, b] for c_loc in coffeeshop_locations) == 1
                   for b in libraries)
mdl.print_information()


# Total nb of open coffee shops
#开的店的数目约束
mdl.add_constraint(mdl.sum(coffeeshop_vars[c_loc] for c_loc in coffeeshop_locations) == nb_shops)


# Print model information
mdl.print_information()




# Minimize total distance from points to hubs
#最小化所有图书馆到咖啡店的存在的link的距离
total_distance = mdl.sum(link_vars[c_loc, b] * get_distance(c_loc, b) for c_loc in coffeeshop_locations for b in libraries)
mdl.minimize(total_distance)



print("# coffee shops locations = %d" % len(coffeeshop_locations))
print("# coffee shops           = %d" % nb_shops)

assert mdl.solve(), "!!! Solve of the model fails"




total_distance = mdl.objective_value
open_coffeeshops = [c_loc for c_loc in coffeeshop_locations if coffeeshop_vars[c_loc].solution_value == 1]
not_coffeeshops = [c_loc for c_loc in coffeeshop_locations if c_loc not in open_coffeeshops]
edges = [(c_loc, b) for b in libraries for c_loc in coffeeshop_locations if int(link_vars[c_loc, b]) == 1]

print("Total distance = %g" % total_distance)
print("# coffee shops  = {0}".format(len(open_coffeeshops)))
for c in open_coffeeshops:
    print("new coffee shop: {0!s}".format(c))

import folium

map_osm = folium.Map(location=[41.878, -87.629], zoom_start=11)
for coffeeshop in open_coffeeshops:
    lt = coffeeshop.y
    lg = coffeeshop.x
    folium.Marker([lt, lg], icon=folium.Icon(color='red', icon='info-sign')).add_to(map_osm)

for b in libraries:
    if b not in open_coffeeshops:
        lt = b.y
        lg = b.x
        folium.Marker([lt, lg]).add_to(map_osm)

for (c, b) in edges:
    coordinates = [[c.y, c.x], [b.y, b.x]]
    map_osm.add_child(folium.PolyLine(coordinates, color='#FF0000', weight=5))

map_osm

