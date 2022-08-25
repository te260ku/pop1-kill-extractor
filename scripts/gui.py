import PySimpleGUI as sg
import cv2
import main
import numpy as np
import mimetypes

gui_font = 'Meiryo UI'

def draw():

    processing = False
    '''************************************************************
    ** レイアウトの定義
    ************************************************************'''
    sg.theme('LightBlue')

    file_select_button_comp = sg.FileBrowse('ファイルを選択', key='inputFilePath', font=(gui_font, 14))

    start_button_comp = sg.Button('開始', key='startButton', font=(gui_font, 14))
    stop_button_comp = sg.Button('停止', key='stopButton', font=(gui_font, 14))
    exit_button_comp = sg.Button('アプリ終了', key='exitButton', font=(gui_font, 14))
    preview_checkbox_comp = sg.Checkbox('プレビュー表示', False, key='previewCheckbox', font=(gui_font, 14))
    processing_status_text_comp = sg.Text('Waiting...', key='processingStatusText', font=(gui_font, 14), expand_x=True, background_color='#37B507')

    preview_image_comp = sg.Image(filename='../images/initial_image.png', key='previewImage')

    kill_count_text_comp = sg.Text('', key='killCountText', font=(gui_font, 14), text_color='#000', background_color='#37B507', size=(10,1))
    fps_text_comp = sg.Text('', key='fpsText', font=(gui_font, 14), text_color='#000', background_color='#37B507', size=(10, 1))

    kill_time_log_comp = sg.Output(size=(28,15))
    copy_button_comp = sg.Button('コピー', key='copyButton', font=(gui_font, 14))
    save_button_comp = sg.Button('保存', key='saveButton', font=(gui_font, 14))

    progress_text_comp = sg.Text('0%', key='progressText', font=(gui_font, 14), size=(5,1))
    progress_bar_comp = sg.ProgressBar(100, orientation='h', size=(36.5,20), key='progressBar')


    layout_1 = [  
        [sg.Text('ファイル', font=(gui_font, 14)), sg.Input(font=(gui_font, 14)), file_select_button_comp], 
        [preview_checkbox_comp],  
        [start_button_comp, stop_button_comp, exit_button_comp], 
        [processing_status_text_comp], 
    ]

    layout_2 = [
        [preview_image_comp], 
        [progress_text_comp, progress_bar_comp], 
    ]

    layout_3 = [
        [kill_count_text_comp], 
        [fps_text_comp], 
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


    main.start_proc()


    while True:
        # timeout: 小さいほど滑らか
        event, values = window.read(timeout=100)

        
        
        if event == 'exitButton' or event == sg.WIN_CLOSED:
            break

        if event == 'startButton':
            if (processing == False):
                # cap = cv2.VideoCapture('../videos/test_1.mp4')

                file_path = values['inputFilePath']
                if (file_path == ''):
                    continue
                mime = mimetypes.guess_type(file_path)
                if (mime[0].startswith('video/')):
                    cap = cv2.VideoCapture(file_path)
                    if (cap.isOpened() == False):
                        continue
                    window['processingStatusText'].update('Processing...')
                    processing = True
                else:
                    sg.popup('ファイル形式が無効です', title='Error')

                
        elif event == 'stopButton':
            processing = False
            window['processingStatusText'].update('Waiting...')
        elif event == 'copyButton':
            main.copy_kill_time()
        elif event == 'saveButton':
            value = sg.popup_get_file('', save_as=True, title='保存先を選択')
            if value is not None:
                main.save_kill_time(value)
            

        if (processing == True):
            ret, frame = cap.read()
            if not ret:
                window['progressBar'].update(1)
                continue

            current_sec = cap.get(cv2.CAP_PROP_POS_MSEC)

            progress_value = float('{:.1f}'.format((main.frame_count/cap.get(cv2.CAP_PROP_FRAME_COUNT))*100))
            window['progressBar'].update(progress_value)
            window['progressText'].update('{}%'.format(str(progress_value)))
            
            frame = main.proc(frame, current_sec=current_sec)
            frame = cv2.resize(frame, dsize=None, fx=0.2, fy=0.2)
            
            if values['previewCheckbox']:
                bytes = cv2.imencode('.png', frame)[1].tobytes()
                window['previewImage'].update(data=bytes)
            else:
                tmp = np.zeros_like(frame)
                bytes = cv2.imencode('.png', tmp)[1].tobytes()
                window['previewImage'].update(data=bytes)


        kill_count_text = 'キル数: {}'.format(main.detection_count)
        window['killCountText'].update(kill_count_text)

        fps_text = 'FPS: {:.2f}'.format(main.fps)
        window['fpsText'].update(fps_text)
        

    cap.release()
    window.close()


if __name__ == '__main__':
    draw()