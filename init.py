from dataclasses import dataclass
from dearpygui import dearpygui
from PIL import Image as img
import pyautogui
import data
import os
import io
import base64

WINDOW_TAG = None

@dataclass
class window_settings:
    """sets the default window attributes"""
    window_w: int = 250
    window_h: int = 225
    center_x: int = int((pyautogui.size().width / 2) - (window_h / 2))
    center_y: int = int((pyautogui.size().height / 2) - (window_w / 2))

def create_viewport(title: str = "Viewport_1"):
    """https://dearpygui.readthedocs.io/en/latest/documentation/viewport.html"""
    dearpygui.create_context()
    dearpygui.create_viewport(
        title       = title,
        width       = window_settings.window_w,
        height      = window_settings.window_h,
        x_pos       = window_settings.center_x,
        y_pos       = window_settings.center_y,
        min_width   = window_settings.window_w,
        min_height  = window_settings.window_h,
        vsync       = True,
        decorated   = False,
    )
    dearpygui.setup_dearpygui()

def create_window(tag: str):
    """https://dearpygui.readthedocs.io/en/latest/tutorials/dearpygui-structure.html"""
    global WINDOW_TAG
    WINDOW_TAG = tag
    with dearpygui.window(
        label           = tag,
        tag             = tag,
        width           = window_settings.window_w,
        height          = window_settings.window_h,
        pos             = (window_settings.center_x, window_settings.center_y),
        no_title_bar    = True,
        no_resize       = True):
        pass

def create_images():
    """stores images as bytes, rebuilds them and save to temp, then load as a texture"""
    global WINDOW_TAG
    temp = os.path.join(os.path.join(os.environ.get("LOCALAPPDATA"), "Temp"))
    salad_logo_bytes = b"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"
    img.open(io.BytesIO(base64.b64decode(salad_logo_bytes))).save(os.path.join(temp, "salad_logo.png"))
    w, h, _, d = dearpygui.load_image(os.path.join(temp, "salad_logo.png"))

    with dearpygui.texture_registry(show=False):
        dearpygui.add_static_texture(
            width           = w,
            height          = h,
            default_value   = d,
            tag             = "salad_logo"
        )
    
    dearpygui.add_image(
        parent      = WINDOW_TAG,
        texture_tag = "salad_logo",
        width       = 100,
        height      = 100,
        indent      = 67
    )

def setup_theme():
    """sets the theme"""
    global WINDOW_TAG
    with dearpygui.theme() as global_theme:
        with dearpygui.theme_component(dearpygui.mvAll):
            dearpygui.add_theme_color(dearpygui.mvThemeCol_WindowBg, (10, 33, 51, 255), category=dearpygui.mvThemeCat_Core)

    dearpygui.bind_item_theme(WINDOW_TAG, global_theme)

def setup_window():
    global WINDOW_TAG
    """https://dearpygui.readthedocs.io/en/latest/documentation/primary-window.html"""
    dearpygui.show_viewport()
    dearpygui.set_primary_window(WINDOW_TAG, True)
    dearpygui.start_dearpygui()
    while dearpygui.is_dearpygui_running():
        dearpygui.render_dearpygui_frame()
    dearpygui.destroy_context()

if __name__ == "__main__":
    pass