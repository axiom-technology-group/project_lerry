#!/usr/bin/env python
# coding: utf-8

# ## Airbnb Chengdu Listings Crawler

# ## 如何通过搜索获取房屋详情，返回JSON格式
# 
# 1. 使用chrome浏览器打开网址 https://www.airbnb.cn/
# 
# 2. 随便搜索一个地方，必须是“国家”+“省”+“城市”+“具体地名”（可选），以免搜索到别的城市。如中国四川省成都市太古里，如果直接搜索“太古里”可能会搜到北京的太古里哦。
# 
# 3. 使用FN+F12打开开发者界面→network→explore_tabs，获取url. 稍后会解释重点参数。
# url示例：
# 
# https://www.airbnb.cn/api/v2/explore_tabs?_format=for_explore_search_web&_intents=p1&auto_ib=false&client_session_id=b268a305-5b97-492c-bc45-58e5fb8edf16&currency=CNY&experiences_per_grid=20&federated_search_session_id=9b7a4306-1e1f-49b4-8893-40c463d62b3f&fetch_filters=true&from_prefetch=true&guidebooks_per_grid=20&has_zero_guest_treatment=true&is_guided_search=true&is_new_cards_experiment=true&is_standard_search=true&items_offset=18&items_per_grid=18&key=d306zoyjsyarp7ifhu67rjxn52tv0t20&last_search_session_id=de45c194-4834-47af-81c9-26290b98aad2&locale=zh&luxury_pre_launch=false&map_toggle=false&metadata_only=false&place_id=ChIJIXdEACPF7zYRAg4kLs5Shrk&query=%E4%B8%AD%E5%9B%BD%E5%9B%9B%E5%B7%9D%E7%9C%81%E6%88%90%E9%83%BD%E5%B8%82&query_understanding_enabled=true&refinement_paths%5B%5D=%2Fhomes&satori_version=1.1.13&screen_height=616&screen_size=small&screen_width=451&section_offset=7&selected_tab_id=home_tab&show_groupings=true&supports_for_you_v3=true&timezone_offset=480&version=1.5.8
# 

# ## 思路：
# 
# ### 构造搜索字段→requests获取网页→存储在List中→list变成dataframe→dataframe导出csv

# In[ ]:


# packages
import requests
import pandas as pd
import json
import time
import urllib
import random
import numpy as np


# In[ ]:


# 结果储存器，类型为List，实际房源信息不止这些
listing_id = [] #id, unique id for each listing, 存储id
latitude = [] #latitude， 存储房屋纬度
longitude = [] #longitude，存储房屋经度
accomdates = [] #person_capacity per listing，存储每个房源最多居住几人
price = [] #in RMB，存储价格
rate_type = [] #nightly, weekly, etc，存储价格单位，一般为每晚
reviews_count = [] #how many reviews for each listing_id，存储该房源的评价数量
rating = [] #average rating of each listing (range 0 to 5), 存储该房源的平均评分，范围为0~5
neigh = [] #search query，存储当前的搜索字段


# ## 网页参数，关注items_offset, query

# 1.  items_offset: 每页展示多少个房源信息，一般为18或18的倍数，输入类型为数字。当爬取到query的尾页时，数字可能不是18的倍数。只要此参数为18的倍数，就可以实现翻页的功能。如，item_offset=0， 返回搜索字段结果的第一页。item_offset=18，返回搜索字段结果的第2页。最多返回17页。
# 
# 
# 
# 2. query：搜索字段，输入类型为文本(String)。
# 
# 对于网页参数的更多解释，请见https://www.jianshu.com/p/75edd92eec1a

# In[ ]:


