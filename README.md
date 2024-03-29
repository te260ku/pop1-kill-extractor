# POP1 Kill Extractor

VRゲーム「[POPULATION: ONE](https://www.populationonevr.com/)」のプレイ映像から、自動的にキルシーンを抽出してキル集を作成するプログラムです。画像認識を使って動画中のキルログを検出します。

## アプリ画面
![pop1](https://github.com/te260ku/pop1-kill-extractor/assets/34476697/f0ac1a11-91fc-4f67-b943-e788a1863e3e)

## 出力映像例
実際にプログラムを使って自分のプレイ映像から自動生成したキル集です。自分が行ったのはBGMを入れる作業だけです。

[![''](https://user-images.githubusercontent.com/34476697/187898730-a0e5bd7f-fb28-434e-8fa1-94b87ffe70a2.png)](https://youtu.be/KIDa9pQgZP4)

## 実行環境
- Mac OS 10.14.6
- Python 3.9.12
- OpenCV 4.4.0

## 使用方法
ターミナルからflet_ocr.pyを実行することでGUIが起動します。動画ファイルを選択して、開始ボタンを押すと解析が始まります。解析が終了したら、切り出しボタンを押すことで、キルシーンを集めた動画を出力することができます。

## 更新・追記
※（更新：2022/9/2）Windowsの場合は、とりあえずscripts/gui_win.pyを実行すれば動くようにしました。
※（追記：2022/9/26）現状、周囲の景観に白色が多く含まれている場合やマップを開いたときなどに誤検出する問題が確認されています。誤検出の詳しい原因は調査中です。
