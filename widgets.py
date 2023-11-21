from dearpygui import dearpygui
from init import window_settings

class Widgets:
    """custom dearpygui widgets"""
    @staticmethod
    def label(text: str, tag: str, indent: int = -1):
        """spawns a label"""
        dearpygui.add_text(
            parent          = window_settings.WINDOW_TAG,
            default_value   = text,
            tag             = tag,
            indent          = indent
        )

    @staticmethod
    def button(text: str, tag: str, callback: any = None, width: int = 234):
        """spawns a button"""
        dearpygui.add_button(
            parent      = window_settings.WINDOW_TAG,
            label       = text,
            tag         = tag,
            width       = width,
            callback    = callback,
        )

    @staticmethod
    def textbox(text: str, tag: str, password: bool = False, hint: str = ""):
        """spawns a textbox"""
        dearpygui.add_input_text(
            parent      = window_settings.WINDOW_TAG,
            label       = text,
            password    = password,
            no_spaces   = True,
            tag         = tag,
            hint        = hint,
            width       = 234
        )

    @staticmethod
    def slider_int(text: str, tag: str, clamps: tuple = (0, 100), callback: any = None):
        """spawns a slider"""
        dearpygui.add_slider_int(
            parent      = window_settings.WINDOW_TAG,
            label       = text,
            tag         = tag,
            min_value   = clamps[0],
            max_value   = clamps[1],
            clamped     = True,
            callback    = callback
        )
