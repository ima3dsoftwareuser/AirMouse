import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox


# ============================================================
# AIR MOUSE LAUNCHER
# ============================================================
#
# Application:
#     AirMouseLauncher
#
# Controls:
#
#     GENERAL
#         - Cursor / trackpad settings
#
#     CUSTOM COMMANDS
#         - Keyboard
#         - Mouse
#         - Program
#         - URL
#         - Text
#
#     HAND COMMANDS
#         - Thumb
#         - Index
#         - Middle
#         - Ring
#         - Pinky
#         - Multiple fingers
#
#     VOICE COMMANDS
#         - Keyboard
#         - Mouse
#         - Program
#         - URL
#         - Text
#
#     SYSTEM
#         - Camera Server
#         - AirMouse
#         - Blue Trackpad
#         - Start / Stop
#         - Process monitoring
#
# Eye Tracker:
#     REMOVED
#
# Settings:
#     Existing settings.json structure is preserved.
#
# ============================================================


# ============================================================
# APPLICATION DIRECTORY
# ============================================================

if getattr(sys, "frozen", False):

    APP_DIR = os.path.dirname(
        os.path.abspath(sys.executable)
    )

else:

    APP_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )


# ============================================================
# FILES
# ============================================================

SETTINGS_FILE = os.path.join(
    APP_DIR,
    "settings.json"
)

ICON_FILE = os.path.join(
    APP_DIR,
    "AirMouseLauncher.ico"
)


# ============================================================
# PYTHON EXECUTABLE
# ============================================================

if getattr(sys, "frozen", False):

    # When the launcher itself is an EXE,
    # child programs are expected to be EXEs.
    PYTHON_EXECUTABLE = "py"

else:

    PYTHON_EXECUTABLE = sys.executable


# ============================================================
# CHILD PROGRAMS
# ============================================================

CAMERA_SERVER_FILE = "camera_server.py"
AIRMOUSE_FILE = "air_mouse.py"
BLUETRACKPAD_FILE = "blue_virtual_trackpad.py"


CAMERA_SERVER_CANDIDATES = [
    "camera_server.py",
    "CameraServer.py",
    "Camera_Server.py",
    "cameraServer.py",
    "CameraServerMain.py",

    "camera_server.exe",
    "CameraServer.exe",
]


AIRMOUSE_CANDIDATES = [
    "air_mouse.py",
    "AirMouse.py",
    "airmouse.py",
    "AirMouseHandler.py",
    "Air_Mouse.py",

    "air_mouse.exe",
    "AirMouse.exe",
]


BLUETRACKPAD_CANDIDATES = [
    "blue_virtual_trackpad.py",
    "BlueTrackpad.py",
    "bluetrackpad.py",
    "BlueTrackPad.py",
    "blue_trackpad.py",

    "blue_virtual_trackpad.exe",
    "BlueTrackpad.exe",
]


# ============================================================
# COLOURS
# ============================================================

BG = "#0B0F14"
PANEL = "#111820"
PANEL_2 = "#151E27"
PANEL_3 = "#1A2530"

BORDER = "#263442"

TEXT = "#E8EEF5"
TEXT_MUTED = "#8E9AA7"

BLUE = "#2388FF"
BLUE_HOVER = "#3A99FF"

GREEN = "#20C878"
GREEN_HOVER = "#32DB8A"

YELLOW = "#F0B429"
YELLOW_HOVER = "#FFC94D"

RED = "#E5484D"
RED_HOVER = "#F15C61"

PURPLE = "#9B6CFF"

WHITE = "#FFFFFF"


# ============================================================
# TRACKING COLOURS
# ============================================================

TRACKPAD_COLORS = [
    "BLUE",
    "GREEN",
    "RED",
    "YELLOW",
    "PURPLE",
    "ORANGE",
]


# ============================================================
# FINGERS
# ============================================================

FINGERS = [
    "Thumb",
    "Index",
    "Middle",
    "Ring",
    "Pinky",
]


# ============================================================
# ACTION TYPES
# ============================================================

ACTION_TYPES = [
    "Keyboard Key",
    "Mouse Action",
    "Program",
    "URL",
    "Text",
]


# ============================================================
# MOUSE ACTIONS
# ============================================================

MOUSE_ACTIONS = [
    "Left Click",
    "Right Click",
    "Middle Click",
    "Double Click",
    "Scroll Up",
    "Scroll Down",
    "Move Up",
    "Move Down",
    "Move Left",
    "Move Right",
]


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_SETTINGS = {

    "TRACKPAD_COLOR": "BLUE",

    "TRACKPAD_WIDTH": 500,
    "TRACKPAD_HEIGHT": 320,
    "TRACKPAD_LEFT": 50,
    "TRACKPAD_TOP": 200,

    "BLUE_MIN_AREA": 8,
    "BLUE_MAX_AREA": 1800,
    "BLUE_MIN_CIRCULARITY": 0.20,

    "TRACKPAD_DEAD_ZONE": 0.25,
    "TRACKPAD_FILTER_FRAMES": 2,

    "TRACKPAD_BASE_SENSITIVITY": 7.5,

    "TRACKPAD_ACCELERATION": 1.35,
    "TRACKPAD_MAX_ACCELERATION": 7.0,

    "TRACKPAD_SPEED_THRESHOLD": 1.5,

    "TRACKPAD_SMOOTHING": 0.82,

    "TRACKPAD_MAX_CURSOR_STEP": 250,

    "TRACKPAD_CURSOR_MARGIN": 2,

    "TRACKPAD_MAX_LOST_FRAMES": 8,

    "TRACKPAD_VIRTUAL_MOVEMENT_SCALE": 4.0,

    "CAMERA_SERVER_HOST": "127.0.0.1",
    "CAMERA_SERVER_PORT": 5000,

    "CUSTOM_COMMANDS": [],
    "HAND_COMMANDS": [],
    "VOICE_COMMANDS": [],
}


# ============================================================
# SETTINGS LOADING
# ============================================================

def load_settings():

    settings = {}

    if os.path.exists(SETTINGS_FILE):

        try:

            with open(
                SETTINGS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                loaded = json.load(file)

            if isinstance(loaded, dict):
                settings.update(loaded)

        except Exception as error:

            messagebox.showwarning(
                "Settings Warning",
                "Could not load settings.json.\n\n"
                f"{error}\n\n"
                "Default values will be used for missing settings."
            )

    for key, value in DEFAULT_SETTINGS.items():

        if key not in settings:
            settings[key] = value

    if not isinstance(
        settings.get("CUSTOM_COMMANDS"),
        list
    ):
        settings["CUSTOM_COMMANDS"] = []

    if not isinstance(
        settings.get("HAND_COMMANDS"),
        list
    ):
        settings["HAND_COMMANDS"] = []

    if not isinstance(
        settings.get("VOICE_COMMANDS"),
        list
    ):
        settings["VOICE_COMMANDS"] = []

    colour = str(
        settings.get(
            "TRACKPAD_COLOR",
            "BLUE"
        )
    ).upper()

    if colour not in TRACKPAD_COLORS:
        colour = "BLUE"

    settings["TRACKPAD_COLOR"] = colour

    return settings


# ============================================================
# SETTINGS SAVE
# ============================================================

def save_settings(settings):

    temporary_file = SETTINGS_FILE + ".tmp"

    try:

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                settings,
                file,
                indent=4,
                ensure_ascii=False
            )

        os.replace(
            temporary_file,
            SETTINGS_FILE
        )

        return True

    except Exception as error:

        try:

            if os.path.exists(
                temporary_file
            ):
                os.remove(
                    temporary_file
                )

        except Exception:
            pass

        messagebox.showerror(
            "Save Error",
            "Could not save settings.json.\n\n"
            f"{error}"
        )

        return False


# ============================================================
# FIND CHILD PROGRAM
# ============================================================