data = {'_format': 'for_explore_search_web',
    '_intents': 'p1',
    'auto_ib': 'false',
    #'client_session_id': 'd0f6aaf7-b8a8-4577-b113-8774c4af417c',
    'experiences_per_grid': '20',
    #'federated_search_session_id': 'dd193745-33b2-4ef8-849c-1506e5034762',
    'fetch_filters': 'true',
    'from_prefetch': 'true',
    'guidebooks_per_grid': 20,
    'has_zero_guest_treatment': 'true',
    'is_guided_search': 'true',
    'is_new_cards_experiment': 'true',
    'is_standard_search': 'true',
    'items_offset': {},  #关键参数，解释见上
    'items_per_grid': 18,
    'key': 'd306zoyjsyarp7ifhu67rjxn52tv0t20',
    'locale': 'zh',
    'luxury_pre_launch': 'true',
    'map_toggle': 'false',
    'metadata_only': 'false',
    #'place_id': 'ChIJIXdEACPF7zYRAg4kLs5Shrk',  #千万别输入Place_id，否则再怎么改动query，结果都是一样的
    'query': {}, #关键参数，解释见上
    'query_understanding_enabled': 'true',
    'refinement_paths[]': '/homes',
    's_tag': 'LBV99TKT',
    'satori_version': '1.1.13',
    'screen_height': 616,
    'screen_size': 'small',
    'screen_width': 575,
    'section_offset': 7,
    'selected_tab_id': 'home_tab',
    'show_groupings': 'true',
    'supports_for_you_v3': 'true',
    'timezone_offset': 480,
    'version': '1.5.8'}


# ## 搜索字段
# 
# 因为AIRBNB上的房源展示有数量限制，搜索字段越详细越好，使用的是AIRBNB成都的filter。
# 
# 下方是AIRBNB成都所有point of interest的清单(list)，一共156个。房源可能会重复。可以根据需求更换。

# In[45]:


chengdu_poi = ['锦江区', '青羊区', '金牛区', '双流区', '龙泉驿区', '新都区',
 '崇州市', '邛崃市', '武侯区', '成华区', '都江堰市', '郫都区',
 '温江区', '大邑县', '金堂县', '蒲江县',
 '一品天下', '万年场','万盛', '三圣乡', '三瓦窑', '世纪城', '世纪城新会展', 
 '东坡路', '东大路', '东门大桥', '中医大省医院', '中坝', '九眼桥', '九里堤',
 '书房', '二仙桥', '五根松', '人民公园', '倪家桥', '光华公园', '八里庄',
 '凤凰大街', '凤溪河', '前锋路', '动物园', '北站西二路', '华兴街', '华府大道',
 '华西坝', '华阳', '南熏大道', '双店路', '双桥路', '双流国际机场', '双流机场1航站楼',
 '双流机场2航站楼', '四川博物馆', '四川师大', '四川电视塔', '塔子山公园', '大慈寺', '大观',
 '天府三街', '天府广场', '天河路', '太升南路', '太升路', '太古里', '太平园', '奎星楼街', 
 '孵化园', '安仁博物馆小镇', '宽窄巷子', '崔家店', '市二医院', '广福', '广都', '府青路',
 '建设巷', '惠王陵', '成渝立交', '成都东客站', '成都东站', '成都南站', '成都大熊猫繁育研究基地', 
 '成都站', '成都行政学院', '成都西站', '文化宫', '文殊院', '新南门', '春熙路', '昭觉寺南路',
 '李家沱', '杜甫草堂', '来龙', '杨柳河', '槐树店', '武侯大道', '武侯祠', '洪河', '海昌路',               
 '涌泉', '清江西路', '火车北站', '火车南站', '熊猫大道', '牛市口', '牛王庙', '犀浦',
 '狮子山', '玉双路', '玉林路', '环球中心', '理工大学', '琉璃场', '白果林', '百草路',
 '盐市口', '省体育馆', '磨子桥', '神仙树', '红星桥', '红牌楼', '羊犀立交', '耍都',
 '花照壁', '茶店子', '茶店子客运站', '草堂北路', '蜀汉路东', '街子古镇', '衣冠庙', 
 '西南交大', '西南财大', '西岭雪山', '迎宾大道', '迎晖路', '连山坡', '都江堰', 
 '金周路', '金沙博物馆', '金沙遗址博物馆', '金科北路', '金花', '金融城', '锦城广场',
 '锦江宾馆', '锦里', '青城山', '青羊宫', '香香巷', '驷马桥', '骡马市', '高升桥',
 '高新', '黄龙溪古镇', '龙平路', '龙泉驿', '龙爪堰']


