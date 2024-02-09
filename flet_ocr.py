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
from enum import *

class ViewType(Enum):
    MAIN = auto()
    SETTING = auto()
    INFO = auto()

input_video_path = ""
detected_kill_times = []
current_view = ViewType.MAIN
selected_preview_image_index = 0


def main(page):
    set_page(page)

    
    progress_bar = ft.ProgressBar(
        width=300, 
        color="pink", 
        bgcolor="#eeeeee", 
    )
    progress_bar.value = 0

    

    target_file = ft.Ref[ft.Text]()
    output_directory_path = ft.Ref[ft.Text]()

    processing_status = ft.Ref[ft.Text]()
    processing_status_text = ft.Text(ref=processing_status)

    progress_value = ft.Ref[ft.Text]()
    progress_value_text = ft.Text(ref=progress_value)

    processing_status.current.value = '待機中'
    progress_value.current.value = f"{round(ocr.progress_value*100, 2)}%"
    
    initial_image_path = "./images/initial_image_16-9.png"
    with open(initial_image_path, 'rb') as f:
        initial_image_base64 = base64.b64encode(f.read()).decode('utf-8')

    

    def get_normal_button_container(c):
        container = ft.Container(
            content=c,
            # margin=10,
            # padding=10,
            # alignment=ft.alignment.center,
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
            # alignment=ft.alignment.center,
            # border_radius=10,
            border=ft.border.all(1, ft.colors.WHITE), 
            width=w, 
            height=h, 
            )
        return container


    def app_close(e):
        print('Closed App')
        page.window_destroy()



    '''************************************************************
    ** プレビューエリア
    ************************************************************'''
    preview_image = ft.Image(
        fit=ft.ImageFit.FIT_WIDTH, 
        height=1920*0.12,
        # width=400, 
        src_base64 = initial_image_base64, 
        repeat=ft.ImageRepeat.NO_REPEAT,
        
        )
    image_panels_container = ft.Container()

    def remove_detected_kill_times(idx):
        global detected_kill_times
        del detected_kill_times[idx]

    def erase_clip_button_clicked(e):
        global selected_preview_image_index
        remove_detected_kill_times(selected_preview_image_index)
        kill_time_table.controls[selected_preview_image_index].opacity = 0.5
        image_panels.controls[selected_preview_image_index].opacity = 0.5
        image_panels.controls[selected_preview_image_index].disabled = True
        # update_image_panels_id()
        page.update()

    play_preview_button = ft.IconButton(
        icon=ft.icons.DELETE, 
        on_click=erase_clip_button_clicked
        )
    
    preview_image_info_text = ft.Text("プレビュー")

    preview_image_control_buttons = ft.Row(
        [
            get_normal_button_container(play_preview_button), 
        #  get_normal_button_container(stop_preview_button), 
         ], 
        vertical_alignment=ft.CrossAxisAlignment.CENTER, 
        alignment=ft.MainAxisAlignment.CENTER
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
    
    def seconds_to_hms(seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))
    

    def set_p_value():
        prev_progress_value = 0
        current_progress_value = 0
        progress_value_update_threshold = 0.05
        while ocr.finished is False:
            current_progress_value = ocr.progress_value

            if (current_progress_value - prev_progress_value > progress_value_update_threshold):
                

                prev_progress_value = current_progress_value
                progress_bar.value = current_progress_value
                progress_value.current.value = f"{round(current_progress_value*100, 2)}%"
                page.update()
            
        progress_bar.value = 1.0
        progress_value.current.value = f"{round(ocr.progress_value*100, 2)}%"
        page.update()
        print("progress complete")



    '''************************************************************
    ** クリップエリア
    ************************************************************'''
    def on_image_panel_clicked(e):
        global selected_preview_image_index
        selected_preview_image_index = e.control.data

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


    forward_preview_image_list_button = ft.IconButton(
        icon=ft.icons.KEYBOARD_ARROW_LEFT, 
        on_click=lambda _: image_panels.scroll_to(delta=-100, duration=500), 
        )
    back_preview_image_list_button = ft.IconButton(
        icon=ft.icons.KEYBOARD_ARROW_RIGHT, 
        on_click=lambda _: image_panels.scroll_to(delta=100, duration=500), 
        )
    
    image_panels_container_processed = ft.Container(
        content=image_panels, 
        border=ft.border.all(1, ft.colors.WHITE), 
    )
    image_panels_container_dummy = ft.Container(
        # content=image_panels, 
        width=300, 
        height=120, 
        border=ft.border.all(1, ft.colors.WHITE), 
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

        detected_kill_times = ocr.proc(video_path=input_video_path, ign=ign_textbox.value)

        
        print(detected_kill_times)
        print("===Finish===")
        

        show_preview_images(detected_kill_times)

    
        update_kill_time_log(detected_kill_times)
        page.update()



    def show_preview_images(kill_times):
        preview_thumbnails = ocr.preview_thumbnails

        
        panels = []

        
        for i in range(0, len(kill_times)):
            thumbnail = preview_thumbnails[i]
            formatted_kill_time = seconds_to_hms(kill_times[i])
            panels.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(str(i+1)),
                            ft.Image(
                                # src=f"https://picsum.photos/150/150?{i}",
                                src_base64=convert_cv_to_base64(thumbnail), 
                                # fit=ft.ImageFit.FIT_WIDTH,
                                width=70, 
                                # repeat=ft.ImageRepeat.NO_REPEAT,
                                # border_radius=ft.border_radius.all(10),
                            ), 
                            ft.Text(formatted_kill_time)
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
    '''************************************************************
    ** 
    ************************************************************'''



    def update_kill_time_log(kill_times):
        kill_time_table.controls.clear()
        for kill_time in kill_times:
            val = seconds_to_hms(kill_time)
            kill_time_table.controls.append(ft.Text(val, selectable=True))
        page.update()





    def stop_button_clicked(e):
        ocr.finished = True






    
    
    '''************************************************************
    ** 出力ボタン
    ************************************************************'''
    def extract_button_clicked(e):
        global detected_kill_times
        print(enable_separeted_output_checkbox.value)
        alert_modal_text_value = ""
        error = False
        if (is_empty_str(output_video_file_name_textbox.value)):
            # 出力ファイル名が入力されていない場合は処理を実行しない
            alert_modal_text_value += "出力ファイル名を入力してください\n"
            error = True
        if (is_empty_str(output_video_file_name_textbox.value)):
            # 出力ディレクトリが指定されていない場合は処理を実行しない
            alert_modal_text_value += "保存するフォルダを選択してください\n"
            error = True
        if (error):
            alert_modal_text.value = alert_modal_text_value
            show_alert_modal()
            return
        
        
        ocr.create_video(input_video_file=input_video_path, output_video_path=output_directory_path.current.value, separated=enable_separeted_output_checkbox.value, kill_times=detected_kill_times)
        # export_video_result = "エクスポートが完了しました" if result else "エクスポートに失敗しました"
        # print(export_video_result)
    '''************************************************************
    ** 
    ************************************************************'''
    
        




    '''************************************************************
    ** ファイルの入出力先を指定するダイアログ
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
    select_input_file_button = ft.IconButton(
        icon=ft.icons.VIDEO_FILE,
        on_click=show_file_picker
        )
    input_file_textbox = ft.TextField(
        ref=target_file, 
        label="ファイル", 
        read_only=True, 
        width=150, 
        # height=40,
        text_size=15,
        )

    
    def get_directory_result(e: ft.FilePickerResultEvent):
        if e.path:
            output_directory_path.current.value = e.path
            page.update()

    output_directory_selector = ft.FilePicker(on_result=get_directory_result)
    page.overlay.append(output_directory_selector)
    select_output_file_button = ft.IconButton(
        icon=ft.icons.FOLDER_OPEN,
        
        on_click=lambda _: output_directory_selector.get_directory_path(),
        )
    output_file_textbox = ft.TextField(
        ref=output_directory_path, 
        label="ディレクトリ", 
        read_only=True, 
        width=150, 
        # height=40,
        text_size=15,
        )
    '''************************************************************
    ** 
    ************************************************************'''
    

    


    '''************************************************************
    ** キルタイムリスト
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
        # height=150,
        # width=300,
        scroll=ft.ScrollMode.ALWAYS,
        on_scroll_interval=0,
    )
    kill_time_table_container = ft.Container(
        content=kill_time_table, 
        border=ft.border.all(1, ft.colors.WHITE), 
        width=100,
        height=320,
        # border_radius=ft.border_radius.all(5), 
    )
    # for i in range(0, 20):
    #     kill_time_table.controls.append(ft.Text("00:00", selectable=True))


    def on_copy_kill_time_button_clicked(e):
        global detected_kill_times
        hms_formatted_kill_times = []
        for kill_time in detected_kill_times:
            hms_formatted_kill_times.append(seconds_to_hms(kill_time))
        formatted_str = ','.join(hms_formatted_kill_times)
        page.set_clipboard(formatted_str)
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
    copy_kill_time_button = ft.IconButton(
        on_click=on_copy_kill_time_button_clicked, 
        icon=ft.icons.COPY,
        # icon_color="blue400",
        icon_size=20,
        tooltip="コピー",
        )
    
    def get_csv_directory_result(e: ft.FilePickerResultEvent):
        if e.path:
            print(e.path)
            file_path = e.path + ".csv"
            save_kill_time_to_csv(file_path)
 

    csv_output_directory_selector = ft.FilePicker(on_result=get_csv_directory_result)
    page.overlay.append(csv_output_directory_selector)

    
    def save_kill_time_to_csv(path):
        global detected_kill_times
        hms_formatted_kill_times = []
        detected_kill_times = [3, 17]
        for kill_time in detected_kill_times:
            hms_formatted_kill_times.append(seconds_to_hms(kill_time))

        with open(path, 'w', newline="") as f:
            writer = csv.writer(f)
            for item in hms_formatted_kill_times:
                writer.writerow([item])

        page.dialog = save_kill_time_dialog
        save_kill_time_dialog.open = True
        page.update()

    
    def on_save_kill_time_button_clicked(e):
        csv_output_directory_selector.save_file(
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["csv"]
        )

        

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
    save_kill_time_button = ft.IconButton(
        on_click=on_save_kill_time_button_clicked, 
        icon=ft.icons.SAVE,
        # icon_color="blue400",
        icon_size=20,
        tooltip="ファイルに保存",
        )
    '''************************************************************
    ** 
    ************************************************************'''




    
        


    '''************************************************************
    ** 設定エリア
    ************************************************************'''
    kill_time_offset_textbox = ft.TextField(
        label="オフセット",
        width=150, 
        height=40,
        text_size=15,
    )

    kill_time_interval_textbox = ft.TextField(
        label="インターバル",
        width=150, 
        height=40,
        text_size=15,
    )

    ign_textbox = ft.TextField(
        label="IGN",
        width=150, 
        height=40,
        text_size=15,
    )

    output_video_file_name_textbox = ft.TextField(
        label="出力ファイル名",
        width=150, 
        height=40,
        text_size=15,
    )
        

    enable_separeted_output_checkbox = ft.Checkbox(label="個別で出力")
    '''************************************************************
    ** 
    ************************************************************'''


    

    '''************************************************************
    ** ページ全体
    ************************************************************'''
    setting_area = get_container(
        ft.Row(
            [
                ft.Column(
                    [ 
                        ft.Text("解析設定"),
                        ft.Row([
                            get_normal_button_container(input_file_textbox),
                            get_normal_button_container(select_input_file_button), 
                        ]), 

                        get_normal_button_container(ign_textbox),

                        ft.Divider(),
                        
                        ft.Text("出力設定"),
                        ft.Row([
                            get_normal_button_container(output_file_textbox), 
                            get_normal_button_container(select_output_file_button), 
                        ]), 
    
                        get_normal_button_container(output_video_file_name_textbox),
                        get_normal_button_container(kill_time_offset_textbox),
                        get_normal_button_container(kill_time_interval_textbox),
                        get_normal_button_container(enable_separeted_output_checkbox),  
                    ],
                    # alignment=ft.MainAxisAlignment.CENTER, 
                    # horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ]
        ), 
        # h=500, 
        p=10, 
    )

    preview_area = get_container(
        ft.Column(
            [           
                ft.Text("プレビュー"),
                ft.Column(
                    [
                        ft.Row([
                            processing_status_text, 
                            progress_value_text, 
                        ]), 
                    
                        progress_bar, 
                        # preview_image_info_text, 
                        get_normal_button_container(preview_image), 
                        preview_image_control_buttons, 
                        ft.Row(
                            [
                                forward_preview_image_list_button, 
                                image_panels_container, 
                                back_preview_image_list_button
                            ]
                        ), 
                    ], 
                # alignment=ft.MainAxisAlignment.CENTER, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                ), 
            ],
        ), 
        # h=500, 
        p=10, 
    )

    kill_time_table_area = get_container(
        ft.Column(
            [
                ft.Text("キルタイム"),
                ft.Column(
                    [
                        ft.Row([
                            copy_kill_time_button, 
                            save_kill_time_button, 
                        ]), 
                        
                        kill_time_table_container, 
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                )
            ], 
            
        ),
        p=10, 
    )

    main_view = ft.Row(
        [
            setting_area,

            ft.VerticalDivider(), 

            preview_area, 

            ft.VerticalDivider(), 

            kill_time_table_area,
        ], 
        expand=True, 
        alignment=ft.MainAxisAlignment.CENTER
    )
    '''************************************************************
    ** 
    ************************************************************'''



    



    '''************************************************************
    ** メニューバー
    ************************************************************'''
    def handle_menu_item_click(e):
        print(f"{e.control.content.value}.on_click")
        page.show_snack_bar(ft.SnackBar(content=ft.Text(f"{e.control.content.value} was clicked!")))
        # appbar_text_ref.current.value = e.control.content.value
        page.update()

    def home_button_clicked(e):
        change_view_type(ViewType.MAIN)

    def settings_button_clicked(e):
        change_view_type(ViewType.SETTING)

    def info_button_clicked(e):
        change_view_type(ViewType.INFO)

    menubar = ft.MenuBar(
        expand=True,
        style=ft.MenuStyle(
            alignment=ft.alignment.top_left,
            # bgcolor=ft.colors.RED_100,
            mouse_cursor={ft.MaterialState.HOVERED: ft.MouseCursor.WAIT,
                          ft.MaterialState.DEFAULT: ft.MouseCursor.ZOOM_OUT},
        ),
        controls=[
            ft.SubmenuButton(
                content=ft.Text("General"),
                controls=[
                    ft.MenuItemButton(
                        content=ft.Text("ホーム"),
                        leading=ft.Icon(ft.icons.HOME),
                        style=ft.ButtonStyle(bgcolor={ft.MaterialState.HOVERED: ft.colors.GREEN_500}),
                        on_click=home_button_clicked
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("情報"),
                        leading=ft.Icon(ft.icons.INFO),
                        style=ft.ButtonStyle(bgcolor={ft.MaterialState.HOVERED: ft.colors.GREEN_500}),
                        on_click=info_button_clicked
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("終了"),
                        leading=ft.Icon(ft.icons.CLOSE),
                        style=ft.ButtonStyle(bgcolor={ft.MaterialState.HOVERED: ft.colors.GREEN_500}),
                        on_click=app_close
                    ),
                ]
            ),
            ft.SubmenuButton(
                content=ft.Text("Analyze"),
                controls=[
                    ft.MenuItemButton(
                        content=ft.Text("開始"),
                        leading=ft.Icon(ft.icons.INFO),
                        style=ft.ButtonStyle(bgcolor={ft.MaterialState.HOVERED: ft.colors.GREEN_500}),
                        on_click=start_button_clicked
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("停止"),
                        leading=ft.Icon(ft.icons.SAVE),
                        style=ft.ButtonStyle(bgcolor={ft.MaterialState.HOVERED: ft.colors.GREEN_500}),
                        on_click=stop_button_clicked
                    ),
                ]
            ),
            ft.SubmenuButton(
                content=ft.Text("Export"),
                controls=[
                    ft.MenuItemButton(
                        content=ft.Text("出力"),
                        leading=ft.Icon(ft.icons.INFO),
                        style=ft.ButtonStyle(bgcolor={ft.MaterialState.HOVERED: ft.colors.GREEN_500}),
                        on_click=extract_button_clicked
                    ),
                ]
            ),
        ]
    )
    '''************************************************************
    ** 
    ************************************************************'''




    page.add(
        ft.Row([menubar]),
    )
    page.add(main_view)



    
    setting_view = ft.Text("settings")
    info_view = ft.Text("info")

    view_list = {ViewType.MAIN : main_view, ViewType.SETTING : setting_view,  ViewType.INFO : info_view}

    def change_view_type(view_type):
        global current_view
        page.remove(view_list[current_view])
        current_view = view_type
        page.add(view_list[current_view])
        page.update()


    

    



    


    appbar_items = [
            ft.PopupMenuItem(text="Home", on_click=home_button_clicked),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(text="Settings", on_click=settings_button_clicked), 
            ft.PopupMenuItem(),
            ft.PopupMenuItem(text="Info", on_click=info_button_clicked)
        ]
    


    appbar = ft.AppBar(
            # leading=ft.Icon(ft.icons.GRID_GOLDENRATIO_ROUNDED),
            leading_width=100,
            title=ft.Container(
                content=ft.Text("POP1 Kill Extractor",size=18, text_align="start"),
                padding=5, 
            ), 
            center_title=False,
            toolbar_height=40,
            bgcolor=ft.colors.LIGHT_BLUE_ACCENT_700,

            # actions=[
            #     ft.Container(
            #         content=ft.PopupMenuButton(
            #             items=appbar_items
            #         ),
            #         margin=ft.margin.only(left=50, right=25), 
            #     )
            # ],
        )
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


    page.appbar = appbar



    


    page.update()




    
    


def set_page(page: ft.Page):
    '''************************************************************
    ** 画面全体の初期設定
    ************************************************************'''

    page.title = "POP1 Kill Extractor"
    # page.theme_mode = ft.ThemeMode.DARK
    # page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window_width = 1000
    # page.window_height = 200
    # page.window_left = 100
    # page.window_top = 400
    page.update()



if __name__ == '__main__':
    ft.app(target = main)