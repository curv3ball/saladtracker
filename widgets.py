from dearpygui import dearpygui
import data
from init import WINDOW_TAG

class Widgets:
    """custom dearpygui widgets"""
    @staticmethod
    def label(text: str, tag: str, indent: int = -1):
        dearpygui.add_text(
            parent          = WINDOW_TAG,
            default_value   = text,
            tag             = tag,
            indent          = indent
        )

    @staticmethod
    def button(text: str, tag: str, callback: any = None, width: int = 234):
        dearpygui.add_button(
            parent      = data.WINDOW_TAG,
            label       = text,
            tag         = tag,
            width       = width,
            callback    = callback,
        )

    @staticmethod
    def textbox(text: str, tag: str, password: bool = False, hint: str = ""):
        dearpygui.add_input_text(
            parent      = data.WINDOW_TAG,
            label       = text,
            password    = password,
            no_spaces   = True,
            tag         = tag,
            hint        = hint,
            width       = 234
        )

    @staticmethod
    def slider_int(text: str, tag: str, clamps: tuple = (0, 100), callback: any = None):
        dearpygui.add_slider_int(
            parent      = data.WINDOW_TAG,
            label       = text,
            tag         = tag,
            min_value   = clamps[0],
            max_value   = clamps[1],
            clamped     = True,
            callback    = callback
        )
