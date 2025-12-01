
import csv
import re

raw_text = """
# 1: 環境構築
## 概要
* メンバー内の誰かの個人のリポジトリにプロジェクトを作成する（private）
* メンバー全員、担当メンターを招待する
* それぞれ環境構築を実施する
* ローカルでRailsの画面が表示されたらOK

## 完了条件
* [ ] メンバー全員が上記の環境構築を完了する

## task
Required

# 2: ルーティング定義
## 概要
* 各チームのGoogleドライブにある「ルーティング定義書」にルーティングを定義する

## 完了条件
* [ ] チーム内レビュー完了

## task
Required

# 3: Agent_ヘッダー
## 要件
[Figma未ログイン](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88-(%E3%82%B3%E3%83%94%E3%83%BC)?type=design&node-id=142-11596&mode=design&t=1yVj1jf1KaeGVoYl-0)
[Figmaログイン済](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88-(%E3%82%B3%E3%83%94%E3%83%BC)?type=design&node-id=149-13053&mode=design&t=1yVj1jf1KaeGVoYl-0)

* Agentページ用のヘッダー
* ログインするとユーザー名が表示される
* ユーザー名をクリックするとトグルメニューが表示される（※表示されるところまでの実装でOKです）
* 左上のアイコンをクリックするとTOPに遷移する

## 完了条件
* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 4: Agent_フッター
## 要件
[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88-(%E3%82%B3%E3%83%94%E3%83%BC)?type=design&node-id=142-11616&mode=design&t=1yVj1jf1KaeGVoYl-0)
* 状況によっての変化はなし

## 完了条件
* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 5: Agent_物件一覧
## 要件
Figma
* https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=0TZfPdAIwIZt2HFD-0

- ログインしているAgentの物件が一覧で表示される
    - updated_atの降順で表示
    - 20件ごとのページネーション
    - 画像は登録1枚めのみ表示
- ソート、検索は別チケットで対応

## 完了条件
* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 6: Agent_物件新規登録
## 要件
[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11476&mode=design&t=0TZfPdAIwIZt2HFD-0)

- [物件一覧の「物件の登録」ボタン](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=0TZfPdAIwIZt2HFD-0)押下で遷移する
- 正しく入力し「登録」ボタン押下で正常に登録が完了すると[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=0TZfPdAIwIZt2HFD-0)にリダイレクトする
- 「一覧へ戻る」をクリックで[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=0TZfPdAIwIZt2HFD-0)に遷移する
- バリデーション
    - 全て空NG→「入力してください」
    - 建物種別、間取り
        - 選択されていない場合→「選択してください」
    - 賃料、管理費、敷金、礼金
        - 半角数字以外→「半角数字で入力してください」
        - 0はOK
    - 築年月
        - 空白→「日付を入力してください」
        - カレンダー方式で入力できること（date_field）
    - エリア
        - 都道府県または市区町村が一つでも空欄の場合→「都道府県または市区町村を選択してください」
    - 交通
        - 1つは必ず登録すること
        - 時間→「半角数字で入力してください」
    - 設備
        - 全て未チェックでもOK
    - 画像
        - 1枚は必須→「画像が選択されていません」
        - 1枚目が物件一覧で表示される画像
        - 並び替えは不要
        - 削除機能は不要

## 完了条件
* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 7: User_ログイン
## 要件
[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11235&mode=design&t=0TZfPdAIwIZt2HFD-0)

- Auth0を用いて認証を実装すること
- 正しくメールアドレス、パスワードを入力し「ログイン」ボタンを押下するとログイン状態になり[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11119&mode=design&t=0TZfPdAIwIZt2HFD-0)にリダイレクトする
- メールアドレス、パスワードのどちらかが違う場合「メールアドレス、もしくはパスワードが違います」というエラーメッセージが表示される
- 「新規登録」ボタンを押下すると[新規登録画面](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11198&mode=design&t=0TZfPdAIwIZt2HFD-0)に遷移する
- 「パスワードをお忘れですか？」を押下すると[パスワード再設定](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=419-10350&mode=design&t=0TZfPdAIwIZt2HFD-0)画面に遷移する

## 完了条件
* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 8: User_ログアウト
## 要件
[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11095&mode=design&t=0TZfPdAIwIZt2HFD-0)

- Auth0を用いて認証を実装すること
- ヘッダーのトグルメニューから「ログアウト」を押下するとログアウトされ、[ログイン画面](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11235&mode=design&t=0TZfPdAIwIZt2HFD-0)にリダイレクトする

## 完了条件
* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 9: User_物件一覧:front
## 要件
[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11119&mode=design&t=0TZfPdAIwIZt2HFD-0)

- DBに存在する物件がupdated_atの降順で表示される
- 20件ごとのページネーション
- ソート、検索、お気に入り、お問い合わせは別チケットで対応する

## 完了条件
* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 10: User_物件検索
## 要件
[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11119&mode=design&t=0TZfPdAIwIZt2HFD-0)

- 全ての項目はAND検索とする
- エリア
    - 1つ目のプルダウンで都道府県を選択できる
    - 1つ目を選択すると2つ目のプルダウンが表示され、市区町村が選択できる
- 駅名
    - 1つ目のプルダウンで路線を選択できる
    - 1つ目を選択すると2つ目のプルダウンが表示され、駅名が選択できる
- キーワード
    - 以下項目の部分一致検索
        - 物件名
        - 住所
- 賃料
    - 万単位でプルダウンで選択できる
- 築年数
    - 以下の選択肢でプルダウンが表示される
        - 1年未満
        - 3年未満
        - 5年未満
        - 10年未満
        - 15年未満
        - 20年未満
        - 30年未満
- 駅までの徒歩時間
    - 以下の選択肢でプルダウンが表示される
        - 3分以内
        - 5分以内
        - 7分以内
        - 10分以内
        - 15分以内
        - 20分以内
        - 30分以内
- 1件も該当する物件がなければ[該当なし](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11079&mode=design&t=0TZfPdAIwIZt2HFD-0)の表示をする

## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 11: User_物件ソート
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11119&mode=design&t=0TZfPdAIwIZt2HFD-0)

- 右上のプルダウンで選択した選択肢でのソートを実現する
    - 選択肢は以下
        - 新着順（created_at）
        - 賃料が安い順（rent）
        - 築年数が新しい順（build_date）
- 検索条件は保持したままソートができること


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 12: User_物件詳細
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10982&mode=design&t=0TZfPdAIwIZt2HFD-0)
[画像最大枚数](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=242-10473&mode=design&t=0TZfPdAIwIZt2HFD-0)

- [物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11119&mode=design&t=0TZfPdAIwIZt2HFD-0)の物件欄（区切り線の中）をクリックすると遷移する
- 画像
    - 右側に最大6枚の登録されている画像を表示する
    - 右側で選択した画像を左側に大きく表示する
- 物件詳細情報
    - 必要な情報を表示
- この物件の特徴
    - 該当するものが水色アイコンになる
- 代理店情報
    - 必要な情報を表示
- 一覧へ戻るをクリックで[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11119&mode=design&t=0TZfPdAIwIZt2HFD-0)に遷移する
- お気に入り、問い合わせボタンは別チケットで対応する


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 13: User_お気に入り一覧
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10960&mode=design&t=zRuBrp5zhjJzAT1r-0)

- [ヘッダーのハンバーガーメニュー内「お気に入り物件」](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11095&mode=design&t=zRuBrp5zhjJzAT1r-0)を押下で遷移できる
- ログインユーザーがお気に入りした物件が一覧で表示される
- 登録日の降順で表示
- 検索、ソート、お気に入り解除は別チケットで対応
- 20件ごとのページネーション
- 「お問い合わせ」を押下で[お問い合わせ](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10905&mode=design&t=zRuBrp5zhjJzAT1r-0)ページに遷移する
- お気に入りが0件の場合は[こちら](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10944&mode=design&t=zRuBrp5zhjJzAT1r-0)


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 14: Gest_物件一覧
## 要件
[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11140&mode=design&t=zRuBrp5zhjJzAT1r-0)

- ログイン状態との違い
    - 「お気に入り」ボタン押下で[ユーザー登録を促すモーダル](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=2682-5338&mode=design&t=ME5lOBVQu9ahF2AU-0)が表示される
    - お気に入りはログイン状態でないとできない


## 完了条件
* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 15: Agent_ログイン
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11596&mode=design&t=egp1LRgeUidwhaW6-0)

- Auth0を用いて認証を実装すること
- メールアドレス、パスワードを入力後「ログイン」を押下
    - 合っていれば[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=egp1LRgeUidwhaW6-0)に遷移する
    - 間違っている場合「メールアドレス、もしくはパスワードが違います」とエラーメッセージを表示する
- 「ログイン」ボタンはエンターボタン押下でも押下できること
- 「パスワードの再発行はこちら」をクリックで[パスワード再発行](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=426-11382&mode=design&t=0TZfPdAIwIZt2HFD-0)に遷移する
- 今回のPJではAgentを新規登録する機能は実装しないため、DBにあらかじめ情報を登録しておくこと

## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 16: Agent_ログアウト
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=149-13053&mode=design&t=0TZfPdAIwIZt2HFD-0)

- Auth0を用いて認証を実装すること
- ログインしている状態でヘッダーのユーザー名をクリックすると表示されるトグルメニューに「ログアウト」が存在する
- 「ログアウト」をクリックするとログアウト状態となり、[ログイン](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11596&mode=design&t=0TZfPdAIwIZt2HFD-0)画面に遷移する（確認モーダルなどは無し）


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 17: Agent_物件編集
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11377&mode=design&t=0TZfPdAIwIZt2HFD-0)

- [物件一覧のペンマーク](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=0TZfPdAIwIZt2HFD-0)をクリックで遷移する
- バリデーションについては新規作成チケットに記載
- 正しく編集が完了したら[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=0TZfPdAIwIZt2HFD-0)にリダイレクトする
- 「一覧へ戻る」をクリックで[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=0TZfPdAIwIZt2HFD-0)に遷移する


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 18: Agent_物件削除
## 要件

- [物件一覧のゴミ箱マーク](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=0TZfPdAIwIZt2HFD-0)をクリックすると、[確認モーダル](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=149-13539&mode=design&t=0TZfPdAIwIZt2HFD-0)が表示される
- 「キャンセル」ボタンをクリックするとモーダルが消える
- モーダル右上の×をクリックするとモーダルが消える
- モーダル外をクリックするとモーダルが消える
- 「削除する」ボタンをクリックすると物件が削除（論理削除）され、モーダルが消える

## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 19: User_ヘッダー
## 要件

[未ログイン(ゲスト)](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11140&mode=design&t=0TZfPdAIwIZt2HFD-0)

[ログイン後](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11119&mode=design&t=0TZfPdAIwIZt2HFD-0)

- 未ログイン(ゲスト)の状態で「ゲスト」の右のアイコンをクリックすると[ログイン画面](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11235&mode=design&t=0TZfPdAIwIZt2HFD-0)へ遷移する
- ログイン状態ではヘッダーにユーザー名が表示される
- ログイン状態でヘッダーのユーザー名の右のハンバーガーメニューアイコンをクリックすると、[トグルメニュー](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11095&mode=design&t=0TZfPdAIwIZt2HFD-0)が表示される
- トグルメニューへの遷移は別チケットで対応
- 左上のアイコンをクリックするとTOPに遷移する

## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 20: User_フッター

## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11140&mode=design&t=0TZfPdAIwIZt2HFD-0)

- ログイン、未ログインに関わらず同一のデザイン


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 21: User_新規登録
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11198&mode=design&t=0TZfPdAIwIZt2HFD-0)

- Auth0を用いて認証を実装すること
- [ログイン画面の「新規登録」ボタン](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11235&mode=design&t=0TZfPdAIwIZt2HFD-0)を押下で遷移する画面
- 「登録済みの方はこちら」を押下すると[ログイン画面](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11235&mode=design&t=0TZfPdAIwIZt2HFD-0)に遷移する
- 全て正しく入力し、「登録」ボタンを押下し、正常に登録が完了するとログインした状態で[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11119&mode=design&t=0TZfPdAIwIZt2HFD-0)にリダイレクトする
- バリデーション
    - 全て必須
        - 空の場合→「入力してください」のエラーメッセージを表示
    - メールアドレス
        - メースアドレス形式でない場合→「メールアドレスが正しい形式ではありません」のエラーメッセージを表示
    - 郵便番号、電話番号
        - ハイフンあり→「ハイフン無しで入力してください」
        - 半角数字以外→「半角数字で入力してください」
    - パスワード
        - 8文字以上16文字未満でない→「8文字以上16文字未満で入力してください」
        - 英数字が含まれていない→「半角英数字で入力してください」


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 22: User_お気に入り追加
## 要件

[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11119&mode=design&t=zRuBrp5zhjJzAT1r-0)
[物件詳細](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10982&mode=design&t=zRuBrp5zhjJzAT1r-0)

- 上記2つの画面から「お気に入り」ボタンをクリックすることでお気に入りに登録できる
- 非同期
- お気に入り状態になると「お気に入り解除」というボタン表示に変わる


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 23: User_お気に入り解除

## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10960&mode=design&t=zRuBrp5zhjJzAT1r-0)

- お気に入り状態で「お気に入り解除」ボタンを押下すると解除される
- 非同期
- [お気に入り一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10960&mode=design&t=zRuBrp5zhjJzAT1r-0)で解除すると、リロードするまでは一覧に表示されている（ボタン表示は「お気に入り」）


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 24: migration・seed作成
## 要件

* migrationファイル・seedファイルともに作成済みではあるが、変更が必要であれば適宜対応すること

### seedファイル
* seedファイルはある程度作成してはいるが、あくまでも参考程度にし、必要に応じて修正すること
* seedファイルを使用する場合、modelが定義されていない段階ではエラーが起きるため、一部をコメントアウトするなどして対応すること

### seedデータ
* 下記の条件を満たすデータが含まれていること


* [ ] User
    * 2名以上
* [ ] Property
    * 100件以上
        * 賃料
            * 5パターン以上（全物件同じ金額はNG）
        * 間取り
            * 5パターン以上（全物件同じ間取りはNG）
        * 建物種類
            * 全建物種類のデータがあること
        * 築年数
            * 5パターン以上（全物件同じ築年数はNG）
        * 駅までの徒歩時間
            * 5パターン以上（全物件同じ徒歩時間はNG）
* [ ] Amenity
    * property A：設備の登録2つ以上
    * property B：設備の登録なし
* [ ] Area
    * property A：東京都 新宿区
    * property B：東京都 新宿区
    * property C：東京都 渋谷区
    * property D：大阪府 北区
* [ ] NearStation
    * property A：JR山手線 高田馬場駅・都電荒川線 学習院下駅・東京メトロ副都心線 西早稲田駅
    * property B：JR山手線 高田馬場駅・JR山手線 目白駅
    * property C：JR山手線 新宿駅
    * property D：東京メトロ東西線 高田馬場駅
* [ ] Agent
    * 2名以上
* [ ] Holiday
    * agent A：定休日の登録2つ以上
    * agent B：定休日の登録なし
* [ ] Inquiry
    * 計100件以上
        * ログインユーザー
            * inquiry A：対応済み
            * inquiry B：未対応
        * ゲストユーザー
            * inquiry C：対応済み
            * inquiry D：未対応
* [ ] Like
    * user A：お気に入り登録100件以上
    * user B：お気に入り登録なし

# 完了条件

* [ ] migrationファイル作成
* [ ] seedファイル作成
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 25: Agent_パスワード再発行
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=426-11382&mode=design&t=0TZfPdAIwIZt2HFD-0)

- Auth0を用いて認証を実装すること
- [ログイン画面の「パスワード再発行はこちら」](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11596&mode=design&t=0TZfPdAIwIZt2HFD-0)をクリックして遷移する
- メールアドレスを入力し「メール送信」ボタンで再発行用のメールが送信される
    - DBに存在しないメールアドレスが入力された状態で「メール送信」ボタンが押下された→「メールアドレスが存在しません」のエラーメッセージが表示される
    - 空の状態で「メール送信」ボタンが押下された→「メールアドレスを入力してください」というエラーメッセージが表示される
    - メールアドレス形式でない値が入力された状態で「メール送信」ボタンが押下された→「メールアドレスが正しい形式ではありませんと表示される」というエラーメッセージが表示される
    - フォームにフォーカスがある状態でエンターボタンをクリックすると「メール送信」ボタンが押下できること
- 「ログイン画面に戻る」をクリックで[ログイン画面](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11596&mode=design&t=0TZfPdAIwIZt2HFD-0)に遷移する


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Challenge

# 26: Agent_パスワード変更
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=426-11398&mode=design&t=0TZfPdAIwIZt2HFD-0)

- Auth0を用いて認証を実装すること
- 再発行メールのリンクを踏むと上記Figmaの画面に遷移する
- パスワードの要件は下記
    - 8文字以上16文字未満
    - 英数字
- 新しいパスワード、新しいパスワード再入力のフォームにパスワードを入力し、「変更する」ボタン押下でパスワードの変更が可能
    - 正常に変更できれば[ログイン画面](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11596&mode=design&t=0TZfPdAIwIZt2HFD-0)に遷移する
    - 「新しいパスワード」と「新しいパスワード再入力」の値が一致していない状態で「変更する」ボタン押下→「パスワードが一致していません」というエラーメッセージが表示される
    - 8文字以上16文字未満ではない状態で「変更する」ボタン押下→「パスワードは8文字以上16文字未満で入力してください」というエラーメッセージが表示される
    - 英数字が含まれていない状態で「変更する」ボタン押下→「パスワードは英数字を含んでください」というエラーメッセージが表示される
    - 空の状態で「変更する」ボタン押下→「パスワードを入力してください」というエラーメッセージが表示される


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Challenge

# 27: Agent_物件検索
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=0TZfPdAIwIZt2HFD-0)

- キーワードでの部分一致検索
    - 物件名
    - 住所
- ヒットする物件が0の場合は「条件にあう物件が見つかりませんでした。条件を変更して再度検索してください。」と表示される


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Optional

# 28: Agent_物件一覧ソート
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=559-10625&mode=design&t=0TZfPdAIwIZt2HFD-0)

- 賃料でのソート
    - 賃料と管理費の列は同じだが、ソート対象は賃料


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Optional

# 29: Agent_ユーザー情報編集
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11307&mode=design&t=0TZfPdAIwIZt2HFD-0)

- [ヘッダーのトグルメニュー内「ユーザー情報の編集」](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=149-13053&mode=design&t=0TZfPdAIwIZt2HFD-0)を押下で遷移する
- バリデーション（全て「更新」ボタン押下でバリデーション発火）
    - 全て空はNG→「〜〜〜を入力してください」のエラーメッセージを表示する
    - 電話番号
        - ハイフン無し→「ハイフンなしで入力してください」
    - メールアドレス
        - メールアドレス形式であること→「メールアドレスが正しい形式ではありませんと表示される」
    - 郵便番号
        - ハイフン無し→「ハイフンなしで入力してください」
        - 7桁→「7桁で入力してください」
- 「更新」ボタン押下で正しく更新ができた場合、[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=0TZfPdAIwIZt2HFD-0)にリダイレクトする
- 「一覧へ戻る」をクリックすると[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=0TZfPdAIwIZt2HFD-0)に遷移する
## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Optional

# 30: Agent_お問い合わせ一覧
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11255&mode=design&t=0TZfPdAIwIZt2HFD-0)

- ユーザーからの物件への問い合わせが表示される
- created_atの降順で表示
- 20件ずつのページネーション
- ソート不要
- 検索は別チケットで対応
- ステータス変更は別チケットで対応
- 「物件一覧へ戻る」ボタンを押下で[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11592&mode=design&t=0TZfPdAIwIZt2HFD-0)に遷移する


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 31: Agent_お問い合わせ検索
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11255&mode=design&t=0TZfPdAIwIZt2HFD-0)

- 以下カラムからキーワード検索（部分一致）
    - 問い合わせ者名
    - お問い合わせ内容

## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Optional

# 32: Agent_お問い合わせステータス変更
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11255&mode=design&t=ME5lOBVQu9ahF2AU-0)

- 問い合わせの対応をしたらチェックを入れる


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Optional

# 33: User_パスワード再設定
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=419-10350&mode=design&t=0TZfPdAIwIZt2HFD-0)

- 認証はAuth0を用いて実装する
- [ログイン画面の「パスワードをお忘れですか？」](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11235&mode=design&t=0TZfPdAIwIZt2HFD-0)をクリックして遷移する
- メールアドレスを入力し「メール送信」ボタンで再発行用のメールが送信される
- DBに存在しないメールアドレスが入力された状態で「メール送信」ボタンが押下された→「メールアドレスが存在しません」のエラーメッセージが表示される
- 空の状態で「メール送信」ボタンが押下された→「メールアドレスを入力してください」というエラーメッセージが表示される
- メールアドレス形式でない値が入力された状態で「メール送信」ボタンが押下された→「メールアドレスが正しい形式ではありませんと表示される」というエラーメッセージが表示される
- フォームにフォーカスがある状態でエンターボタンをクリックすると「メール送信」ボタンが押下できる
「ログイン画面に戻る」をクリックで[ログイン画面](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11235&mode=design&t=0TZfPdAIwIZt2HFD-0)に遷移する


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Challenge

# 34: User_パスワード変更
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=419-10374&mode=design&t=0TZfPdAIwIZt2HFD-0)

- 認証はAuth0を用いて実装する
- 再発行メールのリンクを踏むと上記Figmaの画面に遷移する
- パスワードの要件は下記
    - 8文字以上16文字未満
    - 英数字
- 新しいパスワード、新しいパスワード再入力のフォームにパスワードを入力し、「変更する」ボタン押下でパスワードの変更が可能
- 正常に変更できれば[ログイン画面](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11235&mode=design&t=0TZfPdAIwIZt2HFD-0)に遷移する
- 「新しいパスワード」と「新しいパスワード再入力」の値が一致していない状態で「変更する」ボタン押下→「パスワードが一致していません」というエラーメッセージが表示される
- 8文字以上16文字未満ではない状態で「変更する」ボタン押下→「パスワードは8文字以上16文字未満で入力してください」というエラーメッセージが表示される
- 英数字が含まれていない状態で「変更する」ボタン押下→「パスワードは英数字を含んでください」というエラーメッセージが表示される
- 空の状態で「変更する」ボタン押下→「パスワードを入力してください」というエラーメッセージが表示される


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Challenge

# 35: User_お気に入りソート
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10960&mode=design&t=zRuBrp5zhjJzAT1r-0)

* 右上のプルダウンで選択した選択肢でのソートを実現する
    * 選択肢は以下
        * 新着順（created_at）
        * 賃料が安い順（rent）
        * 築年数が新しい順（build_date）
        * 登録した順（likeのcreated_at）
* 検索条件は保持したままソートができること


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Optional

# 36: User_お気に入り検索
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10960&mode=design&t=zRuBrp5zhjJzAT1r-0)

- 全ての項目はAND検索とする
- エリア
    - 1つ目のプルダウンで都道府県を選択できる
    - 1つ目を選択すると2つ目のプルダウンが表示され、市区町村が選択できる
- 駅名
    - 1つ目のプルダウンで路線を選択できる
    - 1つ目を選択すると2つ目のプルダウンが表示され、駅名が選択できる
- キーワード
    - 以下項目の部分一致検索
        - 物件名
        - 住所
- 賃料
    - 万単位でプルダウンで選択できる
- 築年数
    - 以下の選択肢でプルダウンが表示される
        - 1年以内
        - 3年以内
        - 5年以内
        - 10年以内
        - 15年以内
        - 20年以内
        - 30年以内
- 駅までの徒歩時間
    - 以下の選択肢でプルダウンが表示される
        - 3分以内
        - 5分以内
        - 7分以内
        - 10分以内
        - 15分以内
        - 20分以内
        - 30分以内
- 1件も該当する物件がなければ「条件にあう物件が見つかりませんでした。条件を変更して再度検索してください。」と表示される

## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Optional

# 37: User_お問い合わせ作成
## 要件

### お問い合わせ入力

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10905&mode=design&t=zRuBrp5zhjJzAT1r-0)

- 「お問い合わせ」ボタンを押下で遷移する
- お問い合わせ内容は以下3つ
    - 空室状況を知りたい
    - 実際に見学したい
    - 詳しく教えてほしい
- お問い合わせ詳細
    - 空欄でも可
- ログイン状態だと名前、メールアドレス、電話番号は自動でUser情報から反映される
    - 編集もできる
    - バリデーションはUser登録時と同じ
- 「確認画面へ進む」を押下すると[確認画面](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10878&mode=design&t=zRuBrp5zhjJzAT1r-0)に遷移する
- 「物件詳細に戻る」を押下すると[物件詳細](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10982&mode=design&t=zRuBrp5zhjJzAT1r-0)に遷移する

### お問い合わせ確認画面

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10878&mode=design&t=zRuBrp5zhjJzAT1r-0)

- 作成画面で入力した内容が反映される
- 「送信」ボタンを押下で[お問い合わせ完了](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10864&mode=design&t=zRuBrp5zhjJzAT1r-0)画面にリダイレクトする
- 「入力画面へ戻る」で[お問い合わせ作成画面](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10905&mode=design&t=zRuBrp5zhjJzAT1r-0)に戻る。入力していたデータは保持したままにすること

### お問い合わせ完了画面

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10864&mode=design&t=zRuBrp5zhjJzAT1r-0)

- 「物件詳細へ戻る」を押下で[物件詳細](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-10982&mode=design&t=zRuBrp5zhjJzAT1r-0)に遷移する

## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Required

# 38: User_マイページ
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=546-11378&mode=design&t=zRuBrp5zhjJzAT1r-0)

- ヘッダーのハンバーガーメニュー[マイページ](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11095&mode=design&t=zRuBrp5zhjJzAT1r-0)を押下で遷移する
- バリデーションはUser新規登録時と同じ
- 「更新」ボタン押下で正しく編集が完了したら情報が更新された状態で、ユーザー編集画面を表示する
- 「物件一覧へ戻る」を押下で[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11119&mode=design&t=zRuBrp5zhjJzAT1r-0)へ遷移する
- アカウント削除は別チケットで対応


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Optional

# 39: User_アカウント削除
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=546-11378&mode=design&t=zRuBrp5zhjJzAT1r-0)

- ヘッダーのハンバーガーメニュー[マイページ](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11095&mode=design&t=zRuBrp5zhjJzAT1r-0)を押下で遷移する
- 「アカウントを削除する」ボタンを押下で[確認モーダル](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=546-11485&mode=design&t=zRuBrp5zhjJzAT1r-0)が表示される
- 「アカウントを削除することに同意する」にチェックを入れると[ボタンが活性化](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=546-11829&mode=design&t=zRuBrp5zhjJzAT1r-0)する
- 「キャンセル」ボタン押下でモーダルが消える
- 右上×を押下でモーダルが消える
- モーダル外を押下でモーダルが消える
- 「削除する」を押下で正常にアカウントを論理削除できたら、[物件一覧](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=142-11140&mode=design&t=zRuBrp5zhjJzAT1r-0)にリダイレクトする


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Optional

# 40: Gest_お問合せ作成
## 要件

[Figma](https://www.figma.com/file/ViB4zNl1vE0aPAWFX1u3yn/%E4%B8%8D%E5%8B%95%E7%94%A3%E6%A4%9C%E7%B4%A2%E3%82%B5%E3%82%A4%E3%83%88?type=design&node-id=420-10398&mode=design&t=zRuBrp5zhjJzAT1r-0)

- ログイン状態との違い
    - 名前、メールアドレス、電話番号が自動で入力されない


## 完了条件

* [ ] 要件を満たして実装完了
* [ ] チーム内レビュー完了
* [ ] developブランチにマージ

## task
Optional

# 41: 成果発表会準備
# 概要
## 成果発表会とは
作成した不動産検索サイトと、チーム開発で学んだことをPRUMの社員に発表する会を開催する。
[6th_不動産検索サイト成果発表会](https://drive.google.com/drive/folders/1Y5x4VwKA6vYp_LiJW1flrrGVTkKfRc3C)
※動画上では勉強会内で発表を行なっていますが、運用が変わり、勉強会とは切り離し成果物発表会単体で行うようになりました。

## 日時
* 平日19:00-22:00の間で15分

## 場所
* GoogleMeets

## 参加メンバー
* 開発メンバー
* 成果発表会参加者

## 開発チームが準備すること
* 成果発表会の日程調整
    * 開発チームで話し合い、Slackの`#all-全社`チャンネルで全社員向けに告知する
    * カレンダーで招待する場合、 「all@prum.jp」 を参加者に入れる

* 発表スライド
    * 例)
        * [5th](https://docs.google.com/presentation/d/1RIV9L50UEKVH76sdmjMm5nxETLdGbwgAnCy2Reapsek/edit#slide=id.g256eaa534a6_0_218)
        * [6th](https://docs.google.com/presentation/d/1ghWZJ7gKxpfCwnr0wcGC922CAj7KuPPQg_Oc-tSAYMU/edit#slide=id.p)

# 完了条件

* 成果発表会を開催する。

## task
Required
"""