def find_program(
    preferred,
    candidates
):

    frozen = getattr(
        sys,
        "frozen",
        False
    )

    # --------------------------------------------------------
    # FROZEN / EXE MODE
    # --------------------------------------------------------

    if frozen:

        executable_map = {

            "camera_server.py":
                "camera_server.exe",

            "air_mouse.py":
                "air_mouse.exe",

            "blue_virtual_trackpad.py":
                "blue_virtual_trackpad.exe",

        }

        executable_name = executable_map.get(
            preferred
        )

        if executable_name:

            executable_path = os.path.join(
                APP_DIR,
                executable_name
            )

            if os.path.isfile(
                executable_path
            ):
                return executable_path

        for filename in candidates:

            if not filename.lower().endswith(
                ".exe"
            ):
                continue

            path = os.path.join(
                APP_DIR,
                filename
            )

            if os.path.isfile(path):
                return path

        return None

    # --------------------------------------------------------
    # PYTHON MODE
    # --------------------------------------------------------

    preferred_path = os.path.join(
        APP_DIR,
        preferred
    )

    if os.path.isfile(
        preferred_path
    ):
        return preferred_path

    for filename in candidates:

        path = os.path.join(
            APP_DIR,
            filename
        )

        if os.path.isfile(path):

            if filename.lower().endswith(
                ".py"
            ):
                return path

    return None


# ============================================================
# MAIN APPLICATION
# ============================================================

