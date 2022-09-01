# POP1 Kill Extractor

VRゲーム「[POPULATION: ONE](https://www.populationonevr.com/)」のプレイ映像から、自動的にキルシーンを抽出してキル集を作成するプログラムです。画像認識を使って動画中のキルログを検出します。

## アプリ画面

<img width="635" alt="スクリーンショット 2022-09-01 19 57 35" src="https://user-images.githubusercontent.com/34476697/187898312-d1ea485d-eb72-4bdf-8972-1d7e7e091cef.png">

## 出力映像
[![''](https://user-images.githubusercontent.com/34476697/187898730-a0e5bd7f-fb28-434e-8fa1-94b87ffe70a2.png)](https://youtu.be/KIDa9pQgZP4)

## 実行環境
- Mac OS 10.14.6
- Python 3.9.12
- OpenCV 4.4.0

## 使用方法
ターミナルからscripts/gui.pyを実行することでGUIが起動します。動画ファイルを選択して、開始ボタンを押すと解析が始まります。解析が終了したら、切り出しボタンを押すことで、キルシーンを集めた動画を出力することができます。今後はexeファイル化して配布したいと思っています。