def parse_tasks(text):
    tasks = []
    # Split by "# N: " pattern
    # Using regex to find start of each task
    pattern = re.compile(r'^# (\d+): (.+)$', re.MULTILINE)
    
    matches = list(pattern.finditer(text))
    
    for i, match in enumerate(matches):
        task_num = match.group(1)
        title = match.group(2).strip()
        
        start_pos = match.end()
        if i < len(matches) - 1:
            end_pos = matches[i+1].start()
        else:
            end_pos = len(text)
            
        body_content = text[start_pos:end_pos].strip()
        
        # Extract labels from body
        # Look for "## task" and the following line
        label_pattern = re.compile(r'## task\s*\n(.+)', re.MULTILINE)
        label_match = label_pattern.search(body_content)
        
        labels = "task"
        if label_match:
            priority = label_match.group(1).strip()
            labels = f"task,{priority}"
            # Remove the label section from body
            body_content = label_pattern.sub('', body_content).strip()
        
        # Clean up body (remove trailing newlines)
        body_content = body_content.strip()
        
        tasks.append({
            'title': title,
            'body': body_content,
            'labels': labels,
            'assignee': '',
            'milestone': '',
            'priority': 'medium'
        })
        
    return tasks

def write_csv(tasks, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'body', 'labels', 'assignee', 'milestone', 'priority'])
        writer.writeheader()
        writer.writerows(tasks)
    print(f"Successfully wrote {len(tasks)} tasks to {filename}")

if __name__ == "__main__":
    tasks = parse_tasks(raw_text)
    write_csv(tasks, '/Users/ryo.akachi/ai/acacemy-level3-template/data/tasks_for_real_estate.csv')
