import flet as ft
from pathlib import Path
import time
import base64
from scripts import main

def main(page):

    set_page(page)


    def button_clicked(e):
        page.add(ft.Text("Clicked!"))

    def app_close(e):
        print('Closed App')
        page.window_destroy()

    target_file = ft.Ref[ft.Text]()
    processing_status = ft.Ref[ft.Text]()
    
    image_extensions = ["jpeg", "jpg", "png"]
    output_folder = ft.Ref[ft.Text]()
    # page.add(target_file)
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            target_file.current.value = e.files[0].path
            # output_folder.current.value = str(Path(target_file.current.value).parent)
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    def show_file_picker(_: ft.ControlEvent):
        file_picker.pick_files(
            allow_multiple=False,
            file_type="custom",
            allowed_extensions=image_extensions
        )


    start_button = ft.ElevatedButton(text="開始", on_click=button_clicked)
    stop_button = ft.ElevatedButton(text="停止", on_click=button_clicked)
    extract_button = ft.ElevatedButton(text="出力", on_click=button_clicked)
    select_file_button = ft.ElevatedButton("ファイルを選択", on_click=show_file_picker)
    progress_bar = ft.ProgressBar(
        width=400, 
        color="pink", 
        bgcolor="#eeeeee"
    )
    progress_bar.value = 0.5
    processing_status_text = ft.Text(ref=processing_status)
    preview_image = ft.Image(fit=ft.ImageFit.CONTAIN)
    initial_image_path = "./images/initial_image.png"
    with open(initial_image_path, 'rb') as f:
        preview_image.src_base64 = base64.b64encode(f.read()).decode('utf-8')
    kill_time_log = ft.Column(
        spacing=5,
        height=150,
        width=200,
        scroll=ft.ScrollMode.ALWAYS,
        on_scroll_interval=0,
    )
    for i in range(0, 50):
        kill_time_log.controls.append(ft.Text(f"Text line {i}", key=str(i)))
    copy_kill_time_log_button = ft.ElevatedButton(text="クリップボードにコピー", on_click=button_clicked)
    save_kill_time_log_button = ft.ElevatedButton(text="保存", on_click=button_clicked)

    

    column = ft.Column(controls=[
        
        ft.Row(controls=[ft.ElevatedButton(text='アプリ終了', on_click=app_close)]), 
        ft.Row(controls=[start_button, stop_button, extract_button]), 
        ft.Row(controls=[ft.TextField(ref=target_file, label="ファイル", disabled=True), select_file_button]), 
        ft.Row(controls=[processing_status_text]), 
        ft.Row(controls=[ft.Column([ft.Text("処理状況"), progress_bar])]), 
        # ft.Row(controls=[preview_image]), 
        ft.Row(controls=[kill_time_log]), 
        ft.Row(controls=[copy_kill_time_log_button, save_kill_time_log_button]), 
    ])
    
    
    processing_status.current.value = '待機中'

    page.add(column)

    

    # for i in range(0, 101):
    #     progress_bar.value = i * 0.01
    #     time.sleep(0.1)
    #     page.update()
    
    
    

    


def set_page(page: ft.Page):
    '''
    画面全体の初期設定
    '''
    

    page.title = "test"

    # page.theme_mode = ft.ThemeMode.DARK
    # page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # page.window_width = 300
    # page.window_height = 200
    # page.window_left = 100
    # page.window_top = 400

    appbar_items = [
            ft.PopupMenuItem(text="Main"),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(text="Settings"), 
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(text="Info")
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
                    margin=ft.margin.only(left=50, right=25)
                )
            ],
        )
    page.appbar = appbar
    

    page.update()




if __name__ == '__main__':
    ft.app(target = main)