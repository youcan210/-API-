from rakuten import *
import urllib.parse

def test_api():
    """APIテスト対象
      レスポンス結果と期待値の比較
      クエリパラメータに指定した値が設定されているか確認
      
    """
    # パラメータセット
    parameters = {
                'applicationId': '1090101428128448381', #アプリID
                'affiliateId' : '24e554d6.nc5b4d4a8.24e554d7.493927e4', #アフィリエイトID
                'keyword' : 'keyword', # キーワードの入力
                'format' : 'json'
    }
    # クエリ文字列を（パラメーター）作成
    d_qs = urllib.parse.urlencode(parameters)

    d_url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706" + '?' + d_qs
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
    
    print("url: ",url)
    # 検索するキーワード取得


    if 'keyword' in parameters:
        parameters['keyword'] = "python"
    # テスト対象API呼び出しクライアント生成
    api = API(url)
    rakuten = Rakuten(api,parameters)
    
    # APIのリクエストを実行
    req = rakuten.get_requests(api.get_url(),parameters)
    req = req.json()
    # レスポンス結果比較
    assert parameters['keyword'] == req['Items']

if __name__ == "__main__":
  test_api()