# ## 爬虫

# 分为四部分：
# 
# 1. 构造搜索字段和结果的第一页Url。原因是第一页的返回结果和其他页面的有所不同。listing总数为18个，但是藏在返回结果的不同部分，分别存储在first_buffer（存储12个）和hidden_buffer中（存储6个或更少）。
# 
# 
# 2. 存储第一页的结果至对应的List中。
# 
# 
# 3. 构造剩余页面的url，获取repsonse，存储结果到buffer中，并判断是否有下一页，对应返回结果的['has_next_page']。
# 
# 
# 4. 每爬完一个字段的结果，输出一次csv。
# 
# 
# 5. 全部爬完后，通过pandas去除重复的数据，依据是Listing_id。
# 
# **如果遇到报错：index out of range，意思是该页面没有18个结果，程序会终止，但是结果已经存储在list中了，只需要删掉已经搜索过的搜索字段然后重新启动。**
# 
# 
# **解决方案：可以尝试建立正则表达式来确定某一页返回的结果到底有几个，建议的搜索字段为'bathroom_label'，它的个数即为该页面的结果数量。**

# In[ ]:


sample_list = [] #chengdu_poi清单的一部分
for num, poi in enumerate(sample_list):
    start = time.time() 
    query = '中国四川省成都市'+ sample_list[num]  #构建搜索字段
    first_url = 'https://www.airbnb.cn/api/v2/explore_tabs?_format=for_explore_search_web&_intents=p1&auto_ib=false&experiences_per_grid=20&fetch_filters=true&from_prefetch=true&guidebooks_per_grid=20&has_zero_guest_treatment=true&is_guided_search=true&is_new_cards_experiment=true&is_standard_search=true&items_offset=0&items_per_grid=18&key=d306zoyjsyarp7ifhu67rjxn52tv0t20&locale=zh&luxury_pre_launch=true&map_toggle=false&metadata_only=false&query={}&query_understanding_enabled=true&refinement_paths%5B%5D=%2Fhomes&s_tag=LBV99TKT&satori_version=1.1.13&screen_height=616&screen_size=small&screen_width=575&section_offset=7&selected_tab_id=home_tab&show_groupings=true&supports_for_you_v3=true&timezone_offset=480&version=1.5.8'.format(query)
    first_response = requests.get(first_url)  #获取搜索结果的第一页
    if first_response.status_code == 200:   #如果状态正常
        print('get first response', query)
        first_answer = first_response.json()  #获取Json数据
        first_buffer = first_answer['explore_tabs'][0]['sections'][0]['listings']  #通过dictionary获取房源信息
        for i in range(0, 12):  #保存第一页前12条结果
            listing_id.append(first_buffer[i]['listing']['id'])
            latitude.append(first_buffer[i]['listing']['lat'])
            longitude.append(first_buffer[i]['listing']['lng'])
            accomdates.append(first_buffer[i]['listing']['person_capacity'])
            price.append(first_buffer[i]['pricing_quote']['rate']['amount'])
            rate_type.append(first_buffer[i]['pricing_quote']['rate_type'])
            reviews_count.append(first_buffer[i]['listing']['reviews_count'])
            rating.append(first_buffer[i]['listing']['avg_rating'])
            neigh.append(query)
        hidden_buffer = first_answer['explore_tabs'][0]['sections'][2]['listings'] #获取第一页结果的后6条
        for k in range(0, 6):  #保存第一页的后6条结果
            listing_id.append(hidden_buffer[k]['listing']['id'])
            latitude.append(hidden_buffer[k]['listing']['lat'])
            longitude.append(hidden_buffer[k]['listing']['lng'])
            accomdates.append(hidden_buffer[k]['listing']['person_capacity'])
            price.append(hidden_buffer[k]['pricing_quote']['rate']['amount'])
            rate_type.append(hidden_buffer[k]['pricing_quote']['rate_type'])
            reviews_count.append(hidden_buffer[k]['listing']['reviews_count'])
            rating.append(hidden_buffer[k]['listing']['avg_rating'])
            neigh.append(query)
        print(query, 'the first page is OK')
        if first_answer['explore_tabs'][0]['pagination_metadata']['has_next_page'] == True: #判断是否有第二页
            for page_num in range(1, 18):
                item_offset = page_num*18  #构造item_offset的参数，为18的倍数，第一页为0，第二页开始为18的正整数倍，最多为17页
                URL = 'https://www.airbnb.cn/api/v2/explore_tabs?_format=for_explore_search_web&_intents=p1&auto_ib=false&experiences_per_grid=20&fetch_filters=true&from_prefetch=true&guidebooks_per_grid=20&has_zero_guest_treatment=true&is_guided_search=true&is_new_cards_experiment=true&is_standard_search=true&items_offset={}&items_per_grid=18&key=d306zoyjsyarp7ifhu67rjxn52tv0t20&locale=zh&luxury_pre_launch=true&map_toggle=false&metadata_only=false&query={}&query_understanding_enabled=true&refinement_paths%5B%5D=%2Fhomes&s_tag=LBV99TKT&satori_version=1.1.13&screen_height=616&screen_size=small&screen_width=575&section_offset=7&selected_tab_id=home_tab&show_groupings=true&supports_for_you_v3=true&timezone_offset=480&version=1.5.8'.format(item_offset, query)
                response = requests.get(URL)
                if response.status_code == 200:
                    answer = response.json()
                    buffer = answer['explore_tabs'][0]['sections'][0]['listings'] #获取房源数据
                    if len(buffer) > 0: 
                        for m in range (0, 18):  #存储数据
                            listing_id.append(buffer[m]['listing']['id'])
                            latitude.append(buffer[m]['listing']['lat'])
                            longitude.append(buffer[m]['listing']['lng'])
                            accomdates.append(buffer[m]['listing']['person_capacity'])
                            price.append(buffer[m]['pricing_quote']['rate']['amount'])
                            rate_type.append(buffer[m]['pricing_quote']['rate_type'])
                            reviews_count.append(buffer[m]['listing']['reviews_count'])
                            rating.append(buffer[m]['listing']['avg_rating'])
                            neigh.append(query)
                            time.sleep(random.randint(0,3))
                    print('the {} page of {} is OK!'.format(page_num, query)) #打印爬取进度
                    end = time.time()
                    print (end-start)
        chengdu_listing = pd.DataFrame({'listing_id': listing_id, 'latitude': latitude,
                                'longitude': longitude, 'neigh': neigh,'accomdates': accomdates,
                                'price': price,'rate_type':rate_type, 'reviews_count': reviews_count,
                                'star_rating': rating, 'create_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        print(len(listing_id),chengdu_listing.shape, query)  #dataframe现在的维度
        chengdu_listing.to_csv('chengdu_listing.csv', index = False, encoding = 'utf-8-sig')  #导出csv
        print('export to csv finished')
    else: break 


# ## 去除重复的结果并保存

# In[ ]:


# Remove duplicated listing_id
print(len(np.unique(chengdu_listing['listing_id']))) #how many unique listings in the chengdu_listing dataframe
df_new = chengdu_listing.drop_duplicates(subset='listing_id')
print(len(df['listing_id'])) #should be equal to len(np.unique(chengdu_listing['listing_id']))
print(df.shape[0]) #should be equal to len(np.unique(chengdu_listing['listing_id']))


# In[ ]:


df.to_csv('chengdu_listing_complete.csv', index = False, encoding = 'utf-8-sig')

