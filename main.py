from functions import Console as console
from functions import Callbacks as callbacks
from init import create_viewport, create_window, create_images, setup_window, setup_theme
from widgets import Widgets

if __name__ == "__main__":
    # clear the console window before setup
    # sometimes i get python warnings, this is mainly for my sanity
    console.clear()

    # create the window
    create_viewport("SaladTrackerViewport")
    create_window("SaladTrackerWindow")

    # window elemnts
    imgui = Widgets()
    imgui.label("Salad Tracker", "label_header", indent=75)
    create_images()

    imgui.label("Email", "label_email")
    imgui.textbox("", "textbox_email")
    imgui.button("Submit", "button_login", callback=callbacks.submit)

    # setup the window
    setup_theme()
    setup_window()
