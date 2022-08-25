import PySimpleGUI as sg
import cv2
import main
import numpy as np

gui_font = 'Meiryo UI'

def draw():
    '''************************************************************
    ** レイアウトの定義
    ************************************************************'''
    sg.theme('LightBlue')

    layout_1 = [  
        [sg.Text('ファイル'), sg.Input(), sg.FileBrowse('ファイルを選択', key='inputFilePath')], 
        [sg.Button('開始', key='startButton'), sg.Button('停止', key='stopButton'), sg.Button('アプリ終了', key='exitButton')], 
        [sg.Checkbox('プレビュー表示', False, key='previewCheckbox', font=(gui_font, 13))],  
        # [sg.Text('', key='analysisStatus')], 
        [sg.Text('', key='killCountText', font=(gui_font, 13))], 
        [sg.Text('', key='fpsText', font=(gui_font, 13))], 
    ]

    layout_2 = [
        [sg.Image(filename='', key='previewImage')]
    ]

    layout_3 = [
        [sg.Output(size=(80,20))], 
        [sg.Button('コピー', key='copyButton'), sg.Button('停止', key='saveButton')]
    ]




    layout=[
        [sg.Frame('Group 1', layout_1, size=(480, 200))], 
        [
            sg.Frame('Group 2', layout_2, size=(1920*0.2, 1080*0.2+50)), 
            sg.Frame('Group 3', layout_3, size=(230, 1080*0.2+50)), 
        ], 
        
    ]
                
    # ウィンドウの生成
    window = sg.Window('POP1 Kill Extractor', layout)


    cap = cv2.VideoCapture('../videos/test_1.mp4')

    main.start_proc()


    while True:
        # timeout: 小さいほど滑らか
        event, values = window.read(timeout=100)
        
        if event == 'exitButton' or event == sg.WIN_CLOSED:
            break

        ret, frame = cap.read()

        if not ret:
            continue

        current_sec = cap.get(cv2.CAP_PROP_POS_MSEC)

        frame = main.proc(frame, current_sec=current_sec)
        frame = cv2.resize(frame, dsize=None, fx=0.2, fy=0.2)
        
        if values['previewCheckbox']:
            bytes = cv2.imencode('.png', frame)[1].tobytes()
            window['previewImage'].update(data=bytes)
        else:
            tmp = np.zeros_like(frame)
            bytes = cv2.imencode('.png', tmp)[1].tobytes()
            window['previewImage'].update(data=bytes)

        if event == 'copyButton':
            main.copy_kill_time()

        kill_count_text = 'キル数: {}'.format(main.detection_count)
        window['killCountText'].update(kill_count_text)

        fps_text = 'fps: {:.2f}'.format(main.fps)
        window['fpsText'].update(fps_text)
        

    cap.release()
    window.close()


if __name__ == '__main__':
    draw()