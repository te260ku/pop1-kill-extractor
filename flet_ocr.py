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

target_video_path = None



def generate_image_panels(image_data):
    images = ft.GridView(
        height=100,
        width=400,
        child_aspect_ratio=1.0,
        horizontal=True,
    )

    for i in range(0, 10):
        images.controls.append(
            ft.Container(
                alignment=ft.alignment.center,
                image_src_base64=image_data, 
                # ink=True, 
                on_click=lambda e: print("Clickable with Ink clicked!")
            )
        )

    def button_clicked(e):
        images.scroll_to(delta=50)
    
        
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_BACK_IOS, on_click=button_clicked, data=0
    )
    forward_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_IOS, on_click=button_clicked, data=0
    )
    r = ft.Row(controls=[images])

    return r


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
            leading=ft.Icon(ft.icons.GRID_GOLDENRATIO_ROUNDED),
            leading_width=100,
            title=ft.Text("POP1 Kill Extractor",size=32, text_align="start"),
            center_title=False,
            toolbar_height=75,
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
    # page.appbar = appbar


    def button_clicked(e):
        page.add(ft.Text("Clicked!"))

    def app_close(e):
        print('Closed App')
        page.window_destroy()

    target_file = ft.Ref[ft.Text]()
    output_directory_path = ft.Ref[ft.Text]()
    processing_status = ft.Ref[ft.Text]()
    
    
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
        # width=108*2, 
        src_base64 = initial_image_base64, 
        )
    def play_preview_button_clicked(e):
        pass
    def stop_preview_button_clicked(e):
        pass
    play_preview_button = ft.IconButton(
        icon=ft.icons.PLAY_CIRCLE, 
        on_click=play_preview_button_clicked
        )
    stop_preview_button = ft.IconButton(
        icon=ft.icons.STOP_CIRCLE, 
        on_click=stop_preview_button_clicked
        )
    # preview_control_buttons = ft.Row(
    #     controls=[play_preview_button, stop_preview_button], 
    #     alignment=ft.MainAxisAlignment.CENTER
    #     )
    def items(count):
        items = []
        # for i in range(1, count + 1):
        items.append(
            ft.Container(
                content=play_preview_button, 
                alignment=ft.alignment.center,
                width=50,
                height=50,
                # bgcolor=ft.colors.AMBER_500,
            )
        )
        items.append(
            ft.Container(
                content=stop_preview_button, 
                alignment=ft.alignment.center,
                width=50,
                height=50,
                # bgcolor=ft.colors.AMBER_500,
            )
        )
        items.append(
            ft.Container(
                content=play_preview_button, 
                alignment=ft.alignment.center,
                width=50,
                height=50,
                # bgcolor=ft.colors.AMBER_500,
            )
        )
        return items

    def row_with_alignment():
        return ft.Column(
            [
                ft.Container(
                    content=ft.Row(items(3), alignment=ft.MainAxisAlignment.CENTER),
                ),
            ]
        )
    preview_control_buttons = row_with_alignment()
    '''************************************************************
    ** 
    ************************************************************'''



    


    def start_button_clicked(e):
        global target_video_path
        print(target_video_path)
        detected_kill_time = ocr.proc_new(target_video_path)
        print(detected_kill_time)
        print("===Finish===")


        # cap = cv2.VideoCapture(target_video_path)
        # while True:
        #     try:
        #         # フレームの読み込み
        #         ret, frame = cap.read()
        #         # フレームが読み込めなくなったら終了
        #         if not ret:
        #             break
                
        #         _, encoded = cv2.imencode(".jpg", frame)
        #         img_str = base64.b64encode(encoded).decode("ascii")

        #         preview_image.src_base64 = img_str
                
        #         page.update()
                
        #     except KeyboardInterrupt:
        #         break
        # cap.release()
        
    def stop_button_clicked(e):
        img = ocr.preview_thumbnails[0]
        _, encoded = cv2.imencode(".jpg", img)
        img_str = base64.b64encode(encoded).decode("ascii")
        panels[0].image_src_base64 = img_str
        page.update()
    
    def extract_button_clicked(e):
        pass

        

    # 動画を指定するダイアログ
    image_extensions = ["mp4"]
    def on_file_picked(e: ft.FilePickerResultEvent):
        global target_video_path
        if e.files:
            target_file.current.value = e.files[0].path
            target_video_path = e.files[0].path
            print(target_video_path)
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
    input_file_textbox = ft.TextField(ref=target_file, label="ファイル", read_only=True)

    
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
    output_file_textbox = ft.TextField(ref=output_directory_path, label="ディレクトリ", read_only=True)

    

    start_button = ft.ElevatedButton(text="開始", on_click=start_button_clicked)
    stop_button = ft.ElevatedButton(text="停止", on_click=stop_button_clicked)
    extract_button = ft.ElevatedButton(text="出力", on_click=extract_button_clicked)
    
    progress_bar = ft.ProgressBar(
        width=385, 
        color="pink", 
        bgcolor="#eeeeee"
    )
    progress_bar.value = 0.5
    # progress_value = float('{:.1f}'.format((main.frame_count/cap.get(cv2.CAP_PROP_FRAME_COUNT))*100))


    processing_status_text = ft.Text(ref=processing_status)

    


    

    


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

    copy_kill_time_log_button = ft.ElevatedButton(text="クリップボードにコピー", on_click=button_clicked)
    save_kill_time_log_button = ft.ElevatedButton(text="保存", on_click=button_clicked)


    def kill_time_offset_textbox_changed(e):
         return e.control.value
    
    def ign_textbox_changed(e):
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



    

    
    '''************************************************************
    ** 切り抜き動画パネル
    ************************************************************'''
    # image_panels = generate_image_panels(initial_image_base64)
    def on_image_panel_clicked(e):
        print(e.control.data)

        for p in panels:
            if p.data == e.control.data:
                p.border=ft.border.all(5, ft.colors.PINK_600)
            else:
                p.border=None
        page.update()

    images = ft.GridView(
        height=100,
        width=400,
        child_aspect_ratio=1.0,
        horizontal=True,
    )

    panels = []
    for i in range(0, 10):
        panels.append(
            ft.Container(
                alignment=ft.alignment.center,
                image_src_base64=initial_image_base64, 
                # ink=True, 
                on_click=on_image_panel_clicked, 
                data=i, 
                
            )
        )

    for p in panels:
        images.controls.append(p)
    
    image_panels = ft.Row(controls=[images])
    '''************************************************************
    ** 
    ************************************************************'''

    

    app_close_button = ft.ElevatedButton(text='アプリ終了', on_click=app_close)



    def on_copy_kill_time_button_clicked(e):
        page.dialog = copy_kill_time_dialog
        copy_kill_time_dialog.open = True
        page.update()
    def on_save_kill_time_button_clicked(e):
        page.dialog = save_kill_time_dialog
        save_kill_time_dialog.open = True
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

    copy_kill_time_button = ft.ElevatedButton(text='コピー', on_click=on_copy_kill_time_button_clicked)
    save_kill_time_button = ft.ElevatedButton(text='ファイルに保存', on_click=on_save_kill_time_button_clicked)





    

    


    home_column = ft.Column(controls=[     
        ft.Row(controls=[app_close_button, start_button, stop_button, extract_button, kill_time_offset_textbox, ign_textbox]), 
        ft.Row(controls=[input_file_textbox, select_input_file_button]), 
        ft.Row(controls=[output_file_textbox, select_output_file_button]), 
        ft.Row(controls=[processing_status_text]), 
        ft.Row(controls=[ft.Column([ft.Text("処理状況"), progress_bar, image_panels]), ft.Column([preview_image, preview_control_buttons])]), 
        # ft.Row(controls=[image_panels]), 
        ft.Row(controls=[ft.Column([ft.Text("ログ"), kill_time_log_container])]), 
        ft.Row(controls=[copy_kill_time_log_button, save_kill_time_log_button]), 
    ])
    processing_status.current.value = '待機中'
    # page.add(home_column)

    def get_normal_button_container(c):
        container = ft.Container(
            content=c,
            # margin=10,
            # padding=10,
            alignment=ft.alignment.center,
            # border_radius=10,
            
            )
        return container
    
    

    page.add(
        ft.Row(
            [
                get_normal_button_container(input_file_textbox),
                get_normal_button_container(select_input_file_button), 
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            width=page.width
        ),
        ft.Row(
            [
                get_normal_button_container(app_close_button), 
                get_normal_button_container(start_button), 
                get_normal_button_container(stop_button),
                get_normal_button_container(extract_button),
                get_normal_button_container(ign_textbox),
                get_normal_button_container(kill_time_offset_textbox),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            width=page.width
        ),
        ft.Divider(),

        ft.Row(
            [
                ft.Column(
                                [ 
                                    get_normal_button_container(processing_status_text), 
                                    get_normal_button_container(progress_bar), 
                                    get_normal_button_container(preview_image), 
                                    ft.Row([get_normal_button_container(play_preview_button), get_normal_button_container(stop_preview_button)]), 
                                    get_normal_button_container(image_panels),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER, 
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        
                    

                    ,
                    ft.VerticalDivider(), 

                    ft.Column(
                                [ 
                                    # get_normal_button_container(processing_status_text), 
                                    ft.Text("ログ", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        
                                    kill_time_log_container, 
                                    ft.Text("検出したキル", style=ft.TextThemeStyle.TITLE_MEDIUM),
                                    kill_time_table_container, 
                                    ft.Row([copy_kill_time_button, save_kill_time_button])
                                    
                                     
                                ],
                                alignment=ft.MainAxisAlignment.CENTER, 
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            )
            ], 
            expand=True, 
            alignment=ft.MainAxisAlignment.CENTER, 
        ), 
    

    )

    
    print(page.window_width)

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
    
    

    # for i in range(0, 101):
    #     progress_bar.value = i * 0.01
    #     time.sleep(0.1)
    #     page.update()
    
    
    

    


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