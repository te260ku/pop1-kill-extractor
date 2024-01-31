import flet as ft
from pathlib import Path
import time
import base64
from scripts import ocr
from scripts import main
import pytesseract
from PIL import Image
import cv2
import numpy as np
import pyperclip
import csv
from moviepy.editor import *
from tqdm import tqdm
import asyncio
import math
import threading

input_video_path = ""
detected_kill_times = []



def main(page):
    set_page(page)


    settings_view = ft.Text("settings")
    info_view = ft.Text("info")


    def home_button_clicked(e):
        page.remove(settings_view)
        page.remove(info_view)
        page.add(home_column)
    def settings_button_clicked(e):
        page.dialog = settings_dialog
        settings_dialog.open = True
        page.update()
    def info_button_clicked(e):
        page.remove(home_column)
        page.remove(settings_view)
        page.add(info_view)

    appbar_items = [
            ft.PopupMenuItem(text="Home", on_click=home_button_clicked),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(text="Settings", on_click=settings_button_clicked), 
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(text="Info", on_click=info_button_clicked)
        ]
    


    appbar = ft.AppBar(
            # leading=ft.Icon(ft.icons.GRID_GOLDENRATIO_ROUNDED),
            leading_width=100,
            title=ft.Text("POP1 Kill Extractor",size=22, text_align="start"),
            center_title=False,
            toolbar_height=55,
            bgcolor=ft.colors.LIGHT_BLUE_ACCENT_700,
            actions=[
                ft.Container(
                    content=ft.PopupMenuButton(
                        items=appbar_items
                    ),
                    margin=ft.margin.only(left=50, right=25), 
                    
                )
            ],
        )
    page.appbar = appbar

    progress_bar = ft.ProgressBar(
        width=300, 
        color="pink", 
        bgcolor="#eeeeee"
    )


    def button_clicked(e):
        page.add(ft.Text("Clicked!"))

    def app_close(e):
        print('Closed App')
        page.window_destroy()

    target_file = ft.Ref[ft.Text]()
    output_directory_path = ft.Ref[ft.Text]()
    processing_status = ft.Ref[ft.Text]()
    progress_value = ft.Ref[ft.Text]()

    # progress_bar = ft.ProgressBar(
    #     width=385, 
    #     color="pink", 
    #     bgcolor="#eeeeee"
    # )
    progress_bar.value = 0


    processing_status_text = ft.Text(ref=processing_status)

    progress_value_text = ft.Text(ref=progress_value)

    

    
    
    output_folder = ft.Ref[ft.Text]()
    # page.add(target_file)
    

    initial_image_path = "./images/initial_image.png"
    
    with open(initial_image_path, 'rb') as f:
        initial_image_base64 = base64.b64encode(f.read()).decode('utf-8')






    '''************************************************************
    ** プレビューエリア
    ************************************************************'''
    preview_image = ft.Image(
        fit=ft.ImageFit.FIT_WIDTH, 
        # height=192/2,
        width=400, 
        src_base64 = initial_image_base64, 
        repeat=ft.ImageRepeat.NO_REPEAT,
        )
    image_panels_container = ft.Container()
    def play_preview_button_clicked(e):
        pass
    def stop_preview_button_clicked(e):
        pass
    play_preview_button = ft.IconButton(
        icon=ft.icons.DELETE, 
        on_click=play_preview_button_clicked
        )
    stop_preview_button = ft.IconButton(
        icon=ft.icons.STOP_CIRCLE, 
        on_click=stop_preview_button_clicked
        )

    '''************************************************************
    ** 
    ************************************************************'''



    '''************************************************************
    ** モーダル
    ************************************************************'''
    alert_modal_text = ft.Text("")
    def show_alert_modal():
        page.dialog = alert_dialog
        alert_dialog.open = True
        page.update()
    def close_alert_dialog(e):
        alert_dialog.open = False
        page.update()
    alert_dialog = ft.AlertDialog(
        modal=True,
        content=alert_modal_text,
        title=ft.Text("エラー"), 
        actions=[
            ft.TextButton("閉じる", on_click=close_alert_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )
    '''************************************************************
    ** 
    ************************************************************'''

    


    def is_empty_str(val):
        return len(val) == 0
    

    def convert_cv_to_base64(img):
        _, encoded = cv2.imencode(".jpg", img)
        img_str = base64.b64encode(encoded).decode("ascii")
        return img_str
    

    def set_p_value():
        while ocr.finished is False:
            progress_bar.value = ocr.progress_value
            progress_value.current.value = f"{round(ocr.progress_value*100, 2)}%"
            page.update()
            
        progress_bar.value = 1.0
        progress_value.current.value = f"{round(ocr.progress_value*100, 2)}%"
        page.update()
        print("progress complete")



    '''************************************************************
    ** 切り抜き動画パネル
    ************************************************************'''
    # image_panels = generate_image_panels(initial_image_base64)
    def on_image_panel_clicked(e):
        # print(e.control.data)
        selected_preview_image_index = e.control.data
        # print(ocr.detected_kill_times)

        for p in image_panels.controls:
            if p.data == selected_preview_image_index:
                p.border=ft.border.all(5, ft.colors.PINK_600)
                if (len(ocr.preview_thumbnails) > selected_preview_image_index):
                    preview_image.src_base64 = convert_cv_to_base64(ocr.preview_thumbnails[selected_preview_image_index])
            else:
                p.border=None
        page.update()

    image_panels = ft.Row(
        # height=90,
        width=300,
        # child_aspect_ratio=1.0,
        # horizontal=True,
        scroll=ft.ScrollMode.HIDDEN, 
        alignment=ft.alignment.center, 
    )

    # panels = []
    # for i in range(0, 10):
    #     panels.append(
    #         ft.Container(
    #             content=ft.Column(
    #                 [
    #                     ft.Image(
    #                         # src=f"https://picsum.photos/150/150?{i}",
    #                         src_base64=initial_image_base64, 
    #                         # fit=ft.ImageFit.FIT_WIDTH,
    #                         width=70, 
    #                         # repeat=ft.ImageRepeat.NO_REPEAT,
    #                         # border_radius=ft.border_radius.all(10),
    #                     ), 
    #                     ft.Text("00:00")
    #                 ], 
    #                 horizontal_alignment=ft.CrossAxisAlignment.CENTER
    #             ), 
    #         ) 
    #     )
    
    # for i in range(0, 10):
    #     c = ft.Container(
    #         content=panels[i], 
    #         on_click=on_image_panel_clicked, 
    #         data=i, 
    #         alignment=ft.alignment.center, 
    #         # width=140,
    #         # padding=ft.padding.symmetric(0, 20), 
    #         # margin=ft.margin.symmetric(0, 20), 
    #         )
    #     image_panels.controls.append(c)
    


    forward_preview_image_list_button = ft.IconButton(
        icon=ft.icons.KEYBOARD_ARROW_LEFT, 
        on_click=lambda _: image_panels.scroll_to(delta=-100, duration=500), 
        )
    back_preview_image_list_button = ft.IconButton(
        icon=ft.icons.KEYBOARD_ARROW_RIGHT, 
        on_click=lambda _: image_panels.scroll_to(delta=100, duration=500), 
        )
    
    # image_panels_container = None
    image_panels_container_processed = ft.Container(
        content=image_panels, 
        border=ft.border.all(1, ft.colors.WHITE), 
        # padding=ft.padding.symmetric(0, 20),
        # margin=ft.margin.symmetric(0, 20),
    )
    image_panels_container_dummy = ft.Container(
        # content=image_panels, 
        width=300, 
        height=80, 
        border=ft.border.all(1, ft.colors.WHITE), 
        # padding=ft.padding.symmetric(0, 20),
        # margin=ft.margin.symmetric(0, 20),
        disabled=True
    )

    image_panels_container = image_panels_container_dummy



    
    '''************************************************************
    ** 
    ************************************************************'''
    




    '''************************************************************
    ** スタートボタン
    ************************************************************'''
    def start_button_clicked(e):
        global input_video_path
        global detected_kill_times

    

        print(input_video_path)
        info_is_incomplete = False
        alert_modal_text_value = ""
        if (is_empty_str(ign_textbox.value)):
            info_is_incomplete = True
            alert_modal_text_value += "IGNを入力してください\n"
        if (is_empty_str(input_video_path)):
            info_is_incomplete = True
            alert_modal_text_value += "動画を選択してください\n"
        if (info_is_incomplete):
            alert_modal_text.value = alert_modal_text_value
            show_alert_modal()
            return
        print(ign_textbox.value)

        
        

        thread1 = threading.Thread(target=set_p_value)
        thread1.start()

        detected_kill_times = ocr.proc_new(video_path=input_video_path, ign=ign_textbox.value)

        
        print(detected_kill_times)
        print("===Finish===")
        

        # show_preview_images()

        preview_thumbnails = ocr.preview_thumbnails

        
        panels = []

        
        for i in range(0, len(detected_kill_times)):
            thumbnail = preview_thumbnails[i]
            panels.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Image(
                                # src=f"https://picsum.photos/150/150?{i}",
                                src_base64=convert_cv_to_base64(thumbnail), 
                                # fit=ft.ImageFit.FIT_WIDTH,
                                width=70, 
                                # repeat=ft.ImageRepeat.NO_REPEAT,
                                # border_radius=ft.border_radius.all(10),
                            ), 
                            ft.Text("00:00")
                        ], 
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ), 
                ) 
            )
        
        for i in range(0, len(detected_kill_times)):
            c = ft.Container(
                content=panels[i], 
                on_click=on_image_panel_clicked, 
                data=i, 
                alignment=ft.alignment.center, 
                # width=140,
                # padding=ft.padding.symmetric(0, 20), 
                # margin=ft.margin.symmetric(0, 20), 
                )
            image_panels.controls.append(c)
        

        image_panels_container_processed.content = image_panels
        image_panels_container.content = image_panels_container_processed
        image_panels_container.disabled = False
        page.update()
        update_kill_time_log()


    def update_kill_time_log():
        pass


    def stop_button_clicked(e):
        ocr.finished = True


    def show_preview_images():
        preview_thumbnails = ocr.preview_thumbnails
        count = 0
        for thumbnail in preview_thumbnails:
            img_str = convert_cv_to_base64(thumbnail)
            panels[count].src_base64 = img_str
            count += 1
        page.update()
    
    def extract_button_clicked(e):
        if (is_empty_str(output_video_file_name_textbox.value)):
            # 出力ファイル名が入力されていない場合は処理を実行しない
            alert_modal_text_value = "出力ファイル名を入力してください\n"
            alert_modal_text.value = alert_modal_text_value
            show_alert_modal()
            return
        
        ocr.create_video(input_video_file=input_video_path, output_video_path=output_directory_path.current.value)
        # export_video_result = "エクスポートが完了しました" if result else "エクスポートに失敗しました"
        # print(export_video_result)
    '''************************************************************
    ** 
    ************************************************************'''
    
        




    '''************************************************************
    ** 動画を指定するダイアログ
    ************************************************************'''
    image_extensions = ["mp4"]
    def on_file_picked(e: ft.FilePickerResultEvent):
        global input_video_path
        if e.files:
            target_file.current.value = e.files[0].path
            input_video_path = e.files[0].path
            print(input_video_path)
            page.update()
    input_file_selector = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(input_file_selector)
    def show_file_picker(_: ft.ControlEvent):
        input_file_selector.pick_files(
            allow_multiple=False,
            file_type="custom",
            allowed_extensions=image_extensions
        )
    select_input_file_button = ft.ElevatedButton(
        "ファイルを選択", 
        on_click=show_file_picker
        )
    input_file_textbox = ft.TextField(ref=target_file, label="ファイル", read_only=True, width=200)
    '''************************************************************
    ** 
    ************************************************************'''
    

    

    '''************************************************************
    ** 出力先のディレクトリを指定するダイアログ
    ************************************************************'''
    def get_directory_result(e: ft.FilePickerResultEvent):
        if e.path:
            output_directory_path.current.value = e.path
            page.update()

    output_directory_selector = ft.FilePicker(on_result=get_directory_result)
    page.overlay.append(output_directory_selector)
    select_output_file_button = ft.ElevatedButton(
        "保存場所を選択",
        # icon=ft.icons.FOLDER_OPEN,
        on_click=lambda _: output_directory_selector.get_directory_path(),
        )
    output_file_textbox = ft.TextField(ref=output_directory_path, label="ディレクトリ", read_only=True, width=200,)
    '''************************************************************
    ** 
    ************************************************************'''
    

    


    '''************************************************************
    ** ログ
    ************************************************************'''
    kill_time_log = ft.Column(
        spacing=5,
        height=150,
        width=300,
        scroll=ft.ScrollMode.ALWAYS,
        on_scroll_interval=0,
    )
    kill_time_log_container = ft.Container(
        content=kill_time_log, 
        border=ft.border.all(1, ft.colors.WHITE), 
        # border_radius=ft.border_radius.all(5)
    )
    # for i in range(0, 50):
    #     kill_time_log.controls.append(ft.Text(f"Text line {i}", key=str(i), selectable=True))
    kill_time_log.controls.append(ft.Text("アプリを起動"))


    kill_time_table = ft.Column(
        spacing=5,
        height=150,
        width=300,
        scroll=ft.ScrollMode.ALWAYS,
        on_scroll_interval=0,
    )
    kill_time_table_container = ft.Container(
        content=kill_time_table, 
        border=ft.border.all(1, ft.colors.WHITE), 
        # border_radius=ft.border_radius.all(5), 
    )
    for i in range(0, 10):
        kill_time_table.controls.append(ft.Text(f"Text line {i}", key=str(i), selectable=True))
    '''************************************************************
    ** 
    ************************************************************'''



    # copy_kill_time_log_button = ft.ElevatedButton(text="クリップボードにコピー", on_click=button_clicked)
    # save_kill_time_log_button = ft.ElevatedButton(text="保存", on_click=button_clicked)


    def kill_time_offset_textbox_changed(e):
         return e.control.value
    
    def ign_textbox_changed(e):
         return e.control.value
    
    def output_video_file_name_textbox_changed(e):
         return e.control.value
        

    kill_time_offset_textbox = ft.TextField(
        label="オフセット",
        width=150, 
        on_change=kill_time_offset_textbox_changed,
    )

    ign_textbox = ft.TextField(
        label="IGN",
        width=150, 
        on_change=kill_time_offset_textbox_changed,
    )

    output_video_file_name_textbox = ft.TextField(
        label="出力ファイル名",
        width=150, 
        on_change=kill_time_offset_textbox_changed,
    )



    

    
    


    

    

    app_close_button = ft.ElevatedButton(text='アプリ終了', on_click=app_close)


    
    def on_copy_kill_time_button_clicked(e):
        global detected_kill_times
        page.set_clipboard(str(detected_kill_times))
        page.dialog = copy_kill_time_dialog
        copy_kill_time_dialog.open = True
        page.update()
    def close_copy_kill_time_dialog(e):
        copy_kill_time_dialog.open = False
        page.update()
    copy_kill_time_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Text("クリップボードにコピーしました"),
        actions=[
            ft.TextButton("閉じる", on_click=close_copy_kill_time_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )
    copy_kill_time_button = ft.ElevatedButton(text='コピー', on_click=on_copy_kill_time_button_clicked)

    
    def on_save_kill_time_button_clicked(e):
        page.dialog = save_kill_time_dialog
        save_kill_time_dialog.open = True
        page.update()
    def close_save_kill_time_dialog(e):
        save_kill_time_dialog.open = False
        page.update()
    save_kill_time_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Text("保存しました"),
        actions=[
            ft.TextButton("閉じる", on_click=close_save_kill_time_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )
    save_kill_time_button = ft.ElevatedButton(text='ファイルに保存', on_click=on_save_kill_time_button_clicked)

    


    start_button = ft.ElevatedButton(text="開始", on_click=start_button_clicked)
    stop_button = ft.ElevatedButton(text="停止", on_click=stop_button_clicked)
    extract_button = ft.ElevatedButton(text="出力", on_click=extract_button_clicked)


    

    

    processing_status.current.value = '待機中'
    progress_value.current.value = f"{round(ocr.progress_value*100, 2)}%"


    def get_normal_button_container(c):
        container = ft.Container(
            content=c,
            # margin=10,
            # padding=10,
            alignment=ft.alignment.center,
            # border_radius=10,
            )
        return container
    
    def get_container(c, w=None, h=None, m=None, p=None):
        if (w == None):
            w = c.width
        if (h == None):
            h = c.height
        # if (m == None):
        #     m = c.margin
        # if (p == None):
        #     p = c.padding
        container = ft.Container(
            content=c,
            margin=m,
            padding=p,
            alignment=ft.alignment.center,
            # border_radius=10,
            border=ft.border.all(1, ft.colors.WHITE), 
            width=w, 
            height=h, 
            )
        return container
    
    preview_image_control_buttons = ft.Row(
        [get_normal_button_container(play_preview_button), 
        #  get_normal_button_container(stop_preview_button), 
         ], 
        vertical_alignment=ft.CrossAxisAlignment.CENTER, 
        alignment=ft.MainAxisAlignment.CENTER
        )
    
    preview_image_info_text = ft.Text("preview")


    
    page.add(
        # ft.Row(
        #     [
        #         get_normal_button_container(input_file_textbox),
        #         get_normal_button_container(select_input_file_button), 
        #         get_normal_button_container(output_file_textbox), 
        #         get_normal_button_container(select_output_file_button), 
                
        #     ],
        #     alignment=ft.MainAxisAlignment.CENTER,
        # ),
        # ft.Row(
        #     controls=
        #     [
                
        #         get_normal_button_container(app_close_button), 
        #         get_normal_button_container(start_button), 
        #         get_normal_button_container(stop_button),
        #         get_normal_button_container(extract_button),
        #         get_normal_button_container(ign_textbox),
        #         get_normal_button_container(kill_time_offset_textbox),
        #         get_normal_button_container(output_video_file_name_textbox),
        #     ],
        #     alignment=ft.MainAxisAlignment.CENTER,
        #     # width=page.width
        # ),
        # ft.Divider(),


        

    # ft.ElevatedButton("update", on_click=set_progress_bar_value), 
    # ft.ElevatedButton("value change", on_click=button_clicked2), 

        ft.Row(
            [
                ft.Column(

                                [ 
                                    # get_normal_button_container(processing_status_text), 
                                    # get_normal_button_container(progress_bar), 
                                    
                                    ft.Row([
                                            

                                            get_container(
                                                ft.Column([
                                                    ft.Row([
                                                        processing_status_text, 
                                                        progress_value_text, 
                                                    ]), 
                                                    
                                                    progress_bar, 
                                                    preview_image_info_text, 
                                                    get_normal_button_container(preview_image), 
                                                    preview_image_control_buttons, 
                                                    ft.Row(
                                                        [
                                                            forward_preview_image_list_button, 
                                                            image_panels_container, 
                                                            back_preview_image_list_button
                                                        ]
                                                    )
                                                    
                                                    ], 
                                            # alignment=ft.MainAxisAlignment.CENTER, 
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                                            # spacing=0, 
                                            ), h=500, p=10
                                            ), 
                                        
                                            # get_container(
                                            #     ft.Column(
                                            #         [
                                            #         forward_preview_image_list_button, 
                                            #         image_panels_container, 
                                            #         back_preview_image_list_button
                                            #         ], 
                                            #         alignment=ft.MainAxisAlignment.CENTER, 
                                            #         horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                                            #         # spacing=0,
                                            #     ), 
                                            #     h=260
                                            # ), 
                                
                                
                                            
                                            
                                            ], 
                                            alignment=ft.MainAxisAlignment.CENTER, 
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                                            ), 
                                     
                                    # ft.Row([get_normal_button_container(play_preview_button), get_normal_button_container(stop_preview_button)]), 
                                    
                                ],
                                # alignment=ft.MainAxisAlignment.CENTER, 
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        
                    

                    ,
                    ft.VerticalDivider(), 

                    get_container(ft.Row([ft.Column(

                        
                                [ 
                                    ft.Row([
                                        get_normal_button_container(input_file_textbox),
                                        get_normal_button_container(select_input_file_button), 
                                    ]), 

                                    
                                    get_normal_button_container(ign_textbox),

                                    ft.Row([
                                        get_normal_button_container(start_button), 
                                        get_normal_button_container(stop_button),
                                    ]), 
                                    



                                    ft.Row([
                                        get_normal_button_container(output_file_textbox), 
                                        get_normal_button_container(select_output_file_button), 
                                    ]), 
                
                                    
                                    get_normal_button_container(output_video_file_name_textbox),
                                    get_normal_button_container(kill_time_offset_textbox),
                                    
                                    
                
                
                                    get_normal_button_container(extract_button),
                                    # get_normal_button_container(processing_status_text), 
                                    # ft.Text("ログ", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        
                                    # kill_time_log_container, 
                                    # ft.Text("検出したキル", style=ft.TextThemeStyle.TITLE_MEDIUM),
                                    # kill_time_table_container, 
                                    # kill_time_log_table, 
                                    ft.Row([copy_kill_time_button, save_kill_time_button])
                                    
                                     
                                ],
                                # alignment=ft.MainAxisAlignment.CENTER, 
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )]), 
                
                # h=500, 
                p=10
                
                
                )
                    

                    
                
            ], 
            expand=True, 
            alignment=ft.MainAxisAlignment.CENTER, 
        ), 
    

    )


    page.window_width = 1000
    page.update()



    # page.add()


    def close_settings_dialog(e):
        settings_dialog.open = False
        page.update()


    user_name = ft.TextField(label="User name")
    password = ft.TextField(label="Password")
    settings_dialog = ft.AlertDialog(
        title=ft.Text("Settings"),
        content=ft.Column([
            user_name,
            password,
            ft.ElevatedButton(text="Login", on_click=close_settings_dialog),
        ], 
        tight=True, 
        width=500,
        height=300,
        ),
    )
    




def set_page(page: ft.Page):
    '''
    画面全体の初期設定
    '''

    page.title = "POP1 Kill Extractor"

    # page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    

    page.window_width = 1000
    # page.window_height = 200
    # page.window_left = 100
    # page.window_top = 400

    page.update()




if __name__ == '__main__':
    ft.app(target = main)