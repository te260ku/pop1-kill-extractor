import PySimpleGUI as sg
import cv2
import main

sg.theme('LightBlue')

gui_font = 'Meiryo UI'

processing = False

layout_1 = [  
    [sg.Text('ファイル', size=(10, 1)), sg.Input(), sg.FileBrowse('ファイルを選択', key='inputFilePath')], 
    # [sg.Text('ここは2行目：適当に文字を入力してください'), sg.InputText()],
    [sg.Button('開始', key='startButton'), sg.Button('停止', key='stopButton'), sg.Button('アプリ終了', key='exit')], 
    [sg.Checkbox('プレビュー表示', False, key='previewCheckbox', font=(gui_font, 13))],  
]

layout_2 = [
    [sg.Text('', key='analysisStatus')], 
    [sg.Image(filename='', key='previewImage',)]
]

layout_3 = [
    [sg.Output(size=(80,20))]
]


layout=[
    [sg.Frame('Group 1', layout_1, size=(480, 100))], 
    [
        sg.Frame('Group 2', layout_2, size=(230, 200)), 
        sg.Frame('Group 3', layout_3, size=(230, 200)), 
    ], 
]
            
# ウィンドウの生成
window = sg.Window('サンプルプログラム', layout, size=(500, 500))



# イベントループ
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'exit':
        break
    elif event == 'startButton':
        window['analysisStatus'].update('Processing...')
        cap = cv2.VideoCapture('../videos/test_full.mp4')
        processing = True
    elif event == 'stopButton':
        window['analysisStatus'].update('')
        recording = False

    
    if (processing == True):
        
        
        # フレームを取得
        ret, frame = cap.read()
        
        if ret is True:
            current_sec = cap.get(cv2.CAP_PROP_POS_MSEC)
            result = cv2.imencode('.png', frame)[1].tobytes() 
            # result = main.proc(frame, current_sec=current_sec)
            window['previewImage'].update(data=result)
            

cap.release()
window.close()