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
6. rate_type: 价格类型，如nightly，表示价格是按每晚计算。
7. reiews_count: 这个房源共收到多少条评论。
8. star_rating: 这个房源的平均评分，分值从0~5。
9. created_time: 爬取该房源信息的时间。

### 2. 
