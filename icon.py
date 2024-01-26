from pystray import Icon
from pystray import MenuItem as item
from PIL import Image



def on_exit(icon, item):
    icon.stop()


def on_command(icon, item):
    icon.update_menu()


def create_systray_icon():
    image = Image.open("ac.png")
    menu = (
        item('Command', on_command, ),
        item('Exit', on_exit),
    )

    icon = Icon("name", image, "Title", menu)
    return icon


def main():
    icon = create_systray_icon()
    icon.run()


if __name__ == "__main__":
    main()
