import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from lxml import html
from tqdm import tqdm
import time
import re
import time

# ------- Def Functions -------
def SpaceRemove(text):
    text = text.replace(" ", "")
    return text

def TextPlainer(text):
    text = re.sub("\n|\r|\t|\u3000", "", text)
    return text
    
def num_max_tab(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    elems = soup.select(".pages")
    return elems[0].text.split(" ")[2]

def get_address(address):
    plain_address = address[0].split("      ")
    address1 = SpaceRemove(plain_address[8])
    address2 = SpaceRemove(plain_address[12])
    return address1 + address2

def get_postal_code(address):
    plain_address = address[0].split("      ")
    postal_code = TextPlainer(plain_address[4])
    postal_code = SpaceRemove(postal_code)
    return postal_code

# ------- Input -------
os.chdir("保存先フォルダ")
output_path = "保存先フォルダ"

all_gotoeatshop_url = 'https://goto-eat.weare.osaka-info.jp/gotoeat/?search_element_0_0=2&search_element_0_1=3&search_element_0_2=4&search_element_0_3=5&search_element_0_4=6&search_element_0_5=7&search_element_0_6=8&search_element_0_7=9&search_element_0_8=10&search_element_0_9=11&search_element_0_cnt=10&search_element_1_0=12&search_element_1_1=13&search_element_1_2=14&search_element_1_3=15&search_element_1_4=16&search_element_1_5=17&search_element_1_6=18&search_element_1_7=19&search_element_1_8=20&search_element_1_9=21&search_element_1_10=22&search_element_1_11=23&search_element_1_12=24&search_element_1_13=25&search_element_1_14=26&search_element_1_15=27&search_element_1_cnt=17&s_keyword_3=&cf_specify_key_3_0=gotoeat_shop_address01&cf_specify_key_3_1=gotoeat_shop_address02&cf_specify_key_3_2=gotoeat_shop_address03&cf_specify_key_length_3=2&searchbutton=%E5%8A%A0%E7%9B%9F%E5%BA%97%E8%88%97%E3%82%92%E6%A4%9C%E7%B4%A2%E3%81%99%E3%82%8B&csp=search_add&feadvns_max_line_0=4&fe_form_no=0'
all_tab_urls = [] # タブのURL：（検索時に数百個のタブがあり、タブの中に数十個のお店がある）
num_max_tabs = int(num_max_tab(all_gotoeatshop_url))

print(f"検索結果のタブは全部で{num_max_tabs}個あります")
for i in range(num_max_tabs):
    url = f'https://goto-eat.weare.osaka-info.jp/gotoeat/page/{i+1}/?search_element_0_0=2&search_element_0_1=3&search_element_0_2=4&search_element_0_3=5&search_element_0_4=6&search_element_0_5=7&search_element_0_6=8&search_element_0_7=9&search_element_0_8=10&search_element_0_9=11&search_element_0_cnt=10&search_element_1_0=12&search_element_1_1=13&search_element_1_2=14&search_element_1_3=15&search_element_1_4=16&search_element_1_5=17&search_element_1_6=18&search_element_1_7=19&search_element_1_8=20&search_element_1_9=21&search_element_1_10=22&search_element_1_11=23&search_element_1_12=24&search_element_1_13=25&search_element_1_14=26&search_element_1_15=27&search_element_1_cnt=17&s_keyword_3&cf_specify_key_3_0=gotoeat_shop_address01&cf_specify_key_3_1=gotoeat_shop_address02&cf_specify_key_3_2=gotoeat_shop_address03&cf_specify_key_length_3=2&searchbutton=%E5%8A%A0%E7%9B%9F%E5%BA%97%E8%88%97%E3%82%92%E6%A4%9C%E7%B4%A2%E3%81%99%E3%82%8B&csp=search_add&feadvns_max_line_0=4&fe_form_no=0'
    all_tab_urls.append(url)


# ------- Process -------
# use val
shop_name_list =[]
address_list = []
postal_code_list = []
phone_num_list = []
open_time_list = []
close_day_list = []
error_list = []


for url in tqdm(all_tab_urls):
    try:
        # -------- Pre Process --------
        html = requests.get(url)
        soup = BeautifulSoup(html.content, "html.parser")
        r_names = soup.find_all('p', class_='name')
        for name in r_names:
            shop_name_list.append(name.text)
        address_complex = soup.find_all('td') # 
        step = 4 # ノイズ情報をスキップするための変数
        
        # tmp val
        tmp_address_list = [] # ノイズ情報の入ったな住所をストック
        split_address_list = [] # ノイズ情報を除去した住所をストック
        for a in address_complex:
            a = a.text
            tmp_address_list.append(a)
        for i in range(0, len(tmp_address_list), step):
            split_address_list.append(tmp_address_list[i: i+step])
            
        # -------- Main Process --------
        for address in split_address_list:
            plain_address = address[0].split("      ")
            postal_code = TextPlainer(plain_address[4])
            postal_code_list.append(get_postal_code(address))
            address_list.append(get_address(address))
            phone_num_list.append(address[1])
            open_time_list.append(address[2])
            close_day_list.append(TextPlainer(address[3]))
            
    except:
        error_list.append(url)
    time.sleep(1) # アクセスしすぎるとアクセス拒否を食らうので待機1秒
    

# ------- Output -------
df = pd.DataFrame({'name': shop_name_list,
                   "postal code": postal_code_list,
                   'address': address_list,
                   'phone' : phone_num_list,
                   'open time' : open_time_list,
                   'close day': close_day_list})

df.to_csv(os.path.join(output_path, 'Go2Eat_Osaka.csv'))
print(df)