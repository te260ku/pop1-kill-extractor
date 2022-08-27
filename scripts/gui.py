import PySimpleGUI as sg
import cv2
import numpy as np
import mimetypes
import main


gui_font = 'Meiryo UI'


def draw():
    processing = False
    select_valid_file = False

    '''************************************************************
    ** レイアウトの定義
    ************************************************************'''

    # テーマを指定
    sg.theme('LightBlue')

    # UIコンポーネントの定義
    file_select_button_comp = sg.FileBrowse('ファイルを選択', key='inputFilePath', font=(gui_font, 14))
    start_button_comp = sg.Button('開始', key='startButton', font=(gui_font, 14))
    stop_button_comp = sg.Button('停止', key='stopButton', font=(gui_font, 14))
    create_button_comp = sg.Button('切り出し', key='createButton', font=(gui_font, 14))
    exit_button_comp = sg.Button('アプリ終了', key='exitButton', font=(gui_font, 14))
    preview_checkbox_comp = sg.Checkbox('プレビュー表示', True, key='previewCheckbox', font=(gui_font, 14))
    processing_status_text_comp = sg.Text('Waiting...', key='processingStatusText', font=(gui_font, 14), expand_x=True, background_color='#87cefa', text_color='black', justification='center')


    preview_image_comp = sg.Image(filename='../images/initial_image.png', key='previewImage')
    progress_text_comp = sg.Text('0%', key='progressText', font=(gui_font, 14), size=(5,1))
    progress_bar_comp = sg.ProgressBar(100, orientation='h', size=(36.5,25), key='progressBar')


    kill_count_text_label_comp = sg.Text('キル数', font=(gui_font, 14), text_color='black', background_color='#c0c0c0', size=(7,1), pad=((5,0), (5,0)))
    kill_count_text_comp = sg.Text('', key='killCountText', font=(gui_font, 14), text_color='white', background_color='#808080', size=(10,1), expand_x=True, pad=((0,5), (5,0)))
    fps_text_label_comp = sg.Text('FPS', font=(gui_font, 14), text_color='black', background_color='#c0c0c0', size=(7, 1), pad=((5,0), (1,5)))
    fps_text_comp = sg.Text('', key='fpsText', font=(gui_font, 14), text_color='white', background_color='#808080', size=(10, 1), expand_x=True, pad=((0,5), (1,5)))
    kill_time_log_comp = sg.Multiline(size=(28,15), key='killTimeLog', disabled=True)
    copy_button_comp = sg.Button('コピー', key='copyButton', font=(gui_font, 14))
    save_button_comp = sg.Button('保存', key='saveButton', font=(gui_font, 14))

    layout_1 = [  
        [sg.Text('ファイル', font=(gui_font, 14)), sg.Input(font=(gui_font, 14)), file_select_button_comp], 
        [preview_checkbox_comp],  
        [start_button_comp, stop_button_comp, create_button_comp, exit_button_comp], 
        [processing_status_text_comp], 
    ]

    layout_2 = [
        [preview_image_comp], 
        [progress_text_comp, progress_bar_comp], 
    ]

    layout_3 = [
        [kill_count_text_label_comp, kill_count_text_comp], 
        [fps_text_label_comp, fps_text_comp], 
        [kill_time_log_comp],  
        [copy_button_comp, save_button_comp]
    ]


    layout=[
        [sg.Frame('Setting', layout_1, size=(1920*0.2+200+25, 150))], 
        [
            sg.Frame('Preview', layout_2, size=(1920*0.2+15, 1080*0.2+80)), 
            sg.Frame('Log', layout_3, size=(200, 1080*0.2+80)), 
        ], 
    ]
                
    # ウィンドウの生成
    window = sg.Window('POP1 Kill Extractor', layout)

    # FPS計測用のタイマーを開始する
    main.start_proc()

    cap = None


    while True:
        # timeout: 小さいほど滑らか
        event, values = window.read(timeout=10)

        '''************************************************************
        ** UIイベントの検出
        ************************************************************'''

        # 終了イベント
        if event == 'exitButton' or event == sg.WIN_CLOSED:
            break

        if event == 'startButton':
            if (processing == False):
                # 選択したファイルのパスを格納
                file_path = values['inputFilePath']
                if (file_path == ''):   # パスが空ならエラー
                    sg.popup('ファイルを選択してください', title='Error')
                    select_valid_file = False
                    continue
                mime = mimetypes.guess_type(file_path)
                if (mime[0].startswith('video/')):  # ファイル形式が動画の場合は処理を進める
                    cap = cv2.VideoCapture(file_path)
                    if (cap.isOpened() == False):
                        continue
                    window['processingStatusText'].update('Processing...')
                    window["processingStatusText"].update(background_color='#cd5c5c')
                    window["processingStatusText"].update(text_color='white')
                    processing = True
                    select_valid_file = True
                else:
                    sg.popup('ファイル形式が無効です', title='Error')
                    select_valid_file = False

        elif event == 'stopButton':
            window['processingStatusText'].update('Waiting...')
            window["processingStatusText"].update(background_color='#87cefa')
            window["processingStatusText"].update(text_color='black')
            processing = False

        elif event == 'createButton':
            if (select_valid_file):
                value = sg.popup_get_file('', save_as=True, title='保存先を選択')
                if (value == None or value == ''):
                    continue
                out = value + '.mp4'
                main.create_clip(file_path, out)
            else:
                sg.popup('ファイルを選択して解析してください', title='Error')

        elif event == 'copyButton':
            main.copy_kill_time()

        elif event == 'saveButton':
            value = sg.popup_get_file('', save_as=True, title='保存先を選択')
            if value is not None:
                main.save_kill_time(value)
            

        '''************************************************************
        ** 動画のプレビュー
        ************************************************************'''
        if (processing == True):
            ret, frame = cap.read()
            if not ret:
                # 動画が終了していたらプログレスバーを満タンにする
                window['progressBar'].update(100)
                window['progressText'].update('100%')
                continue

            current_sec = cap.get(cv2.CAP_PROP_POS_MSEC)

            # プログレスバーの更新
            progress_value = float('{:.1f}'.format((main.frame_count/cap.get(cv2.CAP_PROP_FRAME_COUNT))*100))
            window['progressBar'].update(progress_value)
            window['progressText'].update('{}%'.format(str(progress_value)))
            
            # 解析用の関数にフレームを渡す
            frame = main.proc(frame, current_sec=current_sec)
            # プレビュー表示用に縮小
            frame = cv2.resize(frame, dsize=None, fx=0.2, fy=0.2)
            
            if values['previewCheckbox']:
                bytes = cv2.imencode('.png', frame)[1].tobytes()
                window['previewImage'].update(data=bytes)
            else:   # プレビューがオフの場合は真っ黒の画面を表示する
                tmp = np.zeros_like(frame)
                bytes = cv2.imencode('.png', tmp)[1].tobytes()
                window['previewImage'].update(data=bytes)

        kill_count_text = '{}'.format(main.detection_count)
        window['killCountText'].update(kill_count_text)
        fps_text = '{:.2f}'.format(main.fps)
        window['fpsText'].update(fps_text)
    
    if (not cap is None):
        cap.release()
    window.close()


if __name__ == '__main__':
    draw()