class AirMouseApp:

    def __init__(
        self,
        root
    ):

        self.root = root

        self.settings = load_settings()

        self.processes = {}

        self.running = False

        self.selected_custom_index = None
        self.selected_hand_index = None
        self.selected_voice_index = None

        self.setting_vars = {}

        self.hand_finger_vars = {}

        self.process_monitor_job = None

        self.build_style()
        self.build_window()
        self.build_header()
        self.build_navigation()
        self.build_pages()

        self.show_page(
            "General"
        )

        self.refresh_program_detection()
        self.refresh_process_status()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )


    # ========================================================
    # STYLE
    # ========================================================

    def build_style(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            ".",
            background=BG,
            foreground=TEXT,
            font=("Segoe UI", 10)
        )

        style.configure(
            "TFrame",
            background=BG
        )

        style.configure(
            "Panel.TFrame",
            background=PANEL
        )

        style.configure(
            "TLabel",
            background=BG,
            foreground=TEXT
        )

        style.configure(
            "Panel.TLabel",
            background=PANEL,
            foreground=TEXT
        )

        style.configure(
            "Muted.TLabel",
            background=BG,
            foreground=TEXT_MUTED
        )

        style.configure(
            "TButton",
            background=PANEL_3,
            foreground=TEXT,
            borderwidth=0,
            padding=(12, 8),
            font=("Segoe UI", 9, "bold")
        )

        style.map(
            "TButton",
            background=[
                ("active", "#263646")
            ]
        )

        style.configure(
            "Green.TButton",
            background=GREEN,
            foreground="#06140D"
        )

        style.map(
            "Green.TButton",
            background=[
                ("active", GREEN_HOVER)
            ]
        )

        style.configure(
            "Yellow.TButton",
            background=YELLOW,
            foreground="#171000"
        )

        style.map(
            "Yellow.TButton",
            background=[
                ("active", YELLOW_HOVER)
            ]
        )

        style.configure(
            "Red.TButton",
            background=RED,
            foreground=WHITE
        )

        style.map(
            "Red.TButton",
            background=[
                ("active", RED_HOVER)
            ]
        )

        style.configure(
            "Blue.TButton",
            background=BLUE,
            foreground=WHITE
        )

        style.map(
            "Blue.TButton",
            background=[
                ("active", BLUE_HOVER)
            ]
        )

        style.configure(
            "TCombobox",
            fieldbackground=PANEL_3,
            background=PANEL_3,
            foreground=TEXT,
            arrowcolor=TEXT,
            bordercolor=BORDER
        )

        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", PANEL_3)
            ],
            foreground=[
                ("readonly", TEXT)
            ]
        )

        style.configure(
            "Treeview",
            background=PANEL_2,
            fieldbackground=PANEL_2,
            foreground=TEXT,
            bordercolor=BORDER,
            rowheight=34
        )

        style.configure(
            "Treeview.Heading",
            background="#202C38",
            foreground="#AFC0D1",
            font=("Segoe UI", 9, "bold")
        )

        style.map(
            "Treeview",
            background=[
                ("selected", "#24527D")
            ],
            foreground=[
                ("selected", WHITE)
            ]
        )


    # ========================================================
    # WINDOW
    # ========================================================

    def build_window(self):

        self.root.title(
            "AirMouseLauncher"
        )

        self.root.geometry(
            "1180x760"
        )

        self.root.minsize(
            980,
            650
        )

        self.root.configure(
            bg=BG
        )

        # ----------------------------------------------------
        # Application icon
        # ----------------------------------------------------

        if os.path.isfile(
            ICON_FILE
        ):

            try:

                self.root.iconbitmap(
                    ICON_FILE
                )

            except Exception:
                pass


    # ========================================================
    # HEADER
    # ========================================================

    def build_header(self):

        header = tk.Frame(
            self.root,
            bg=BG,
            height=72
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)

        tk.Label(
            header,
            text="AirMouseLauncher",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 20, "bold")
        ).pack(
            side="left",
            padx=24
        )

        tk.Label(
            header,
            text="Gesture • Voice • Virtual Trackpad",
            bg=BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9)
        ).pack(
            side="left"
        )

        self.status_label = tk.Label(
            header,
            text="● STOPPED",
            bg=BG,
            fg=RED,
            font=("Segoe UI", 10, "bold")
        )

        self.status_label.pack(
            side="right",
            padx=20
        )

        self.stop_button = ttk.Button(
            header,
            text="■ STOP",
            style="Red.TButton",
            command=self.stop_system
        )

        self.stop_button.pack(
            side="right",
            padx=5
        )

        self.start_button = ttk.Button(
            header,
            text="▶ START",
            style="Green.TButton",
            command=self.start_system
        )

        self.start_button.pack(
            side="right",
            padx=5
        )


    # ========================================================
    # NAVIGATION
    # ========================================================

    def build_navigation(self):

        nav = tk.Frame(
            self.root,
            bg=PANEL,
            width=190
        )

        nav.pack(
            side="left",
            fill="y"
        )

        nav.pack_propagate(False)

        self.nav_buttons = {}

        pages = [
            "General",
            "Custom Commands",
            "Hand Commands",
            "Voice Commands",
            "System"
        ]

        for page in pages:

            button = tk.Button(
                nav,
                text=page,
                anchor="w",
                bg=PANEL,
                fg=TEXT_MUTED,
                activebackground=PANEL_3,
                activeforeground=TEXT,
                relief="flat",
                borderwidth=0,
                padx=20,
                pady=13,
                font=("Segoe UI", 10, "bold"),
                command=lambda p=page:
                    self.show_page(p)
            )

            button.pack(
                fill="x",
                pady=1
            )

            self.nav_buttons[
                page
            ] = button


    # ========================================================
    # PAGE CONTAINER
    # ========================================================

    def build_pages(self):

        self.page_container = tk.Frame(
            self.root,
            bg=BG
        )

        self.page_container.pack(
            side="left",
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        self.pages = {}

        self.build_general_page()
        self.build_custom_page()
        self.build_hand_page()
        self.build_voice_page()
        self.build_system_page()


    # ========================================================
    # SHOW PAGE
    # ========================================================

    def show_page(
        self,
        name
    ):

        for page in self.pages.values():
            page.pack_forget()

        self.pages[name].pack(
            fill="both",
            expand=True
        )

        for page_name, button in self.nav_buttons.items():

            if page_name == name:

                button.configure(
                    bg="#1E4D76",
                    fg=WHITE
                )

            else:

                button.configure(
                    bg=PANEL,
                    fg=TEXT_MUTED
                )


    # ========================================================
    # GENERAL PAGE
    # ========================================================

    def build_general_page(self):

        page = tk.Frame(
            self.page_container,
            bg=BG
        )

        self.pages[
            "General"
        ] = page

        tk.Label(
            page,
            text="General Settings",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 18, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            page,
            text="Configure the shared virtual trackpad settings.",
            bg=BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            pady=(2, 15)
        )

        cursor_panel = self.create_panel(
            page,
            "Cursor Settings"
        )

        cursor_panel.pack(
            fill="x",
            pady=8
        )

        self.add_label(
            cursor_panel,
            "Tracking Colour"
        )

        self.tracking_colour_var = tk.StringVar(
            value=self.settings.get(
                "TRACKPAD_COLOR",
                "BLUE"
            )
        )

        self.tracking_colour_combo = ttk.Combobox(
            cursor_panel,
            textvariable=self.tracking_colour_var,
            values=TRACKPAD_COLORS,
            state="readonly",
            width=24
        )

        self.tracking_colour_combo.grid(
            row=0,
            column=1,
            sticky="w",
            padx=10,
            pady=8
        )

        tk.Label(
            cursor_panel,
            text="Colour detected by BlueTrackpad",
            bg=PANEL,
            fg=TEXT_MUTED
        ).grid(
            row=0,
            column=2,
            sticky="w",
            padx=10
        )

        settings = [

            ("Base Sensitivity",
             "TRACKPAD_BASE_SENSITIVITY"),

            ("Acceleration",
             "TRACKPAD_ACCELERATION"),

            ("Maximum Acceleration",
             "TRACKPAD_MAX_ACCELERATION"),

            ("Speed Threshold",
             "TRACKPAD_SPEED_THRESHOLD"),

            ("Smoothing",
             "TRACKPAD_SMOOTHING"),

            ("Maximum Cursor Step",
             "TRACKPAD_MAX_CURSOR_STEP"),

            ("Dead Zone",
             "TRACKPAD_DEAD_ZONE"),

            ("Filter Frames",
             "TRACKPAD_FILTER_FRAMES"),

            ("Cursor Margin",
             "TRACKPAD_CURSOR_MARGIN"),

            ("Lost Frames",
             "TRACKPAD_MAX_LOST_FRAMES"),
        ]

        for row, (
            label,
            key
        ) in enumerate(
            settings,
            start=1
        ):

            self.add_setting_entry(
                cursor_panel,
                row,
                label,
                key
            )

        ttk.Button(
            cursor_panel,
            text="SAVE CURSOR SETTINGS",
            style="Blue.TButton",
            command=self.save_cursor_settings
        ).grid(
            row=len(settings) + 1,
            column=1,
            sticky="w",
            padx=10,
            pady=15
        )

        pad_panel = self.create_panel(
            page,
            "Virtual Trackpad Window"
        )

        pad_panel.pack(
            fill="x",
            pady=8
        )

        pad_settings = [

            ("Width",
             "TRACKPAD_WIDTH"),

            ("Height",
             "TRACKPAD_HEIGHT"),

            ("Left Position",
             "TRACKPAD_LEFT"),

            ("Top Position",
             "TRACKPAD_TOP"),
        ]

        for row, (
            label,
            key
        ) in enumerate(
            pad_settings
        ):

            self.add_setting_entry(
                pad_panel,
                row,
                label,
                key
            )

        ttk.Button(
            pad_panel,
            text="SAVE WINDOW SETTINGS",
            style="Blue.TButton",
            command=self.save_cursor_settings
        ).grid(
            row=len(pad_settings),
            column=1,
            sticky="w",
            padx=10,
            pady=15
        )


    # ========================================================
    # CREATE PANEL
    # ========================================================

    def create_panel(
        self,
        parent,
        title
    ):

        frame = tk.Frame(
            parent,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        tk.Label(
            frame,
            text=title,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 12, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=15,
            pady=12
        )

        return frame


    # ========================================================
    # LABEL HELPER
    # ========================================================

    def add_label(
        self,
        parent,
        text
    ):

        row = parent.grid_size()[1]

        tk.Label(
            parent,
            text=text,
            bg=PANEL,
            fg=TEXT
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=15,
            pady=7
        )


    # ========================================================
    # SETTING ENTRY
    # ========================================================

    def add_setting_entry(
        self,
        parent,
        row,
        label,
        key
    ):

        tk.Label(
            parent,
            text=label,
            bg=PANEL,
            fg=TEXT
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=15,
            pady=6
        )

        variable = tk.StringVar(
            value=str(
                self.settings.get(
                    key,
                    ""
                )
            )
        )

        entry = tk.Entry(
            parent,
            textvariable=variable,
            bg=PANEL_3,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat",
            width=25
        )

        entry.grid(
            row=row,
            column=1,
            sticky="w",
            padx=10,
            pady=6
        )

        self.setting_vars[
            key
        ] = variable


    # ========================================================
    # SAVE CURSOR SETTINGS
    # ========================================================

    def save_cursor_settings(self):

        colour = (
            self.tracking_colour_var.get()
            .strip()
            .upper()
        )

        if colour not in TRACKPAD_COLORS:
            colour = "BLUE"

        self.settings[
            "TRACKPAD_COLOR"
        ] = colour

        for key, variable in self.setting_vars.items():

            value = variable.get().strip()

            if value == "":
                continue

            old_value = self.settings.get(
                key,
                value
            )

            try:

                if isinstance(
                    old_value,
                    bool
                ):

                    self.settings[key] = (
                        value.lower()
                        in (
                            "1",
                            "true",
                            "yes",
                            "on"
                        )
                    )

                elif isinstance(
                    old_value,
                    int
                ):

                    self.settings[key] = int(
                        float(value)
                    )

                elif isinstance(
                    old_value,
                    float
                ):

                    self.settings[key] = float(
                        value
                    )

                else:

                    self.settings[key] = value

            except ValueError:

                messagebox.showerror(
                    "Invalid Setting",
                    f"Invalid value for:\n{key}"
                )

                return

        if save_settings(
            self.settings
        ):

            messagebox.showinfo(
                "Settings Saved",
                "Settings saved successfully."
            )


    # ========================================================
    # CUSTOM COMMAND PAGE
    # ========================================================

    def build_custom_page(self):

        page = tk.Frame(
            self.page_container,
            bg=BG
        )

        self.pages[
            "Custom Commands"
        ] = page

        tk.Label(
            page,
            text="Custom Commands",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 18, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            page,
            text=(
                "Create keyboard, mouse, program, URL or text commands."
            ),
            bg=BG,
            fg=TEXT_MUTED
        ).pack(
            anchor="w",
            pady=(2, 15)
        )

        panel = tk.Frame(
            page,
            bg=PANEL
        )

        panel.pack(
            fill="both",
            expand=True
        )

        columns = (
            "name",
            "type",
            "value"
        )

        self.custom_tree = ttk.Treeview(
            panel,
            columns=columns,
            show="headings"
        )

        self.custom_tree.heading(
            "name",
            text="COMMAND"
        )

        self.custom_tree.heading(
            "type",
            text="ACTION TYPE"
        )

        self.custom_tree.heading(
            "value",
            text="ACTION"
        )

        self.custom_tree.column(
            "name",
            width=220
        )

        self.custom_tree.column(
            "type",
            width=180
        )

        self.custom_tree.column(
            "value",
            width=500
        )

        self.custom_tree.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=12
        )

        self.custom_tree.bind(
            "<<TreeviewSelect>>",
            self.custom_selected
        )

        buttons = tk.Frame(
            page,
            bg=BG
        )

        buttons.pack(
            fill="x",
            pady=10
        )

        ttk.Button(
            buttons,
            text="+ ADD",
            style="Green.TButton",
            command=self.add_custom_command
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            buttons,
            text="EDIT",
            style="Yellow.TButton",
            command=self.edit_custom_command
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            buttons,
            text="DELETE",
            style="Red.TButton",
            command=self.delete_custom_command
        ).pack(
            side="left",
            padx=4
        )

        self.refresh_custom_commands()


    # ========================================================
    # CUSTOM SELECTION
    # ========================================================

    def custom_selected(
        self,
        event=None
    ):

        selection = self.custom_tree.selection()

        if not selection:

            self.selected_custom_index = None

            return

        item = selection[0]

        tags = self.custom_tree.item(
            item,
            "tags"
        )

        if tags:

            self.selected_custom_index = int(
                tags[0]
            )


    # ========================================================
    # REFRESH CUSTOM COMMANDS
    # ========================================================

    def refresh_custom_commands(self):

        for item in self.custom_tree.get_children():

            self.custom_tree.delete(
                item
            )

        for index, command in enumerate(
            self.settings["CUSTOM_COMMANDS"]
        ):

            self.custom_tree.insert(
                "",
                "end",
                values=(
                    command.get(
                        "name",
                        ""
                    ),
                    command.get(
                        "type",
                        ""
                    ),
                    command.get(
                        "value",
                        ""
                    )
                ),
                tags=(str(index),)
            )


    # ========================================================
    # ADD CUSTOM
    # ========================================================

    def add_custom_command(self):

        result = self.command_editor(
            "Add Custom Command"
        )

        if result is None:
            return

        self.settings[
            "CUSTOM_COMMANDS"
        ].append(
            result
        )

        if save_settings(
            self.settings
        ):

            self.refresh_custom_commands()


    # ========================================================
    # EDIT CUSTOM
    # ========================================================

    def edit_custom_command(self):

        if self.selected_custom_index is None:

            messagebox.showwarning(
                "Select Command",
                "Select a command first."
            )

            return

        commands = self.settings[
            "CUSTOM_COMMANDS"
        ]

        index = self.selected_custom_index

        if not (
            0 <= index < len(commands)
        ):
            return

        result = self.command_editor(
            "Edit Custom Command",
            commands[index]
        )

        if result is None:
            return

        commands[index] = result

        if save_settings(
            self.settings
        ):

            self.refresh_custom_commands()


    # ========================================================
    # DELETE CUSTOM
    # ========================================================

    def delete_custom_command(self):

        if self.selected_custom_index is None:

            messagebox.showwarning(
                "Select Command",
                "Select a command first."
            )

            return

        if not messagebox.askyesno(
            "Delete Command",
            "Delete the selected custom command?"
        ):
            return

        index = self.selected_custom_index

        if 0 <= index < len(
            self.settings["CUSTOM_COMMANDS"]
        ):

            del self.settings[
                "CUSTOM_COMMANDS"
            ][index]

        self.selected_custom_index = None

        if save_settings(
            self.settings
        ):

            self.refresh_custom_commands()


    # ========================================================
    # HAND COMMAND PAGE
    # ========================================================

    def build_hand_page(self):

        page = tk.Frame(
            self.page_container,
            bg=BG
        )

        self.pages[
            "Hand Commands"
        ] = page

        tk.Label(
            page,
            text="Hand Commands",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 18, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            page,
            text=(
                "Select individual fingers to create a hand command."
            ),
            bg=BG,
            fg=TEXT_MUTED
        ).pack(
            anchor="w",
            pady=(2, 12)
        )

        outer = tk.Frame(
            page,
            bg=BG
        )

        outer.pack(
            fill="both",
            expand=True
        )

        self.hand_canvas = tk.Canvas(
            outer,
            bg=BG,
            highlightthickness=0
        )

        self.hand_scrollbar = ttk.Scrollbar(
            outer,
            orient="vertical",
            command=self.hand_canvas.yview
        )

        self.hand_canvas.configure(
            yscrollcommand=self.hand_scrollbar.set
        )

        self.hand_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.hand_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.hand_scroll_frame = tk.Frame(
            self.hand_canvas,
            bg=BG
        )

        self.hand_window = self.hand_canvas.create_window(
            (0, 0),
            window=self.hand_scroll_frame,
            anchor="nw"
        )

        self.hand_scroll_frame.bind(
            "<Configure>",
            self.update_hand_scroll_region
        )

        self.hand_canvas.bind(
            "<Configure>",
            self.resize_hand_scroll_frame
        )

        self.hand_canvas.bind(
            "<MouseWheel>",
            self.hand_mousewheel
        )

        self.hand_scroll_frame.bind(
            "<MouseWheel>",
            self.hand_mousewheel
        )

        self.hand_canvas.bind(
            "<Button-4>",
            self.hand_mousewheel_up
        )

        self.hand_canvas.bind(
            "<Button-5>",
            self.hand_mousewheel_down
        )

        list_panel = self.create_panel(
            self.hand_scroll_frame,
            "Assigned Hand Commands"
        )

        list_panel.pack(
            fill="x",
            pady=8
        )

        columns = (
            "gesture",
            "type",
            "value"
        )

        self.hand_tree = ttk.Treeview(
            list_panel,
            columns=columns,
            show="headings",
            height=7
        )

        self.hand_tree.heading(
            "gesture",
            text="FINGERS"
        )

        self.hand_tree.heading(
            "type",
            text="ACTION TYPE"
        )

        self.hand_tree.heading(
            "value",
            text="ACTION"
        )

        self.hand_tree.column(
            "gesture",
            width=280
        )

        self.hand_tree.column(
            "type",
            width=180
        )

        self.hand_tree.column(
            "value",
            width=500
        )

        self.hand_tree.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="nsew",
            padx=12,
            pady=10
        )

        list_panel.grid_columnconfigure(
            0,
            weight=1
        )

        self.hand_tree.bind(
            "<<TreeviewSelect>>",
            self.hand_selected
        )

        buttons = tk.Frame(
            self.hand_scroll_frame,
            bg=BG
        )

        buttons.pack(
            fill="x",
            pady=8
        )

        ttk.Button(
            buttons,
            text="+ ADD HAND COMMAND",
            style="Green.TButton",
            command=self.add_hand_command
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            buttons,
            text="EDIT",
            style="Yellow.TButton",
            command=self.edit_hand_command
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            buttons,
            text="DELETE",
            style="Red.TButton",
            command=self.delete_hand_command
        ).pack(
            side="left",
            padx=4
        )

        settings_panel = self.create_panel(
            self.hand_scroll_frame,
            "Add / Edit Hand Command"
        )

        settings_panel.pack(
            fill="x",
            pady=8
        )

        tk.Label(
            settings_panel,
            text="Select Fingers",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=1,
            column=0,
            sticky="nw",
            padx=15,
            pady=10
        )

        fingers_frame = tk.Frame(
            settings_panel,
            bg=PANEL
        )

        fingers_frame.grid(
            row=1,
            column=1,
            sticky="w",
            padx=10,
            pady=10
        )

        self.hand_finger_vars = {}

        for row, finger in enumerate(
            FINGERS
        ):

            variable = tk.BooleanVar(
                value=False
            )

            self.hand_finger_vars[
                finger
            ] = variable

            tk.Checkbutton(
                fingers_frame,
                text=finger,
                variable=variable,
                bg=PANEL,
                fg=TEXT,
                activebackground=PANEL,
                activeforeground=TEXT,
                selectcolor=PANEL_3,
                highlightthickness=0,
                bd=0,
                font=("Segoe UI", 10),
                anchor="w"
            ).grid(
                row=row,
                column=0,
                sticky="w",
                pady=3
            )

        tk.Label(
            settings_panel,
            text=(
                "Select one or more fingers.\n"
                "Example: Thumb + Index"
            ),
            bg=PANEL,
            fg=TEXT_MUTED,
            justify="left"
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=10,
            pady=10
        )

        tk.Label(
            settings_panel,
            text="Action Type",
            bg=PANEL,
            fg=TEXT
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=15,
            pady=10
        )

        self.hand_action_type_var = tk.StringVar(
            value=ACTION_TYPES[0]
        )

        ttk.Combobox(
            settings_panel,
            textvariable=self.hand_action_type_var,
            values=ACTION_TYPES,
            state="readonly",
            width=30
        ).grid(
            row=2,
            column=1,
            sticky="w",
            padx=10,
            pady=10
        )

        tk.Label(
            settings_panel,
            text="Action",
            bg=PANEL,
            fg=TEXT
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=15,
            pady=10
        )

        self.hand_action_value_var = tk.StringVar()

        tk.Entry(
            settings_panel,
            textvariable=self.hand_action_value_var,
            bg=PANEL_3,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat",
            width=40
        ).grid(
            row=3,
            column=1,
            sticky="w",
            padx=10,
            pady=10
        )

        tk.Label(
            settings_panel,
            text=(
                "Keyboard: Ctrl+C\n"
                "Mouse: Left Click\n"
                "Program: program.exe\n"
                "URL: https://example.com\n"
                "Text: Hello World"
            ),
            bg=PANEL,
            fg=TEXT_MUTED,
            justify="left"
        ).grid(
            row=4,
            column=0,
            columnspan=3,
            sticky="w",
            padx=15,
            pady=10
        )

        self.hand_save_button = ttk.Button(
            settings_panel,
            text="SAVE HAND COMMAND",
            style="Blue.TButton",
            command=self.save_hand_command_from_panel
        )

        self.hand_save_button.grid(
            row=5,
            column=1,
            sticky="w",
            padx=10,
            pady=15
        )

        ttk.Button(
            settings_panel,
            text="CLEAR",
            command=self.clear_hand_command_panel
        ).grid(
            row=5,
            column=2,
            sticky="w",
            padx=10,
            pady=15
        )

        self.hand_info_label = tk.Label(
            self.hand_scroll_frame,
            text="Ready to add a new hand command.",
            bg=BG,
            fg=TEXT_MUTED,
            justify="left"
        )

        self.hand_info_label.pack(
            anchor="w",
            pady=5
        )

        self.refresh_hand_commands()

        self.root.after(
            100,
            self.update_hand_scroll_region
        )


    # ========================================================
    # HAND SCROLL
    # ========================================================

    def update_hand_scroll_region(
        self,
        event=None
    ):

        if hasattr(
            self,
            "hand_canvas"
        ):

            self.hand_canvas.configure(
                scrollregion=self.hand_canvas.bbox("all")
            )


    def resize_hand_scroll_frame(
        self,
        event
    ):

        if hasattr(
            self,
            "hand_canvas"
        ):

            self.hand_canvas.itemconfigure(
                self.hand_window,
                width=event.width
            )


    def hand_mousewheel(
        self,
        event
    ):

        try:

            if event.delta:

                amount = int(
                    -event.delta / 120
                )

                if amount == 0:

                    amount = (
                        -1
                        if event.delta > 0
                        else 1
                    )

                self.hand_canvas.yview_scroll(
                    amount,
                    "units"
                )

        except Exception:
            pass


    def hand_mousewheel_up(
        self,
        event=None
    ):

        self.hand_canvas.yview_scroll(
            -3,
            "units"
        )


    def hand_mousewheel_down(
        self,
        event=None
    ):

        self.hand_canvas.yview_scroll(
            3,
            "units"
        )


    # ========================================================
    # HAND HELPERS
    # ========================================================

    def get_selected_fingers(self):

        selected = []

        for finger in FINGERS:

            variable = self.hand_finger_vars.get(
                finger
            )

            if variable and variable.get():

                selected.append(
                    finger
                )

        return selected


    def set_selected_fingers(
        self,
        fingers
    ):

        if isinstance(
            fingers,
            str
        ):

            old_map = {

                "Open Palm":
                    FINGERS.copy(),

                "Five Fingers":
                    FINGERS.copy(),

                "Fist":
                    [],

                "Two Fingers":
                    [
                        "Index",
                        "Middle"
                    ],

                "Three Fingers":
                    [
                        "Index",
                        "Middle",
                        "Ring"
                    ],

                "Four Fingers":
                    [
                        "Index",
                        "Middle",
                        "Ring",
                        "Pinky"
                    ],

                "Pinch":
                    [
                        "Thumb",
                        "Index"
                    ]
            }

            fingers = old_map.get(
                fingers,
                []
            )

        if not isinstance(
            fingers,
            list
        ):

            fingers = []

        normalized = {
            str(f).strip().lower()
            for f in fingers
        }

        for finger in FINGERS:

            self.hand_finger_vars[
                finger
            ].set(
                finger.lower()
                in normalized
            )


    def format_fingers(
        self,
        fingers
    ):

        if not fingers:

            return "No fingers selected"

        return " + ".join(
            fingers
        )


    # ========================================================
    # HAND SELECTED
    # ========================================================

    def hand_selected(
        self,
        event=None
    ):

        selection = self.hand_tree.selection()

        if not selection:

            self.selected_hand_index = None

            return

        item = selection[0]

        tags = self.hand_tree.item(
            item,
            "tags"
        )

        if not tags:
            return

        index = int(
            tags[0]
        )

        self.selected_hand_index = index

        commands = self.settings[
            "HAND_COMMANDS"
        ]

        if not (
            0 <= index < len(commands)
        ):
            return

        command = commands[index]

        fingers = command.get(
            "fingers",
            []
        )

        if not fingers:

            fingers = command.get(
                "gesture",
                []
            )

        self.set_selected_fingers(
            fingers
        )

        self.hand_action_type_var.set(
            command.get(
                "type",
                ACTION_TYPES[0]
            )
        )

        self.hand_action_value_var.set(
            command.get(
                "value",
                ""
            )
        )

        self.hand_info_label.configure(
            text=(
                "Editing selected command:\n"
                f"Fingers: {self.format_fingers(fingers)}\n"
                f"Action Type: {command.get('type', '')}\n"
                f"Action: {command.get('value', '')}"
            )
        )

        self.hand_save_button.configure(
            text="UPDATE HAND COMMAND"
        )


    # ========================================================
    # REFRESH HAND
    # ========================================================

    def refresh_hand_commands(self):

        for item in self.hand_tree.get_children():

            self.hand_tree.delete(
                item
            )

        for index, command in enumerate(
            self.settings["HAND_COMMANDS"]
        ):

            fingers = command.get(
                "fingers",
                []
            )

            if not fingers:

                old_gesture = command.get(
                    "gesture",
                    ""
                )

                if isinstance(
                    old_gesture,
                    list
                ):

                    fingers = old_gesture

                else:

                    fingers = []

            self.hand_tree.insert(
                "",
                "end",
                values=(
                    self.format_fingers(
                        fingers
                    ),
                    command.get(
                        "type",
                        ""
                    ),
                    command.get(
                        "value",
                        ""
                    )
                ),
                tags=(str(index),)
            )

        self.root.after(
            50,
            self.update_hand_scroll_region
        )


    # ========================================================
    # CLEAR HAND PANEL
    # ========================================================

    def clear_hand_command_panel(self):

        for finger in FINGERS:

            self.hand_finger_vars[
                finger
            ].set(False)

        self.hand_action_type_var.set(
            ACTION_TYPES[0]
        )

        self.hand_action_value_var.set(
            ""
        )

        self.selected_hand_index = None

        for item in self.hand_tree.selection():

            self.hand_tree.selection_remove(
                item
            )

        self.hand_info_label.configure(
            text="Ready to add a new hand command."
        )

        self.hand_save_button.configure(
            text="SAVE HAND COMMAND"
        )


    # ========================================================
    # SAVE HAND COMMAND
    # ========================================================

    def save_hand_command_from_panel(self):

        fingers = self.get_selected_fingers()

        action_type = (
            self.hand_action_type_var.get()
            .strip()
        )

        action_value = (
            self.hand_action_value_var.get()
            .strip()
        )

        if not fingers:

            messagebox.showwarning(
                "No Fingers Selected",
                "Tick at least one finger."
            )

            return

        if not action_type:

            messagebox.showwarning(
                "Missing Action Type",
                "Select an action type."
            )

            return

        if not action_value:

            messagebox.showwarning(
                "Missing Action",
                "Enter an action."
            )

            return

        command = {

            "fingers":
                fingers,

            "type":
                action_type,

            "value":
                action_value
        }

        commands = self.settings[
            "HAND_COMMANDS"
        ]

        if self.selected_hand_index is not None:

            index = self.selected_hand_index

            if 0 <= index < len(commands):

                commands[index] = command

            else:

                commands.append(
                    command
                )

        else:

            commands.append(
                command
            )

        if save_settings(
            self.settings
        ):

            self.refresh_hand_commands()

            self.clear_hand_command_panel()

            messagebox.showinfo(
                "Hand Command Saved",
                "Hand command saved successfully."
            )


    # ========================================================
    # ADD HAND
    # ========================================================

    def add_hand_command(self):

        self.clear_hand_command_panel()

        self.root.after(
            50,
            lambda:
                self.hand_canvas.yview_moveto(1.0)
        )


    # ========================================================
    # EDIT HAND
    # ========================================================

    def edit_hand_command(self):

        if self.selected_hand_index is None:

            messagebox.showwarning(
                "Select Hand Command",
                "Select a hand command first."
            )

            return

        commands = self.settings[
            "HAND_COMMANDS"
        ]

        index = self.selected_hand_index

        if not (
            0 <= index < len(commands)
        ):
            return

        command = commands[index]

        fingers = command.get(
            "fingers",
            []
        )

        if not fingers:

            fingers = command.get(
                "gesture",
                []
            )

        self.set_selected_fingers(
            fingers
        )

        self.hand_action_type_var.set(
            command.get(
                "type",
                ACTION_TYPES[0]
            )
        )

        self.hand_action_value_var.set(
            command.get(
                "value",
                ""
            )
        )

        self.hand_info_label.configure(
            text=(
                "Editing selected command.\n"
                f"Fingers: {self.format_fingers(fingers)}"
            )
        )

        self.hand_save_button.configure(
            text="UPDATE HAND COMMAND"
        )

        self.root.after(
            50,
            lambda:
                self.hand_canvas.yview_moveto(1.0)
        )


    # ========================================================
    # DELETE HAND
    # ========================================================

    def delete_hand_command(self):

        if self.selected_hand_index is None:

            messagebox.showwarning(
                "Select Hand Command",
                "Select a hand command first."
            )

            return

        if not messagebox.askyesno(
            "Delete Hand Command",
            "Delete the selected hand command?"
        ):
            return

        index = self.selected_hand_index

        commands = self.settings[
            "HAND_COMMANDS"
        ]

        if 0 <= index < len(commands):

            del commands[index]

        self.selected_hand_index = None

        if save_settings(
            self.settings
        ):

            self.refresh_hand_commands()

            self.clear_hand_command_panel()


    # ========================================================
    # VOICE PAGE
    # ========================================================

    def build_voice_page(self):

        page = tk.Frame(
            self.page_container,
            bg=BG
        )

        self.pages[
            "Voice Commands"
        ] = page

        tk.Label(
            page,
            text="Voice Commands",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 18, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            page,
            text="Assign actions to voice commands.",
            bg=BG,
            fg=TEXT_MUTED
        ).pack(
            anchor="w",
            pady=(2, 15)
        )

        panel = tk.Frame(
            page,
            bg=PANEL
        )

        panel.pack(
            fill="both",
            expand=True
        )

        columns = (
            "command",
            "type",
            "value"
        )

        self.voice_tree = ttk.Treeview(
            panel,
            columns=columns,
            show="headings"
        )

        self.voice_tree.heading(
            "command",
            text="VOICE COMMAND"
        )

        self.voice_tree.heading(
            "type",
            text="ACTION TYPE"
        )

        self.voice_tree.heading(
            "value",
            text="ACTION"
        )

        self.voice_tree.column(
            "command",
            width=260
        )

        self.voice_tree.column(
            "type",
            width=180
        )

        self.voice_tree.column(
            "value",
            width=500
        )

        self.voice_tree.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=12
        )

        self.voice_tree.bind(
            "<<TreeviewSelect>>",
            self.voice_selected
        )

        buttons = tk.Frame(
            page,
            bg=BG
        )

        buttons.pack(
            fill="x",
            pady=10
        )

        ttk.Button(
            buttons,
            text="+ ADD",
            style="Green.TButton",
            command=self.add_voice_command
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            buttons,
            text="EDIT",
            style="Yellow.TButton",
            command=self.edit_voice_command
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            buttons,
            text="DELETE",
            style="Red.TButton",
            command=self.delete_voice_command
        ).pack(
            side="left",
            padx=4
        )

        self.refresh_voice_commands()


    # ========================================================
    # VOICE SELECTED
    # ========================================================

    def voice_selected(
        self,
        event=None
    ):

        selection = self.voice_tree.selection()

        if not selection:

            self.selected_voice_index = None

            return

        item = selection[0]

        tags = self.voice_tree.item(
            item,
            "tags"
        )

        if tags:

            self.selected_voice_index = int(
                tags[0]
            )


    # ========================================================
    # REFRESH VOICE
    # ========================================================

    def refresh_voice_commands(self):

        for item in self.voice_tree.get_children():

            self.voice_tree.delete(
                item
            )

        for index, command in enumerate(
            self.settings["VOICE_COMMANDS"]
        ):

            self.voice_tree.insert(
                "",
                "end",
                values=(
                    command.get(
                        "command",
                        ""
                    ),
                    command.get(
                        "type",
                        ""
                    ),
                    command.get(
                        "value",
                        ""
                    )
                ),
                tags=(str(index),)
            )


    # ========================================================
    # ADD VOICE
    # ========================================================

    def add_voice_command(self):

        result = self.voice_command_editor(
            "Add Voice Command"
        )

        if result is None:
            return

        self.settings[
            "VOICE_COMMANDS"
        ].append(
            result
        )

        if save_settings(
            self.settings
        ):

            self.refresh_voice_commands()


    # ========================================================
    # EDIT VOICE
    # ========================================================

    def edit_voice_command(self):

        if self.selected_voice_index is None:

            messagebox.showwarning(
                "Select Command",
                "Select a voice command first."
            )

            return

        commands = self.settings[
            "VOICE_COMMANDS"
        ]

        index = self.selected_voice_index

        if not (
            0 <= index < len(commands)
        ):
            return

        result = self.voice_command_editor(
            "Edit Voice Command",
            commands[index]
        )

        if result is None:
            return

        commands[index] = result

        if save_settings(
            self.settings
        ):

            self.refresh_voice_commands()


    # ========================================================
    # DELETE VOICE
    # ========================================================

    def delete_voice_command(self):

        if self.selected_voice_index is None:

            messagebox.showwarning(
                "Select Command",
                "Select a voice command first."
            )

            return

        if not messagebox.askyesno(
            "Delete Command",
            "Delete the selected voice command?"
        ):
            return

        index = self.selected_voice_index

        commands = self.settings[
            "VOICE_COMMANDS"
        ]

        if 0 <= index < len(commands):

            del commands[index]

        self.selected_voice_index = None

        if save_settings(
            self.settings
        ):

            self.refresh_voice_commands()


    # ========================================================
    # COMMAND EDITOR
    # ========================================================

    def command_editor(
        self,
        title,
        existing=None
    ):

        dialog = tk.Toplevel(
            self.root
        )

        dialog.title(
            title
        )

        dialog.geometry(
            "560x420"
        )

        dialog.configure(
            bg=BG
        )

        dialog.transient(
            self.root
        )

        dialog.grab_set()

        name_var = tk.StringVar(
            value=(
                existing.get(
                    "name",
                    ""
                )
                if existing
                else ""
            )
        )

        type_var = tk.StringVar(
            value=(
                existing.get(
                    "type",
                    ACTION_TYPES[0]
                )
                if existing
                else ACTION_TYPES[0]
            )
        )

        value_var = tk.StringVar(
            value=(
                existing.get(
                    "value",
                    ""
                )
                if existing
                else ""
            )
        )

        tk.Label(
            dialog,
            text="Command Name",
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 5)
        )

        name_entry = tk.Entry(
            dialog,
            textvariable=name_var,
            bg=PANEL_3,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat"
        )

        name_entry.pack(
            fill="x",
            padx=25,
            ipady=8
        )

        tk.Label(
            dialog,
            text="Action Type",
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=25,
            pady=(18, 5)
        )

        ttk.Combobox(
            dialog,
            textvariable=type_var,
            values=ACTION_TYPES,
            state="readonly"
        ).pack(
            fill="x",
            padx=25
        )

        tk.Label(
            dialog,
            text="Action Value",
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=25,
            pady=(18, 5)
        )

        tk.Entry(
            dialog,
            textvariable=value_var,
            bg=PANEL_3,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat"
        ).pack(
            fill="x",
            padx=25,
            ipady=8
        )

        tk.Label(
            dialog,
            text=(
                "Examples: Ctrl+C • Left Click • "
                "program.exe • https://example.com • Hello World"
            ),
            bg=BG,
            fg=TEXT_MUTED,
            wraplength=500
        ).pack(
            anchor="w",
            padx=25,
            pady=10
        )

        result = {
            "value": None
        }

        def accept():

            name = name_var.get().strip()

            action_type = (
                type_var.get().strip()
            )

            value = value_var.get().strip()

            if not name:

                messagebox.showwarning(
                    "Missing Name",
                    "Enter a command name.",
                    parent=dialog
                )

                return

            if not value:

                messagebox.showwarning(
                    "Missing Action",
                    "Enter an action value.",
                    parent=dialog
                )

                return

            result["value"] = {

                "name":
                    name,

                "type":
                    action_type,

                "value":
                    value
            }

            dialog.destroy()

        buttons = tk.Frame(
            dialog,
            bg=BG
        )

        buttons.pack(
            fill="x",
            padx=25,
            pady=20
        )

        ttk.Button(
            buttons,
            text="CANCEL",
            command=dialog.destroy
        ).pack(
            side="right",
            padx=4
        )

        ttk.Button(
            buttons,
            text="SAVE",
            style="Green.TButton",
            command=accept
        ).pack(
            side="right",
            padx=4
        )

        name_entry.focus_set()

        self.root.wait_window(
            dialog
        )

        return result["value"]


    # ========================================================
    # VOICE EDITOR
    # ========================================================

    def voice_command_editor(
        self,
        title,
        existing=None
    ):

        dialog = tk.Toplevel(
            self.root
        )

        dialog.title(
            title
        )

        dialog.geometry(
            "560x450"
        )

        dialog.configure(
            bg=BG
        )

        dialog.transient(
            self.root
        )

        dialog.grab_set()

        command_var = tk.StringVar(
            value=(
                existing.get(
                    "command",
                    ""
                )
                if existing
                else ""
            )
        )

        type_var = tk.StringVar(
            value=(
                existing.get(
                    "type",
                    ACTION_TYPES[0]
                )
                if existing
                else ACTION_TYPES[0]
            )
        )

        value_var = tk.StringVar(
            value=(
                existing.get(
                    "value",
                    ""
                )
                if existing
                else ""
            )
        )

        tk.Label(
            dialog,
            text="Voice Command",
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 5)
        )

        tk.Entry(
            dialog,
            textvariable=command_var,
            bg=PANEL_3,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat"
        ).pack(
            fill="x",
            padx=25,
            ipady=8
        )

        tk.Label(
            dialog,
            text="Action Type",
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=25,
            pady=(18, 5)
        )

        ttk.Combobox(
            dialog,
            textvariable=type_var,
            values=ACTION_TYPES,
            state="readonly"
        ).pack(
            fill="x",
            padx=25
        )

        tk.Label(
            dialog,
            text="Action",
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=25,
            pady=(18, 5)
        )

        tk.Entry(
            dialog,
            textvariable=value_var,
            bg=PANEL_3,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat"
        ).pack(
            fill="x",
            padx=25,
            ipady=8
        )

        result = {
            "value": None
        }

        def accept():

            command = (
                command_var.get()
                .strip()
            )

            action_type = (
                type_var.get()
                .strip()
            )

            value = (
                value_var.get()
                .strip()
            )

            if not command:

                messagebox.showwarning(
                    "Missing Command",
                    "Enter a voice command.",
                    parent=dialog
                )

                return

            if not value:

                messagebox.showwarning(
                    "Missing Action",
                    "Enter an action.",
                    parent=dialog
                )

                return

            result["value"] = {

                "command":
                    command,

                "type":
                    action_type,

                "value":
                    value
            }

            dialog.destroy()

        buttons = tk.Frame(
            dialog,
            bg=BG
        )

        buttons.pack(
            fill="x",
            padx=25,
            pady=15
        )

        ttk.Button(
            buttons,
            text="CANCEL",
            command=dialog.destroy
        ).pack(
            side="right",
            padx=4
        )

        ttk.Button(
            buttons,
            text="SAVE",
            style="Green.TButton",
            command=accept
        ).pack(
            side="right",
            padx=4
        )

        self.root.wait_window(
            dialog
        )

        return result["value"]


    # ========================================================
    # SYSTEM PAGE
    # ========================================================

    def build_system_page(self):

        page = tk.Frame(
            self.page_container,
            bg=BG
        )

        self.pages[
            "System"
        ] = page

        tk.Label(
            page,
            text="System",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 18, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            page,
            text="Program and process information.",
            bg=BG,
            fg=TEXT_MUTED
        ).pack(
            anchor="w",
            pady=(2, 15)
        )

        panel = self.create_panel(
            page,
            "Detected Programs"
        )

        panel.pack(
            fill="x"
        )

        self.program_labels = {}

        programs = [

            (
                "Camera Server",
                CAMERA_SERVER_FILE,
                CAMERA_SERVER_CANDIDATES
            ),

            (
                "AirMouse",
                AIRMOUSE_FILE,
                AIRMOUSE_CANDIDATES
            ),

            (
                "Blue Trackpad",
                BLUETRACKPAD_FILE,
                BLUETRACKPAD_CANDIDATES
            )
        ]

        for row, (
            name,
            preferred,
            candidates
        ) in enumerate(programs):

            tk.Label(
                panel,
                text=name,
                bg=PANEL,
                fg=TEXT
            ).grid(
                row=row + 1,
                column=0,
                sticky="w",
                padx=15,
                pady=9
            )

            label = tk.Label(
                panel,
                text="Checking...",
                bg=PANEL,
                fg=YELLOW
            )

            label.grid(
                row=row + 1,
                column=1,
                sticky="w",
                padx=10,
                pady=9
            )

            self.program_labels[
                name
            ] = label

        process_panel = self.create_panel(
            page,
            "Process Status"
        )

        process_panel.pack(
            fill="x",
            pady=15
        )

        self.process_status_labels = {}

        for row, name in enumerate([

            "CameraServer",
            "Air_Mouse",
            "Blue_virtual_Trackpad"

        ]):

            display_name = {

                "CameraServer":
                    "Camera Server",

                "Air_Mouse":
                    "AirMouse",

                "Blue_virtual_Trackpad":
                    "Blue Trackpad"
            }[name]

            tk.Label(
                process_panel,
                text=display_name,
                bg=PANEL,
                fg=TEXT
            ).grid(
                row=row + 1,
                column=0,
                sticky="w",
                padx=15,
                pady=8
            )

            label = tk.Label(
                process_panel,
                text="STOPPED",
                bg=PANEL,
                fg=RED
            )

            label.grid(
                row=row + 1,
                column=1,
                sticky="w",
                padx=10,
                pady=8
            )

            self.process_status_labels[
                name
            ] = label

        buttons = tk.Frame(
            page,
            bg=BG
        )

        buttons.pack(
            fill="x",
            pady=10
        )

        ttk.Button(
            buttons,
            text="REFRESH PROGRAMS",
            style="Blue.TButton",
            command=self.refresh_program_detection
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            buttons,
            text="START SYSTEM",
            style="Green.TButton",
            command=self.start_system
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            buttons,
            text="STOP SYSTEM",
            style="Red.TButton",
            command=self.stop_system
        ).pack(
            side="left",
            padx=4
        )

        tk.Label(
            page,
            text=(
                f"Application folder:\n{APP_DIR}"
            ),
            bg=BG,
            fg=TEXT_MUTED,
            justify="left",
            wraplength=850
        ).pack(
            anchor="w",
            pady=15
        )


    # ========================================================
    # PROGRAM DETECTION
    # ========================================================

    def refresh_program_detection(self):

        programs = [

            (
                "Camera Server",
                CAMERA_SERVER_FILE,
                CAMERA_SERVER_CANDIDATES
            ),

            (
                "AirMouse",
                AIRMOUSE_FILE,
                AIRMOUSE_CANDIDATES
            ),

            (
                "Blue Trackpad",
                BLUETRACKPAD_FILE,
                BLUETRACKPAD_CANDIDATES
            )
        ]

        for name, preferred, candidates in programs:

            path = find_program(
                preferred,
                candidates
            )

            label = self.program_labels.get(
                name
            )

            if label is None:
                continue

            if path:

                label.configure(
                    text=path,
                    fg=GREEN
                )

            else:

                if getattr(
                    sys,
                    "frozen",
                    False
                ):

                    expected = {

                        "Camera Server":
                            "camera_server.exe",

                        "AirMouse":
                            "air_mouse.exe",

                        "Blue Trackpad":
                            "blue_virtual_trackpad.exe"

                    }.get(
                        name,
                        "EXE"
                    )

                else:

                    expected = preferred

                label.configure(
                    text=(
                        f"NOT FOUND — expected {expected}"
                    ),
                    fg=RED
                )


    # ========================================================
    # CREATE CHILD PROCESS
    # ========================================================

    def launch_child(
        self,
        path
    ):

        frozen = getattr(
            sys,
            "frozen",
            False
        )

        if frozen:

            command = [
                path
            ]

        else:

            command = [
                sys.executable,
                path
            ]

        creationflags = 0

        startupinfo = None

        if os.name == "nt":

            creationflags = (
                subprocess.CREATE_NEW_PROCESS_GROUP
                |
                subprocess.CREATE_NO_WINDOW
            )

        process = subprocess.Popen(

            command,

            cwd=APP_DIR,

            stdin=subprocess.DEVNULL,

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL,

            creationflags=creationflags,

            startupinfo=startupinfo
        )

        return process


    # ========================================================
    # START SYSTEM
    # ========================================================

    def start_system(self):

        if self.running:
            return

        programs = [

            (
                "CameraServer",
                "Camera Server",
                CAMERA_SERVER_FILE,
                CAMERA_SERVER_CANDIDATES
            ),

            (
                "Air_Mouse",
                "AirMouse",
                AIRMOUSE_FILE,
                AIRMOUSE_CANDIDATES
            ),

            (
                "Blue_virtual_Trackpad",
                "Blue Trackpad",
                BLUETRACKPAD_FILE,
                BLUETRACKPAD_CANDIDATES
            )
        ]

        self.processes.clear()

        started = []

        # ----------------------------------------------------
        # Locate every program BEFORE starting anything.
        # ----------------------------------------------------

        located = []

        for (
            process_name,
            display_name,
            preferred,
            candidates
        ) in programs:

            path = find_program(
                preferred,
                candidates
            )

            if not path:

                messagebox.showerror(
                    "Program Not Found",
                    f"{display_name} could not be found.\n\n"
                    f"Expected:\n{preferred}\n\n"
                    f"Application folder:\n{APP_DIR}"
                )

                return

            located.append(
                (
                    process_name,
                    display_name,
                    path
                )
            )

        # ----------------------------------------------------
        # Start programs.
        # ----------------------------------------------------

        for (
            process_name,
            display_name,
            path
        ) in located:

            try:

                process = self.launch_child(
                    path
                )

                self.processes[
                    process_name
                ] = process

                started.append(
                    display_name
                )

                # ------------------------------------------------
                # Check immediately whether the program died.
                # ------------------------------------------------

                self.root.after(
                    500,
                    lambda p=process,
                    n=display_name:
                        self.check_child_startup(
                            p,
                            n
                        )
                )

            except Exception as error:

                self.stop_system(
                    show_message=False
                )

                messagebox.showerror(
                    "Startup Error",
                    f"Could not start {display_name}.\n\n"
                    f"File:\n{path}\n\n"
                    f"Error:\n{error}"
                )

                return

        if len(started) == len(programs):

            self.running = True

            self.status_label.configure(
                text="● RUNNING (3/3)",
                fg=GREEN
            )

            return


    # ========================================================
    # CHECK CHILD STARTUP
    # ========================================================

    def check_child_startup(
        self,
        process,
        display_name
    ):

        try:

            return_code = process.poll()

            if return_code is not None:

                self.running = False

                # Find internal process name.
                process_name = None

                for name, p in self.processes.items():

                    if p is process:

                        process_name = name
                        break

                if process_name:

                    self.processes.pop(
                        process_name,
                        None
                    )

                self.refresh_process_status()

                messagebox.showerror(
                    "Program Stopped",
                    f"{display_name} started but then stopped.\n\n"
                    f"Exit code: {return_code}\n\n"
                    "The child program may have an error."
                )

        except Exception:
            pass


    # ========================================================
    # STOP SYSTEM
    # ========================================================

    def stop_system(
        self,
        show_message=False
    ):

        self.running = False

        processes = list(
            self.processes.items()
        )

        for name, process in processes:

            try:

                if process.poll() is None:

                    if os.name == "nt":

                        subprocess.run(

                            [
                                "taskkill",
                                "/PID",
                                str(process.pid),
                                "/T",
                                "/F"
                            ],

                            stdout=subprocess.DEVNULL,

                            stderr=subprocess.DEVNULL,

                            creationflags=(
                                subprocess.CREATE_NO_WINDOW
                            )
                        )

                    else:

                        process.terminate()

            except Exception:
                pass

        for name, process in processes:

            try:

                process.wait(
                    timeout=2
                )

            except Exception:
                pass

        for name, process in processes:

            try:

                if process.poll() is None:

                    process.kill()

            except Exception:
                pass

        self.processes.clear()

        self.status_label.configure(
            text="● STOPPED",
            fg=RED
        )

        self.refresh_process_status()

        if show_message:

            messagebox.showinfo(
                "System Stopped",
                "All AirMouse programs have been stopped."
            )


    # ========================================================
    # PROCESS STATUS
    # ========================================================

    def refresh_process_status(self):

        dead = []

        for name, process in self.processes.items():

            if process.poll() is not None:

                dead.append(
                    name
                )

        for name in dead:

            self.processes.pop(
                name,
                None
            )

        for name, label in self.process_status_labels.items():

            process = self.processes.get(
                name
            )

            if process is not None:

                if process.poll() is None:

                    label.configure(
                        text=(
                            f"RUNNING — PID {process.pid}"
                        ),
                        fg=GREEN
                    )

                else:

                    label.configure(
                        text="STOPPED",
                        fg=RED
                    )

            else:

                label.configure(
                    text="STOPPED",
                    fg=RED
                )

        if self.running:

            count = len(
                self.processes
            )

            if count == 3:

                self.status_label.configure(
                    text="● RUNNING (3/3)",
                    fg=GREEN
                )

            elif count > 0:

                self.status_label.configure(
                    text=f"● RUNNING ({count}/3)",
                    fg=YELLOW
                )

            else:

                self.running = False

                self.status_label.configure(
                    text="● STOPPED",
                    fg=RED
                )

        if self.root.winfo_exists():

            self.process_monitor_job = self.root.after(
                1000,
                self.refresh_process_status
            )


    # ========================================================
    # CLOSE
    # ========================================================

    def on_close(self):

        if self.processes:

            answer = messagebox.askyesno(
                "Exit",
                "Stop all running programs and exit?"
            )

            if not answer:
                return

        self.stop_system(
            show_message=False
        )

        if self.process_monitor_job:

            try:

                self.root.after_cancel(
                    self.process_monitor_job
                )

            except Exception:
                pass

        self.root.destroy()


# ============================================================
# START APPLICATION
# ============================================================

def main():

    root = tk.Tk()

    # --------------------------------------------------------
    # Use AirMouseLauncher.ico
    # --------------------------------------------------------

    if os.path.isfile(
        ICON_FILE
    ):

        try:

            root.iconbitmap(
                ICON_FILE
            )

        except Exception:
            pass

    app = AirMouseApp(
        root
    )

    root.mainloop()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()