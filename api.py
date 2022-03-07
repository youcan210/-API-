"""
取得商品名と価格の一覧を取得

"""
from operator import itemgetter
import requests
import json
from pandas import json_normalize
# *todo コンテンツの取得
# *todo コンテンツから色々な商品情報を取得表示

# コマンド引数から入力した商品名から（楽天内の）最安値と最高値を表示する

# requests
# リクエストURL
url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
# パラメータセット
parameters = {
            'applicationId': '1090101428128448381', #アプリID
            'affiliateId' : '24e554d6.c5b4d4a8.24e554d7.493927e4', #アフィリエイトID
            'genreId' : '100316', #ジャンルID(例えばドリンク・酒であれば100316)
            'period' : 'realtime' #ランキング集計期間
}

item_info = {
    "商品コード":"Item.itemCode",
    "商品名":"Item.itemName",
    "商品金額":"Item.itemPrice",
    "商品URL":"Item.itemUrl",
    "商品画像URL":"Item.mediumImageUrls",
    "ポイントレート":"Item.pointRate"
    }

def create_csv():
    df = trans_dataframe()
    # 商品ID,商品名,金額
    item = df[["Item.itemCode","Item.itemName","Item.itemPrice","Item.itemUrl","Item.mediumImageUrls","Item.pointRate"]]
    item.to_csv("item.csv",encoding="utf_8_sig")
    return item

def check_header(req):
    if "json" in req.headers.get("Content-Type"):
        result = req.json()
        return result
    else:
        result = req.text
        print(result)

def get_ranking(rakuten=url):
    #jsonデータの取得
    req = requests.get(url, params = parameters)
    result = check_header(req)
    json.dumps(result, indent=2,ensure_ascii=False)
    return result

# 取得したjson形式データをdataframeに変換
def trans_dataframe():
    jsondata = get_ranking()
    df = json_normalize(jsondata["Items"])
    return df


def view_record(item):
    print("取得件数: ",str(len(item)),"件")

def append_dict(item_info):
    items = item.append(item_info,ignore_index=True,sort=False)
    print(items)



item = create_csv()
# rakuten = Rakuten(item)
# print(rakuten.item)

view_record(item)
append_dict(item_info)