
楽天APIで商品情報を取得する
===
楽天が提供しているAPIはDevelopersで取得する。専用ページで取得したAPIのテストをすることができる。
なお、APIを利用するには予めログインからアプリIDを発行する必要がある。
## API？
APIとは何か、という問いですがAPIは他のWEBサービスから自分の作ったWEBサービスに欲しい情報をかりてくることができる機能です。
WEB上でHTTPリクエストをなげHTTPレスポンスを受け取ることで自分が一から開発する手間をなくせます。
### パラメーター？
パラメーターとはデータをWEBサービスに送信する際、HTTPリクエストして結果を反映するものです。このパラメーターに楽天API登録時に割り当てられたアフィリエイトID、アプリケーションIDを設定します。
楽天APIの詳細については[楽天Developers](https://webservice.rakuten.co.jp/documentation/ichiba-product-search)から確認できます。

### APIを楽天DevelopersでIDを発行
まず楽天APIを取得します。[楽天Developers](https://webservice.rakuten.co.jp/)にアクセスしサインインし、アプリを作成を選択します。初めてアクセスする方はNew AppからアプリIDを取得します。
[画像]
アプリIDを作成したらこのIDをパラメーターに記述するのでプログラム作成時に利用します。


## APIでデータを取得し、Excelに転記する全体像

仕様としては、APIからデータを引っ張ってきてそこからデータの精査、そして取得データを保存というイメージです。なのでいくつかクラスを作って抽象化を行ってみました。今回作成したクラスは3つAPIクラス、Rakutenクラス、RakutenAnalysisクラスです。

今回Excelを使うので`openpyxl`をインストールして利用します。
この記事では全てのコードは貼り付けませんが記事の最後にGithubのURLを貼り付けておくので確認したい方はそこからコードを見てください。
[iframe]
### APIクラスの概要
[概要]
楽天APIはAPIドメインのURLにクエリ文字列を入れることでリクエストを取得することができます。楽天のテストAPIを見ると、パラメーターとしてkeywordとアプリID、アフィリエイトIDを持たせているのでこちらも同様の形でパラメーターを設定します。そのためAPIクラスにはコンストラクタにurlとparametersを持たせています。
[メソッドの表]


### Rakutenクラスの概要
[概要]
RakutenのクラスはAPI()から情報を取得し取得したい商品情報を渡します。この時、渡す値はパラメーターで設定しているjson形式で商品情報を持っています。
リクエストの取得、ヘッダー情報の確認をここで行います。
[メソッドの表]

### Analysisクラスの概要
[概要]
Rakutenクラスからヘッダー情報を受け取った商品情報をAnalysisクラスで結果からデータを抽出します。抽出したデータはpandasを使用してDataFrameを作成した後、Excel形式で商品情報を出力します。必要はありませんでしたが、CSVファイルでのデータもよく利用するのでCSV出力も作成します。

## APIから情報をリクエスト
main()関数を作成しそこからプログラムを開始します。まずキーワードを入力し、その値はパラメーターに入ります。APIをリクエストするためにインスタンスを作成、これらをRakutenクラスにapiインスタンスとパラメーターに入れリクエストを取得します。
```
class API:
    def __init__(self,url:str):
        self.url = url
        self.parameters = {}
    
    def get_parameters(self,parameters):
        self.parameters = parameters
        return self.parameters

    def get_url(self):
        return self.url

class Rakuten:
    def __init__(self,api,params):
        self.api = api
        self.params = params

    
    def get_requests(self,url,parameters):
        self.req = requests.get(url,params=parameters)
        return self.req

def main(keyword:str):
    # パラメータセット
    parameters = {
                'applicationId': '1090101428128448381', #アプリID
                'affiliateId' : '24e554d6.nc5b4d4a8.24e554d7.493927e4', #アフィリエイトID
                'keyword' : 'keyword', # キーワードの入力
                'format' : 'json'
    }
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
    # 検索するキーワード取得

    if 'keyword' in parameters:
        parameters['keyword'] = keyword

    api = API(url)
    rakuten = Rakuten(api,parameters)
    # APIのリクエストを取得
    req = rakuten.get_requests(api.get_url(),parameters)
```
APIから受け取ったデータを確認するとデータはJSON形式で返事が返ってきています。
どのようなやり方で使用するのがわからなかったので調べてみたところ、`requests.get(url).json()`に含まれる.json()の部分でJSON形式から辞書型に変換した上で使用するのが一般的なようです。それに倣ってプログラムを組んでいきます。
取得したリクエストを変数reqに持たせます。このreq変数をヘッダー情報を確認。こちらはJSON形式のレスポンスが欲しいので、Content-Typeを明示し、データが正しく返されれば、レスポンスをデコードします。
そうでない場合は、リクエストをテキスト形式で取得し返すます。
```

def check_header(self,req):
        if "json" in req.headers.get("Content-type"):
            result = req.json()

            return result
        else:
            result = req.text
            return True

# ヘッダー情報を確認する
result = rakuten.check_header(req)

```
requestsのオブジェクトはPythonのdictに変換され、データの取り扱いを簡単にすることができます。


## 取得する商品情報を抽出
今回楽天APIから取得した商品データから抽出したい商品項目をforループで回して取得します。
```
# 結果からデータを抽出
rakuten_analysis = RakutenAnalysis()
rakuten_analysis.sampling(result,keyword)
```
このsamplingメソッドは対象のデータから任意の商品情報を抽出し、出力する商品情報を返すのが目的です。

上述した通り、取得した辞書型オブジェクトを操作して辞書の値を取得、追加、変更していきます。

リクエストした中の辞書を見てみます。Itemsの中に一度のリクエストで取れる商品が入っています。この入っているItemsの次の中を見るとリストでそれぞれの商品は群として入っています。
ここまでで**一つの商品情報**を参照することが出来ました。ここからは取得したい情報を個別に指定していきます。
例えば商品番号なら以下の通りになります。
`item_code = q["Items"][0]["Item"]["itemCode"]# [全ての商品][リスト内の商品][商品情報]`
今回は商品番号、商品名、商品金額、商品URL、商品画像URLを取得したいと思います。一度確認の為に取得したい値を取得してみます。

```
item_code = q["Items"][0]["Item"]["itemCode"]# [全ての商品][リスト内の商品][商品情報]
item_name = q["Items"][0]["Item"]["itemName"]# [全ての商品][リスト内の商品][商品情報]
item_price = q["Items"][0]["Item"]["itemPrice"]# [全ての商品][リスト内の商品][商品情報]
item_url = q["Items"][0]["Item"]["itemUrl"]# [全ての商品][リスト内の商品][商品情報]
image_url = q["Items"][0]["Item"]["mediumImageUrls"]# [全ての商品][リスト内の商品][商品情報]
```
### forで全ての商品情報を取得
先ほど取得したい商品情報を指定して作成しました。ですが、これでは一つの商品情報のみになってしまいます。ここからforループを追加で記述して全ての商品を取得していきます。
[一個ずつ]
まず、いくつのデータが一度のリクエストで取得出来ているのでしょうか。楽天のAPIでは一度で30件が取得できるようですので、`len()`を使用して確認します。
```

print("取得件数: len",len(q["Items"]))
>> 取得件数: len 30
```
これで30件の取得をしていることが確認できました。
forループで繰り返して確認した商品をすべて取得してみます。
```
for item in items:
    items = item["Item"]
    print(items)
```
これで全ての商品情報を取得することができます。ですがこのままではリストを追加して取得したデータを格納するのにまた記述が増えてしまいます。それに分かりにくくなります。ですので一度別のやり方を見てみます。
forでループさせ、取得したデータはリストに格納する、それなら内包表記でも済みそうです。では内包表記で書き直してみます。
```
items = [item["Item"] for item in items]
```
これで結果は同じでなおかつ一行で済みました。

### データフレームに逐次追加し必要な形に整形する
ここで取得したいデータを抽出していきます。今回はpandasのDataFrameを使用して欲しいデータを抽出します。
`pd.DataFrame(items)`で全ての商品情報をDataFrameに入れることができます。
ここでDataFrameにcolumnsを設定を行いデータを整形します。上がitemsリストのみの設定、下がcolumnsで設定したものです。
取得したデータのキーを確認しながら取得したデータを抽出するで
```

df = pd.DataFrame(items)

# これでカラムで取得したいデータを抽出
df = pd.DataFrame(items,columns=[
    'asurakuArea', 'asurakuClosingTime','availability',
    'catchcopy','genreId','itemCode',
    'itemName', 'itemPrice', 'itemUrl',
    'mediumImageUrls','reviewAverage', 'reviewCount',
'shopCode', 'shopName','shopUrl'
])
```
取得結果は以下になります。
```
  asurakuArea asurakuClosingTime  availability           catchcopy genreId  ... reviewAverage reviewCount  shopCode shopName                                            shopUrl
0                                            1  【楽天ブックスならいつでも送料無料】  101937  ...           5.0           1      book   楽天ブックス  https://hb.afl.rakuten.co.jp/hgc/24e554d6.nc5b...
1                                            1  【楽天ブックスならいつでも送料無料】  101937  ...           0.0           0      book   楽天ブックス  https://hb.afl.rakuten.co.jp/hgc/24e554d6.nc5b...
2                                            1  【楽天ブックスならいつでも送料無料】  209118  ...           0.0           0      book   楽天ブックス  https://hb.afl.rakuten.co.jp/hgc/24e554d6.nc5b...
```
きれいに整形できています。ですがcolumnsの商品情報が英語で読みにくいです。なので、新しくcolumnsを設定して上書きしていきます。
`df.columns = new_columns`とすることで先ほど設定してcolumnsをnew_columnsで上書きすることができます。
```
new_columns = ['商品番号','商品名','商品金額','商品URL','商品画像URL','ジャンルID','あす楽エリア','販売可能','キャッチコピー','レビュー平均点','レビュー数','ショップ番号','ショップ名','ショップURL']
df.columns = new_columns
```
columnsを新しくするのと、順番を並び替えてみました。これで抽出は完了です。
### 取得データをソート
データを取得し、欲しいデータを抽出。これで商品情報は確認することができました。ですが、このアプリの作成する目的としてはやはり取得した情報を元に何らかのアクションを促したい目的があって作成するということになったはずです。
つまり何が言いたいのかというと、商品情報を取得して確認する理由は、その日の購入を目的としているはずなのです。このままではどの商品が安いのか高いのか確認しずらいです。
ということで、**ソートして最低金額の商品情報がデータの上**に来るようにします。

```
df_s = df.sort_values('商品金額',ascending=False)#昇順ではない設定
```
`pandas.sort_values()`メソッドは指定した引数を昇順、降順してくれるメソッドです。標準は昇順らしいので今回は降順で設定してみます。
また**一度変数に渡してあげないと上書きされないので注意**です。

## CSVファイルを作成
`pandasにpandas.DataFrame()`をexcelファイルとして書き出すには`to_excel()`メソッドを使う。
openpyxlとxlwtをインストールします。
```
pip install openpyxl
pip install xlwt
```
to_excel()は内部でopenpyxl,xlwtというライブラリを使用している。なので、to_excel()メソッドを使うためにこれらのライブラリをインストールします。
以上の内容を以下のコードに表示します。

```
class RakutenAnalysis:
    def sampling(self,q:dict,keyword:str):
        """
        取得したAPI情報から
        インスタンス化する商品情報を選定

        Args:
            q (str): キーワード
        return:
            items(dict): 出力する商品情報
        """
        
        # 取得する商品情報を抽出
        items = q["Items"]
        items = [item["Item"] for item in items]
            # データを逐次追加する
        df = pd.DataFrame(items,columns=[
            'itemCode','itemName','itemPrice',
            'itemUrl','mediumImageUrls',
            'genreId','asurakuArea','availability',
            'catchcopy','reviewAverage', 'reviewCount',
            'shopCode', 'shopName','shopUrl'
        ])
        new_columns = ['商品番号','商品名','商品金額','商品URL','商品画像URL','ジャンルID','あす楽エリア','販売可能','キャッチコピー','レビュー平均点','レビュー数','ショップ番号','ショップ名','ショップURL']
        df.columns = new_columns
        df_s = df.sort_values('商品金額',ascending=False)#昇順ではない設定

        # pandasでexcelファイルを作成
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        df_s.to_excel(f"export_{keyword}_{now}.xlsx",sheet_name="商品情報")
        # CSVファイルを作成
        df_s.to_csv(f"export_{keyword}_{now}.csv",mode='w',encoding='utf-8 sig')
        wb = px.load_workbook(f"export_{keyword}_{now}.xlsx")
        sheet = wb["商品情報"]
        max = sheet.max_row
        min = sheet.min_row
        max = sheet.cell(row=max,column=4).value# 最終行
        min = sheet.cell(row=min+1,column=4).value#先頭行+1
        print('最終行の商品金額',max)
        print('先頭行の商品金額',min)

```
ソートもしたので最終行と先頭行の値を取得して最安地と最高値を確認してみました。
## pytestでテスト
Pythonに単体テストをする機能があるテストをするためのフレームワークだそうです。便利そうなのでテストの書き方と、機能について整理してみます。
テストの準備をします。必要になるのはテストをするための対象のファイル（テストコードですね）を配置。そしてテスト用のコードを配置しそれぞれ対象のフォルダの中に用意します。
基本の約束としてテストするファイル名は、test_*.py(*ここにファイル名が入ります)とする必要があります。
```
pip install pytest
```
**基本的なやり方:**
基本的なやり方をまとめると次のような手順になります。そして、assertで期待できる結果を書いていきます。

1. テストするコードのファイルにtest_*.pyと命名する
2. test_で始まる関数がテスト対象となるので関数にtest_*()と命名(テストする関数名と同じにしておくのが無難)とする
3. 確認したい処理にassertと記述し、期待する値か設定する
4. `pytest test_ファイル名.py`とコマンドで実行することでpytestを行う

`def test_関数名`とするとpytestが勝手にテストする関数と認識してくれます。無難にtest_テスト関数名としてテスト実行するのがわかりやすいです。
実行してみるとターミナル中に結果が返ってきます。pytest用に一度サンプル関数を作成してテストしたプログラムが以下になります。

assertとは何か。[what][what's better usually]調べてみると、基本的な使い方は条件をテストするためのデバックツールとして使われています。
assertが真の評価を得られた場合何も起きずプログラムは実行し続けます。ですが条件が偽の評価の場合はAssertionError例外が送出されます。

```
def func(x):
  return x+1


def test_answer():
  assert func(3) == 5

=================================================================================== FAILURES ==================================================================================== 
__________________________________________________________________________________ test_answer __________________________________________________________________________________ 

    def test_answer():
>     assert func(3) == 5
E     assert 4 == 5
E      +  where 4 = func(3)

test_sample.py:6: AssertionError
============================================================================ short test summary info ============================================================================ 
FAILED test_sample.py::test_answer - assert 4 == 5
```

failedと返ってきています。またpytestを実行するとテストしたフォルダ内にpytest_cacheが作成されます。では4と設定してもう一度実行してみます。
```
============================================================================== test session starts ==============================================================================
platform win32 -- Python 3.10.2, pytest-7.0.1, pluggy-1.0.0
rootdir: C:\Users\ahoo\Documents\python\rakuten-api
collected 1 item

test_sample.py .                                                                                                                                                           [100%] 

=============================================================================== 1 passed in 0.02s =============================================================================== 

```
何もエラーが返ってきていません。何事もなくプログラムは実行され終了したようです。。ではこのpytestを使用して作成したプログラムrakuten.pyをテストしてみようと思います。


## まとめ
関数だけで作ったプログラムがすごく分かりにくかったのでクラスに直してみましたがやはり抽象化するのはわたしにはまだまだ難しいという結論が出ました。まだまだクラスの抽象化にやり方があるでしょうが私にはこれ以上は考えつかなかったです。
もう少しわかりやすいクラスの設計があるはずなのでこれからも試行錯誤してプログラムを作っていくのが大切。
`https://github.com/youcan210?tab=repositories`

