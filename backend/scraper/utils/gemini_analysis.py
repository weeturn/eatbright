# -*- coding: utf-8 -*-
import csv
import google.generativeai as genai
import re
from .db_operations import insert_reviews, read_raw_reviews_from_db
from rapidfuzz import fuzz


GOOGLE_API_KEY = "AIzaSyCuVi-0-rH5uuoCE51OmPom_kjDDprOSFE"
MAX_TRIES = 3

def find_similar_dish(dish_name, known_dishes, threshold=75):
    for known_dish in known_dishes:
        if fuzz.ratio(dish_name, known_dish) > threshold:
            print(f'Ratio: {fuzz.ratio(dish_name, known_dish)}, 把{dish_name}換成{known_dish}')
            return known_dish
    return dish_name


def analyze_reviews_and_store_results(store_id):
    review_list = read_raw_reviews_from_db(store_id)
    print(f"共有{len(review_list)}筆資料")

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('models/gemini-1.0-pro-latest')

    result = []
    known_dishes = []  # 用來保存已經處理過的標準名稱 但只有看這次全部爬的有哪些 如果跟資料庫已經有的不同就GG
    batch_size = 10

    for i in range(0, len(review_list), batch_size):
        print(f'Batch {i//batch_size} / {(len(review_list) // batch_size)}')
        batch_reviews = review_list[i:i + batch_size]
        
        batch_result = []
        tries = 0

        while len(batch_result) < 5 and tries < MAX_TRIES:
            try:
                review_text = "\n".join([f"{idx + 1}. {item}" for idx, item in enumerate(batch_reviews)])
                response = model.generate_content(
                    f"幫我找出以下這幾段美食評論中分別提及哪些料理，並且根據評論中的描述給予料理(1,2,3)分的評分，分數越高代表越好吃，1分=難吃、2分=普通(有一些小缺點)、3分=好吃，一則評論可能有0到多個料理，幾乎都有1個以上，盡可能地將評論中的料理找出來，同一個料理可能出現在不同評論，都要寫出來。每個料理要提供\"名稱\"、\"描述\"(是根據評論中的哪些描述給分的)、\"分數\"，中間以**隔開，每個料理結束要換行，請嚴格遵守輸出格式，範例如下: [**美式漢堡**這間的美式漢堡味中規中矩，漢堡排不算香**2**\n**抹茶冰淇淋**從來沒吃過如此美味的佳餚**3**\n**炸雞**炸的又乾又硬**1**\n**地瓜球**地瓜球本身炸的很酥，但是涼掉了**2**]\n 以下是評論:\n{review_text}"
                )
                response_text = response.text
                
                # 使用正則表達式找到每個review的部分
                matches = re.findall(r'\*\*(.*?)\*\*(.*?)\*\*(\d+)\*\*', response_text)
                
                # 將結果轉換為需要的格式
                score_mapping = {
                '1': '1',  # 不變，保留原來的值
                '2': '3',  # 2 對應 3
                '3': '5'   # 3 對應 5
                }

                for match in matches:
                    # 提取原始數據
                    dish_name = find_similar_dish(match[0], known_dishes)
                    if dish_name not in known_dishes:
                        known_dishes.append(dish_name)
                    description = match[1].replace("描述: ", "")
                    score_str = match[2]
                    
                    # 轉換分數
                    if int(score_str) >= 1:  # 只保留分數大於等於 1 的項目
                        # 確保分數在映射中
                        mapped_score = score_mapping.get(score_str, score_str)
                        # 將結果加入 batch_result
                        batch_result.append([dish_name, description, mapped_score])
                
                if len(batch_result) < 5:
                    print("Batch result less than 5, retrying...")
                    tries += 1
                else:
                    break  # 結束 while 迴圈，繼續下一個 batch
            except:
                print("Gemini API error, retrying...")
                tries += 1

        print(batch_result)
        result.extend(batch_result)

    print(result)
    print(len(result))

    # 將結果寫入資料庫
    insert_reviews(store_id, result)








