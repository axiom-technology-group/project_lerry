# Airbnb 成都房源相关信息说明

一共有X个csv,分别存储了Airbnb成都房源的基本信息、评价、地址、通过百度地图API返回的美食POI信息等等。

## 注意：
Airbnb在网页上使用的是高德地图，经纬度和百度地图使用的坐标系不同。在搜索时建议进行转换。
转换function(python)：https://www.jianshu.com/p/6e69737cffaa

## 文件说明：

### 1. chengdu_listing_complete.csv
房源基本信息。共计12,532条。
字段说明：
1. lisitng_id: 房源唯一编号，注意类型为string/object。如23616507。
2. latitude: 纬度，数值型。如30.67425。
3. longitude: 经度，数值型，如103.81968。
4. neigh: 搜索字段使用的query。主要成分为“中国四川省成都市”+“自定义字段”。
4. accomdates: 这个房源最多入住的人数。
5. price: 价格，单位为人民币元。
6. rate_type: 价格类型，如nightly，表示价格是按每晚计算。本数据中全部都是nightly.
7. reiews_count: 这个房源共收到多少条评论。
8. star_rating: 这个房源的平均评分，分值从0~5。
9. created_time: 爬取该房源信息的时间。

### 2. chengdu_listing_with_address.csv
房源基本信息+房源完整地址，12532条。
在chengdu_listing_complete.csv的基础上加入了：
1. result: 百度地图API搜索经纬度返回的完整结果，类型为string，需要使用函数转化为dictionary。
代码示例：
Python:


import ast


data['list'] = data['result'].apply(lambda x: ast.literal_eval(x[26:]))
2. address: 从result里面提取出来的完整地址，精确到门牌号。
3. zipcode：邮政编码
4. country：国家
5. province: 省份
6. city: 城市
7. district: 行政区
8. street: 街道名称
9. street_number: 门牌号
10. business：离该地址最近的三个POI点

### 3. chengdu_listing_price.csv
房源基本信息+结构化地址+聚类标签+每晚价格
在chengdu_listing_complete.csv的基础上加入了：
1. district: 通过百度地图API搜索经纬度，返回的完整地址中的【区域】部分，如温江区，金牛区。
2. add:  通过百度地图API搜索经纬度，返回的完整地址中的【区域】部分+【街道】部分，如温江区科林路西段。
3. person_price: price/accomdates. 价格/入住人数。表示XX元/人/晚。

### 4. chengdu_listing_cluster.csv
房源基本信息+ 百度地图API返回的美食POI信息+聚类结果
百度地图美食POI分类：http://lbsyun.baidu.com/index.php?title=lbscloud/poitags
以下对新增字段进行说明：
1. xiaochi_total: 百度地图API圆形区域搜索，半径为5KM，表示半径5KM圆形内小吃快餐店的数量。后续字段的搜索半径均为5KM。【中式餐饮】
2. zhongcanting_total: 中餐厅数量。【中式餐饮】
3. waiguocanting_total: 外国餐厅数量。【西式餐饮】
4. cake_total：蛋糕甜品店数量。【西式餐饮】
5. coffee_total: 咖啡厅数量。 【西式餐饮】
6. tea_total：茶座数量。【中式餐饮】
7. pub_total：酒吧数量。【西式餐饮】
8. subway_total: 地铁站数量。
9. chinese: 所有标记为【中式餐饮】的店铺数量加总。= xiaochi_total+zhoncanting_total+tea_total
10. western： 所有标记为【西式餐饮】的店铺数量加总。 =waiguocanting_total+cake_total+pub_total
11. label: 房源类别标签，有0， 1， 2， 3一共四类。

### 5. chengdu_reviews.csv
房源评论，有20万条，包含9000多个房源。
1. listing_id
2. comment_id：评价id，每个评价的独立编码。
3. rating: 评分。
4. comment: 评价正文。
5. create_at：评价发布时间

### 6. chengdu_listing_sentiment.csv
房源评论数据+情感分析结果+经纬度，按照每个房源求了各项均值。
1. rating：从评论里计算的出的平均评分。
2. sentiment_label: 评价情感倾向，取值为0~1，数字越大表示越积极。
3. positive_probs: 评价为积极的概率，取值为0~1.
4. negative_probs: 评价为消极的概率，取值为0~1.

5&6，经纬度。

### 7. lianjia_chengdu_address.csv
链家网上成都地区的写字楼信息
1. id：该条信息的id
2. name: 写字楼名称
3. areaDesc(m2): 面积区间，单位为平方米。
4. priceDesc(yuan/m2)：价格区间，单位为元/平方米。
5. roomCount：房间套数。

6&7: 通过百度地图API返回的经纬度信息。


