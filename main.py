# Standard library imports
import os
from pathlib import Path
from functools import partial

# Third-party library imports
from PyQt6_SwitchControl import SwitchControl
from PyQt6 import QtCore
from PyQt6.QtGui import QDesktopServices, QCursor, QPainter, QPen, QBrush, QColor, QPainterPath, QFontDatabase, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QStackedWidget,
    QAbstractItemView,
    QMenu,
    QInputDialog,
    QLabel,
    QPushButton,
    QTextEdit,
    QComboBox,
    QScrollBar,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QSizeGrip,
    QFileIconProvider,
    QWIDGETSIZE_MAX
)

# Local imports
from TitleBar import TitleBar
from SideGrip import SideGrip

# Resolves to either root project directory or to temp folder
BUNDLE_DIR = Path(__file__).resolve().parent

THEMES_DIR = BUNDLE_DIR / "themes"
ICONS_DIR = BUNDLE_DIR / "icons"


# Manager class
class Manager(QWidget):
    _grip_size = 10

    # Constructor
    def __init__(self):
        super().__init__()

        # Sub-folder for themes
        self.themes = os.path.join(os.path.dirname(__file__), "themes")

        # Theme variables
        self.default_theme = os.path.join(self.themes, "default.qss")
        self.dark_theme = os.path.join(self.themes, "dark.qss")
        self.light_theme = os.path.join(self.themes, "light.qss")

        # Set default theme on startup
        self.theme = self.default_theme
        self.color = "#343642"
        self.style_sheet()

        # Default window settings
        self.window_default()
        self.container.paintEvent = self.container_paint_event

        # Store new title bar object in instance variable
        self.title_bar = TitleBar(self)

        # Sub-folder for icons
        self.icons = os.path.join(os.path.dirname(__file__), "icons")

        # Icon variables
        self.folders_icon = QIcon(os.path.join(self.icons, "folders.png"))
        self.files_icon = QIcon(os.path.join(self.icons, "files.png"))
        self.apps_icon = QIcon(os.path.join(self.icons, "apps.png"))
        self.home_icon = QIcon(os.path.join(self.icons, "home.png"))
        self.settings_icon = QIcon(os.path.join(self.icons, "settings.png"))
        self.add_icon = QIcon(os.path.join(self.icons, "add.png"))

        self.min_icon = QIcon(os.path.join(self.icons, "min.png"))
        self.max_icon = QIcon(os.path.join(self.icons, "max.png"))
        self.close_icon = QIcon(os.path.join(self.icons, "close.png"))
        self.normal_icon = QIcon(os.path.join(self.icons, "normal.png"))

        self.min_icon_light = QIcon(os.path.join(self.icons, "min (light theme).png"))
        self.max_icon_light = QIcon(os.path.join(self.icons, "max (light theme).png"))
        self.close_icon_light = QIcon(os.path.join(self.icons, "close (light theme).png"))
        self.normal_icon_light = QIcon(os.path.join(self.icons, "normal (light theme).png"))

        # Layout for button text
        self.button_layout = QGridLayout()

        # Add font
        QFontDatabase.addApplicationFont("arialroundedmtbold.ttf")

        # Create pages
        self.page1 = QWidget()
        self.page2 = QWidget()
        self.page3 = QWidget()
        self.page4 = QWidget()
        self.page5 = QWidget()

        self.home()
        self.folder_page()
        self.file_page()
        self.app_page()
        self.settings_page()

        self.stack = QStackedWidget()

        self.stack.currentChanged.connect(self.on_page_change)

        # Add pages to stack
        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.stack.addWidget(self.page3)
        self.stack.addWidget(self.page4)
        self.stack.addWidget(self.page5)

        # Main layout
        self.inner_layout.addWidget(self.title_bar)
        self.inner_layout.addWidget(self.stack)

        self.widget_events()

        # Set grips for window resizing
        self.sideGrips = [
            SideGrip(self.container, QtCore.Qt.Edge.LeftEdge),
            SideGrip(self.container, QtCore.Qt.Edge.TopEdge),
            SideGrip(self.container, QtCore.Qt.Edge.RightEdge),
            SideGrip(self.container, QtCore.Qt.Edge.BottomEdge),
        ]

        self.cornerGrips = [QSizeGrip(self.container) for _ in range(4)]

        # Restore settings from previous session
        self.settings = QtCore.QSettings("Lucas Torres", "Fileon")
        self.read_settings()

    # Home page
    def home(self):
        # Home page folder list
        folder_label = QLabel("Folders")
        folder_label.setObjectName("Title")

        h_folder_list = QListWidget()
        h_folder_list.setIconSize(QtCore.QSize(32, 32))
        h_folder_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        h_folder_scroll = QScrollBar()
        h_folder_scroll.setVisible(True)
        h_folder_list.setVerticalScrollBar(h_folder_scroll)
        h_folder_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # Home page file list
        file_label = QLabel("Files")
        file_label.setObjectName("Title")

        h_file_list = QListWidget()
        h_file_list.setIconSize(QtCore.QSize(32, 32))
        h_file_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        h_file_scroll = QScrollBar()
        h_file_scroll.setVisible(True)
        h_file_list.setVerticalScrollBar(h_file_scroll)
        h_file_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # Home page app list
        app_label = QLabel("Apps")
        app_label.setObjectName("Title")

        h_app_list = QListWidget()
        h_app_list.setIconSize(QtCore.QSize(26, 26))
        h_app_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        h_app_scroll = QScrollBar()
        h_app_scroll.setVisible(True)
        h_app_list.setVerticalScrollBar(h_app_scroll)
        h_app_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # Home page: Manage folders button
        folders1_label = QLabel("Folders")
        folders1_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        folders1_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        manage_folders1 = QPushButton()
        manage_folders1.setIcon(self.folders_icon)
        manage_folders1.setIconSize(QtCore.QSize(26, 26))
        manage_folders1.setFixedHeight(60)
        manage_folders1.setMinimumWidth(140)

        manage_folders1.setLayout(QGridLayout())
        folders1_layout = manage_folders1.layout()
        folders1_layout.addWidget(folders1_label)
        self.button_layout.addWidget(manage_folders1)

        # Home page: Manage files button
        files1_label = QLabel("Files")
        files1_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        files1_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        manage_files1 = QPushButton()
        manage_files1.setIcon(self.files_icon)
        manage_files1.setIconSize(QtCore.QSize(26, 26))
        manage_files1.setFixedHeight(60)
        manage_files1.setMinimumWidth(140)

        manage_files1.setLayout(QGridLayout())
        files1_layout = manage_files1.layout()
        files1_layout.addWidget(files1_label)
        self.button_layout.addWidget(manage_files1)

        # Home page: Manage apps button
        apps1_label = QLabel("Apps")
        apps1_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        apps1_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        manage_apps1 = QPushButton()
        manage_apps1.setIcon(self.apps_icon)
        manage_apps1.setIconSize(QtCore.QSize(26, 26))
        manage_apps1.setFixedHeight(60)
        manage_apps1.setMinimumWidth(140)

        manage_apps1.setLayout(QGridLayout())
        apps1_layout = manage_apps1.layout()
        apps1_layout.addWidget(apps1_label)
        self.button_layout.addWidget(manage_apps1)

        # Home page: Settings button
        settings1_label = QLabel("Settings")
        settings1_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        settings1_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        settings1 = QPushButton()
        settings1.setIcon(self.settings_icon)
        settings1.setIconSize(QtCore.QSize(26, 26))
        settings1.setFixedHeight(60)
        settings1.setMinimumWidth(140)

        settings1.setLayout(QGridLayout())
        settings1_layout = settings1.layout()
        settings1_layout.addWidget(settings1_label)
        self.button_layout.addWidget(settings1)

        # Directory display
        show_dir1 = QTextEdit()
        show_dir1.setReadOnly(True)

        # References for use elsewhere
        self.h_folder_list = h_folder_list
        self.h_file_list = h_file_list
        self.h_app_list = h_app_list
        self.manage_folders1 = manage_folders1
        self.manage_files1 = manage_files1
        self.manage_apps1 = manage_apps1
        self.settings1 = settings1
        self.show_dir1 = show_dir1

        # Manage layout for widgets
        master_row = QHBoxLayout()

        # Folder section
        folder_col = QVBoxLayout()
        header1 = QHBoxLayout()
        folder_row = QHBoxLayout()

        scroll1_col = QVBoxLayout()
        list1_col = QVBoxLayout()

        # File section
        file_col = QVBoxLayout()
        header2 = QHBoxLayout()
        file_row = QHBoxLayout()

        scroll2_col = QVBoxLayout()
        list2_col = QVBoxLayout()

        # App section
        app_col = QVBoxLayout()
        header3 = QHBoxLayout()
        app_row = QHBoxLayout()

        scroll3_col = QVBoxLayout()
        list3_col = QVBoxLayout()

        # Last column
        button_col = QVBoxLayout()
        spacer = QHBoxLayout()
        button_row = QVBoxLayout()

        # Set spacing and margins
        header1.setContentsMargins(8, 0, 0, 0)
        scroll1_col.setSpacing(8)
        scroll1_col.setContentsMargins(8, 30, 0, 10)
        list1_col.setSpacing(8)
        list1_col.setContentsMargins(3, 30, 12, 10)

        scroll2_col.setSpacing(8)
        scroll2_col.setContentsMargins(0, 30, 0, 10)
        list2_col.setSpacing(8)
        list2_col.setContentsMargins(3, 30, 12, 10)

        scroll3_col.setSpacing(8)
        scroll3_col.setContentsMargins(0, 30, 0, 10)
        list3_col.setSpacing(8)
        list3_col.setContentsMargins(3, 30, 12, 10)

        button_col.setSpacing(8)
        button_col.setContentsMargins(6, 6, 6, 6)

        # Add widgets to folder section
        header1.addWidget(folder_label)

        scroll1_col.addWidget(h_folder_scroll)
        list1_col.addWidget(h_folder_list)
        folder_row.addLayout(scroll1_col)
        folder_row.addLayout(list1_col)

        folder_col.addLayout(header1, 10)
        folder_col.addLayout(folder_row, 90)

        # Add widgets to file section
        header2.addWidget(file_label)

        scroll2_col.addWidget(h_file_scroll)
        list2_col.addWidget(h_file_list)
        file_row.addLayout(scroll2_col)
        file_row.addLayout(list2_col)

        file_col.addLayout(header2, 10)
        file_col.addLayout(file_row, 90)

        # Add widgets to app section
        header3.addWidget(app_label)

        scroll3_col.addWidget(h_app_scroll)
        list3_col.addWidget(h_app_list)
        app_row.addLayout(scroll3_col)
        app_row.addLayout(list3_col)

        app_col.addLayout(header3, 10)
        app_col.addLayout(app_row, 90)

        # Add widgets to last column
        button_row.addWidget(show_dir1)
        button_row.addWidget(manage_folders1)
        button_row.addWidget(manage_files1)
        button_row.addWidget(manage_apps1)
        button_row.addWidget(settings1)

        button_col.addLayout(spacer, 10)
        button_col.addLayout(button_row, 90)

        # Add columns to main layout
        master_row.addStretch(1)
        master_row.addLayout(folder_col, 26)
        master_row.addLayout(file_col, 26)
        master_row.addLayout(app_col, 26)
        master_row.addLayout(button_col, 10)

        self.page1.setLayout(master_row)

    # Add/remove and sort folders
    def folder_page(self):
        # Folder list
        folder_label = QLabel("Folders")
        folder_label.setObjectName("Title")

        folder_list = QListWidget()
        folder_list.setIconSize(QtCore.QSize(32, 32))
        folder_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        folder_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        folder_scroll = QScrollBar()
        folder_scroll.setVisible(True)
        folder_list.setVerticalScrollBar(folder_scroll)
        folder_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # Folder page: Add folders button
        add_folders_label = QLabel("Add folders")
        add_folders_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        add_folders_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        add_folders = QPushButton()
        add_folders.setIcon(self.add_icon)
        add_folders.setIconSize(QtCore.QSize(26, 26))
        add_folders.setFixedHeight(60)
        add_folders.setMinimumWidth(170)

        add_folders.setLayout(QGridLayout())
        add_folders_layout = add_folders.layout()
        add_folders_layout.addWidget(add_folders_label)
        self.button_layout.addWidget(add_folders)

        # Folder page: Manage files button
        files2_label = QLabel("Files")
        files2_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        files2_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        manage_files2 = QPushButton()
        manage_files2.setIcon(self.files_icon)
        manage_files2.setIconSize(QtCore.QSize(26, 26))
        manage_files2.setFixedHeight(60)
        manage_files2.setMinimumWidth(170)

        manage_files2.setLayout(QGridLayout())
        files2_layout = manage_files2.layout()
        files2_layout.addWidget(files2_label)
        self.button_layout.addWidget(manage_files2)

        # Folder page: Manage apps button
        apps2_label = QLabel("Apps")
        apps2_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        apps2_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        manage_apps2 = QPushButton()
        manage_apps2.setIcon(self.apps_icon)
        manage_apps2.setIconSize(QtCore.QSize(26, 26))
        manage_apps2.setFixedHeight(60)
        manage_apps2.setMinimumWidth(170)

        manage_apps2.setLayout(QGridLayout())
        apps2_layout = manage_apps2.layout()
        apps2_layout.addWidget(apps2_label)
        self.button_layout.addWidget(manage_apps2)

        # Folder page: Home menu button
        home_menu1 = QPushButton()
        home_menu1.setObjectName("No-Label")
        home_menu1.setIcon(self.home_icon)
        home_menu1.setIconSize(QtCore.QSize(30, 30))
        home_menu1.setFixedHeight(60)

        # Folder page: Settings button
        settings2 = QPushButton()
        settings2.setObjectName("No-Label")
        settings2.setIcon(self.settings_icon)
        settings2.setIconSize(QtCore.QSize(26, 26))
        settings2.setFixedHeight(60)

        # Directory display
        show_dir2 = QTextEdit()
        show_dir2.setReadOnly(True)

        # References for use elsewhere
        self.folder_list = folder_list
        self.add_folders = add_folders
        self.manage_files2 = manage_files2
        self.manage_apps2 = manage_apps2
        self.home_menu1 = home_menu1
        self.settings2 = settings2
        self.show_dir2 = show_dir2

        # Manage layout for widgets
        master_row = QHBoxLayout()
        master_row.setContentsMargins(9, 9, 0, 9)

        # Folder list section
        folder_col = QVBoxLayout()
        header = QHBoxLayout()
        folder_row = QHBoxLayout()

        scroll_col = QVBoxLayout()
        list_col = QVBoxLayout()

        # Button section
        button_section = QVBoxLayout()
        spacer = QHBoxLayout()
        button_col = QVBoxLayout()
        button_row = QHBoxLayout()

        # Set spacing and margins
        header.setContentsMargins(8, 0, 0, 0)
        scroll_col.setSpacing(8)
        scroll_col.setContentsMargins(8, 30, 0, 10)
        list_col.setSpacing(8)
        list_col.setContentsMargins(3, 30, 12, 10)

        button_section.setSpacing(8)
        button_section.setContentsMargins(6, 6, 15, 6)

        # Add widgets to folder list section
        header.addWidget(folder_label)

        scroll_col.addWidget(folder_scroll)
        list_col.addWidget(folder_list)
        folder_row.addLayout(scroll_col)
        folder_row.addLayout(list_col)

        folder_col.addLayout(header, 10)
        folder_col.addLayout(folder_row, 90)

        # Add widgets to button section
        button_col.addWidget(show_dir2)
        button_col.addWidget(add_folders)
        button_col.addWidget(manage_files2)
        button_col.addWidget(manage_apps2)

        button_row.addWidget(home_menu1)
        button_row.addWidget(settings2)

        button_col.addLayout(button_row)

        button_section.addLayout(spacer, 10)
        button_section.addLayout(button_col, 90)

        # Add columns to main layout
        master_row.addStretch(1)
        master_row.addLayout(folder_col, 68)
        master_row.addLayout(button_section, 20)

        self.page2.setLayout(master_row)

    # Add/remove and sort files
    def file_page(self):
        # File list
        file_label = QLabel("Files")
        file_label.setObjectName("Title")

        file_list = QListWidget()
        file_list.setIconSize(QtCore.QSize(32, 32))
        file_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        file_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        file_scroll = QScrollBar()
        file_scroll.setVisible(True)
        file_list.setVerticalScrollBar(file_scroll)
        file_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # File page: Add files button
        add_files_label = QLabel("Add files")
        add_files_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        add_files_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        add_files = QPushButton()
        add_files.setIcon(self.add_icon)
        add_files.setIconSize(QtCore.QSize(26, 26))
        add_files.setFixedHeight(60)
        add_files.setMinimumWidth(170)

        add_files.setLayout(QGridLayout())
        add_files_layout = add_files.layout()
        add_files_layout.addWidget(add_files_label)
        self.button_layout.addWidget(add_files)

        # File page: Manage folders button
        folders2_label = QLabel("Folders")
        folders2_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        folders2_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        manage_folders2 = QPushButton()
        manage_folders2.setIcon(self.folders_icon)
        manage_folders2.setIconSize(QtCore.QSize(26, 26))
        manage_folders2.setFixedHeight(60)
        manage_folders2.setMinimumWidth(170)

        manage_folders2.setLayout(QGridLayout())
        folders2_layout = manage_folders2.layout()
        folders2_layout.addWidget(folders2_label)
        self.button_layout.addWidget(manage_folders2)

        # File page: Manage apps button
        apps3_label = QLabel("Apps")
        apps3_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        apps3_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        manage_apps3 = QPushButton()
        manage_apps3.setIcon(self.apps_icon)
        manage_apps3.setIconSize(QtCore.QSize(26, 26))
        manage_apps3.setFixedHeight(60)
        manage_apps3.setMinimumWidth(170)

        manage_apps3.setLayout(QGridLayout())
        apps3_layout = manage_apps3.layout()
        apps3_layout.addWidget(apps3_label)
        self.button_layout.addWidget(manage_apps3)

        # File page: Home menu button
        home_menu2 = QPushButton()
        home_menu2.setObjectName("No-Label")
        home_menu2.setIcon(self.home_icon)
        home_menu2.setIconSize(QtCore.QSize(30, 30))
        home_menu2.setFixedHeight(60)

        # File page: Settings button
        settings3 = QPushButton()
        settings3.setObjectName("No-Label")
        settings3.setIcon(self.settings_icon)
        settings3.setIconSize(QtCore.QSize(26, 26))
        settings3.setFixedHeight(60)

        # Directory display
        show_dir3 = QTextEdit()
        show_dir3.setReadOnly(True)

        # References for use elsewhere
        self.file_list = file_list
        self.add_files = add_files
        self.manage_folders2 = manage_folders2
        self.manage_apps3 = manage_apps3
        self.home_menu2 = home_menu2
        self.settings3 = settings3
        self.show_dir3 = show_dir3

        # Manage layout for widgets
        master_row = QHBoxLayout()
        master_row.setContentsMargins(9, 9, 0, 9)

        # Folder list section
        file_col = QVBoxLayout()
        header = QHBoxLayout()
        file_row = QHBoxLayout()

        scroll_col = QVBoxLayout()
        list_col = QVBoxLayout()

        # Button section
        button_section = QVBoxLayout()
        spacer = QHBoxLayout()
        button_col = QVBoxLayout()
        button_row = QHBoxLayout()

        # Set spacing and margins
        header.setContentsMargins(8, 0, 0, 0)
        scroll_col.setSpacing(8)
        scroll_col.setContentsMargins(8, 30, 0, 10)
        list_col.setSpacing(8)
        list_col.setContentsMargins(3, 30, 12, 10)

        button_section.setSpacing(8)
        button_section.setContentsMargins(6, 6, 15, 6)

        # Add widgets to folder list section
        header.addWidget(file_label)

        scroll_col.addWidget(file_scroll)
        list_col.addWidget(file_list)
        file_row.addLayout(scroll_col)
        file_row.addLayout(list_col)

        file_col.addLayout(header, 10)
        file_col.addLayout(file_row, 90)

        # Add widgets to button section
        button_col.addWidget(show_dir3)
        button_col.addWidget(add_files)
        button_col.addWidget(manage_folders2)
        button_col.addWidget(manage_apps3)

        button_row.addWidget(home_menu2)
        button_row.addWidget(settings3)

        button_col.addLayout(button_row)

        button_section.addLayout(spacer, 10)
        button_section.addLayout(button_col, 90)

        # Add columns to main layout
        master_row.addStretch(1)
        master_row.addLayout(file_col, 68)
        master_row.addLayout(button_section, 20)

        self.page3.setLayout(master_row)

    # Add/remove and sort apps
    def app_page(self):
        # App list
        app_label = QLabel("Apps")
        app_label.setObjectName("Title")

        app_list = QListWidget()
        app_list.setIconSize(QtCore.QSize(26, 26))
        app_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        app_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        app_scroll = QScrollBar()
        app_scroll.setVisible(True)
        app_list.setVerticalScrollBar(app_scroll)
        app_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # App page: Add apps button
        add_apps_label = QLabel("Add apps")
        add_apps_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        add_apps_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        add_apps = QPushButton()
        add_apps.setIcon(self.add_icon)
        add_apps.setIconSize(QtCore.QSize(26, 26))
        add_apps.setFixedHeight(60)
        add_apps.setMinimumWidth(170)

        add_apps.setLayout(QGridLayout())
        add_apps_layout = add_apps.layout()
        add_apps_layout.addWidget(add_apps_label)
        self.button_layout.addWidget(add_apps)

        # App page: Manage folders button
        folders3_label = QLabel("Folders")
        folders3_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        folders3_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        manage_folders3 = QPushButton()
        manage_folders3.setIcon(self.folders_icon)
        manage_folders3.setIconSize(QtCore.QSize(26, 26))
        manage_folders3.setFixedHeight(60)
        manage_folders3.setMinimumWidth(170)

        manage_folders3.setLayout(QGridLayout())
        folders3_layout = manage_folders3.layout()
        folders3_layout.addWidget(folders3_label)
        self.button_layout.addWidget(manage_folders3)

        # App page: Manage files button
        files3_label = QLabel("Files")
        files3_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        files3_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        manage_files3 = QPushButton()
        manage_files3.setIcon(self.files_icon)
        manage_files3.setIconSize(QtCore.QSize(26, 26))
        manage_files3.setFixedHeight(60)
        manage_files3.setMinimumWidth(170)

        manage_files3.setLayout(QGridLayout())
        files2_layout = manage_files3.layout()
        files2_layout.addWidget(files3_label)
        self.button_layout.addWidget(manage_files3)

        # App page: Home menu button
        home_menu3 = QPushButton()
        home_menu3.setObjectName("No-Label")
        home_menu3.setIcon(self.home_icon)
        home_menu3.setIconSize(QtCore.QSize(30, 30))
        home_menu3.setFixedHeight(60)

        # App page: Settings button
        settings4 = QPushButton()
        settings4.setObjectName("No-Label")
        settings4.setIcon(self.settings_icon)
        settings4.setIconSize(QtCore.QSize(26, 26))
        settings4.setFixedHeight(60)

        # Directory display
        show_dir4 = QTextEdit()
        show_dir4.setReadOnly(True)

        # References for use elsewhere
        self.app_list = app_list
        self.add_apps = add_apps
        self.manage_folders3 = manage_folders3
        self.manage_files3 = manage_files3
        self.home_menu3 = home_menu3
        self.settings4 = settings4
        self.show_dir4 = show_dir4

        # Manage layout for widgets
        master_row = QHBoxLayout()
        master_row.setContentsMargins(9, 9, 0, 9)

        # Folder list section
        app_col = QVBoxLayout()
        header = QHBoxLayout()
        app_row = QHBoxLayout()

        scroll_col = QVBoxLayout()
        list_col = QVBoxLayout()

        # Button section
        button_section = QVBoxLayout()
        spacer = QHBoxLayout()
        button_col = QVBoxLayout()
        button_row = QHBoxLayout()

        # Set spacing and margins for columns and rows
        header.setContentsMargins(8, 0, 0, 0)
        scroll_col.setSpacing(8)
        scroll_col.setContentsMargins(8, 30, 0, 10)
        list_col.setSpacing(8)
        list_col.setContentsMargins(3, 30, 12, 10)

        button_section.setSpacing(8)
        button_section.setContentsMargins(6, 6, 15, 6)

        # Add widgets to folder list section
        header.addWidget(app_label)

        scroll_col.addWidget(app_scroll)
        list_col.addWidget(app_list)
        app_row.addLayout(scroll_col)
        app_row.addLayout(list_col)

        app_col.addLayout(header, 10)
        app_col.addLayout(app_row, 90)

        # Add widgets to button section
        button_col.addWidget(show_dir4)
        button_col.addWidget(add_apps)
        button_col.addWidget(manage_folders3)
        button_col.addWidget(manage_files3)

        button_row.addWidget(home_menu3)
        button_row.addWidget(settings4)

        button_col.addLayout(button_row)

        button_section.addLayout(spacer, 10)
        button_section.addLayout(button_col, 90)

        # Add columns to main layout
        master_row.addStretch(1)
        master_row.addLayout(app_col, 68)
        master_row.addLayout(button_section, 20)

        self.page4.setLayout(master_row)

    # Settings page
    def settings_page(self):
        settings_label = QLabel("Settings")
        settings_label.setObjectName("Title")

        # General settings
        general_label = QLabel("General")
        general_label.setObjectName("Description")

        directory_toggle_label = QLabel("Show Directory")
        directory_toggle_label.setObjectName("Description")

        directory_toggle = SwitchControl(bg_color="#51587a", circle_color="#DDD", active_color="#7285e0",
                                         animation_curve=QtCore.QEasingCurve.Type.InOutCubic,
                                         animation_duration=175,
                                         checked=True, change_cursor=False)

        fixed_window_size_label = QLabel("Fixed Window Size")
        fixed_window_size_label.setObjectName("Description")

        fixed_window_size = SwitchControl(bg_color="#51587a", circle_color="#DDD", active_color="#7285e0",
                                          animation_curve=QtCore.QEasingCurve.Type.InOutCubic,
                                          animation_duration=175,
                                          checked=False, change_cursor=False)

        window_size_label = QLabel("Change Window Size")
        window_size_label.setObjectName("Description")
        window_size = QComboBox()
        window_size.setFixedSize(90, 30)
        window_size.setEnabled(False)

        window_size.addItem("1280 × 720")
        window_size.addItem("1200 × 600")
        window_size.addItem("1000 × 660")
        window_size.addItem("800 × 550")
        window_size.addItem("700 × 500")

        # Theme settings
        theme_label = QLabel("Theme")
        theme_label.setObjectName("Description")
        change_theme = QComboBox()

        change_theme.addItem("Default")
        change_theme.addItem("Dark")
        change_theme.addItem("Light")

        # Settings page: Manage folders button
        folders4_label = QLabel("Folders")
        folders4_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        folders4_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        manage_folders4 = QPushButton()
        manage_folders4.setIcon(self.folders_icon)
        manage_folders4.setIconSize(QtCore.QSize(26, 26))
        manage_folders4.setFixedSize(200, 60)

        manage_folders4.setLayout(QGridLayout())
        folders3_layout = manage_folders4.layout()
        folders3_layout.addWidget(folders4_label)
        self.button_layout.addWidget(manage_folders4)

        # Settings page: Manage files button
        files4_label = QLabel("Files")
        files4_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        files4_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        manage_files4 = QPushButton()
        manage_files4.setIcon(self.files_icon)
        manage_files4.setIconSize(QtCore.QSize(26, 26))
        manage_files4.setFixedSize(200, 60)

        manage_files4.setLayout(QGridLayout())
        folders3_layout = manage_files4.layout()
        folders3_layout.addWidget(files4_label)
        self.button_layout.addWidget(manage_files4)

        # Settings page: Manage apps button
        apps4_label = QLabel("Apps")
        apps4_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        apps4_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        manage_apps4 = QPushButton()
        manage_apps4.setIcon(self.apps_icon)
        manage_apps4.setIconSize(QtCore.QSize(26, 26))
        manage_apps4.setFixedSize(200, 60)

        manage_apps4.setLayout(QGridLayout())
        folders3_layout = manage_apps4.layout()
        folders3_layout.addWidget(apps4_label)
        self.button_layout.addWidget(manage_apps4)

        # Settings page: home menu button
        home4_label = QLabel("Home")
        home4_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        home4_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, 1)

        home_menu4 = QPushButton()
        home_menu4.setIcon(self.home_icon)
        home_menu4.setIconSize(QtCore.QSize(26, 26))
        home_menu4.setFixedSize(200, 60)

        home_menu4.setLayout(QGridLayout())
        folders3_layout = home_menu4.layout()
        folders3_layout.addWidget(home4_label)
        self.button_layout.addWidget(home_menu4)

        # References for use elsewhere
        self.directory_toggle = directory_toggle
        self.fixed_window_size = fixed_window_size
        self.window_size = window_size
        self.change_theme = change_theme
        self.manage_folders4 = manage_folders4
        self.manage_files4 = manage_files4
        self.manage_apps4 = manage_apps4
        self.home_menu4 = home_menu4

        # Manage layout for widgets
        master_row = QHBoxLayout()
        master_row.setContentsMargins(9, 9, 0, 9)

        # Settings section
        settings_col = QVBoxLayout()
        header = QHBoxLayout()
        settings_row = QHBoxLayout()

        col1 = QVBoxLayout()
        col2 = QVBoxLayout()
        col3 = QVBoxLayout()
        col4 = QVBoxLayout()

        # Button section
        button_col = QVBoxLayout()
        button_section = QVBoxLayout()
        spacer = QHBoxLayout()

        # Set spacing and margins
        header.setContentsMargins(8, 0, 0, 0)

        col1.setSpacing(8)
        col1.setContentsMargins(6, 6, 6, 6)
        col2.setSpacing(8)
        col2.setContentsMargins(6, 6, 6, 6)
        col3.setSpacing(8)
        col3.setContentsMargins(6, 6, 6, 6)
        col4.setSpacing(8)
        col4.setContentsMargins(6, 6, 6, 6)

        button_section.setSpacing(8)
        button_section.setContentsMargins(6, 6, 15, 6)

        # Add widgets to settings section
        header.addWidget(settings_label)

        col1.insertSpacing(1, 30)
        col1.addWidget(general_label)
        col1.insertSpacing(3, 24)
        col1.addWidget(directory_toggle)
        col1.insertSpacing(5, 24)
        col1.addWidget(fixed_window_size)
        col1.insertSpacing(7, 24)
        col1.addWidget(window_size)
        col1.addStretch()

        col2.insertSpacing(1, 85)
        col2.addWidget(directory_toggle_label)
        col2.insertSpacing(3, 33)
        col2.addWidget(fixed_window_size_label)
        col2.insertSpacing(5, 33)
        col2.addWidget(window_size_label)
        col2.addStretch()

        col3.insertSpacing(1, 30)
        col3.addWidget(theme_label)
        col3.insertSpacing(3, 24)
        col3.addWidget(change_theme)
        col3.addStretch()

        settings_row.addStretch(1)
        settings_row.addLayout(col1, 30)
        settings_row.addLayout(col2, 30)
        settings_row.addLayout(col3, 30)
        settings_row.addLayout(col4, 15)

        settings_col.addLayout(header, 10)
        settings_col.addLayout(settings_row, 90)

        # Add widgets to button section
        button_col.addWidget(manage_folders4)
        button_col.addWidget(manage_files4)
        button_col.addWidget(manage_apps4)
        button_col.addWidget(home_menu4)
        button_col.addStretch()

        button_section.addLayout(spacer, 10)
        button_section.addLayout(button_col, 90)

        # Add columns to main layout
        master_row.addStretch(1)
        master_row.addLayout(settings_col, 68)
        master_row.addLayout(button_section, 20)

        self.page5.setLayout(master_row)

    # Events
    def widget_events(self):
        # Folder, file, and app lists
        lists = [self.folder_list, self.file_list, self.app_list]

        # Home screen folder, file, and app lists
        h_lists = [self.h_folder_list, self.h_file_list, self.h_app_list]

        # Return to home screen
        set_page1 = lambda: self.stack.setCurrentWidget(self.page1)
        for button in [self.home_menu1, self.home_menu2, self.home_menu3, self.home_menu4]:
            button.clicked.connect(set_page1)
            button.clicked.connect(self.clear_directories)

        # Switch to folder page
        set_page2 = lambda: self.stack.setCurrentWidget(self.page2)
        for button in [self.manage_folders1, self.manage_folders2, self.manage_folders3, self.manage_folders4]:
            button.clicked.connect(set_page2)
            button.clicked.connect(self.clear_directories)

        # Switch to file page
        set_page3 = lambda: self.stack.setCurrentWidget(self.page3)
        for button in [self.manage_files1, self.manage_files2, self.manage_files3, self.manage_files4]:
            button.clicked.connect(set_page3)
            button.clicked.connect(self.clear_directories)

        # Switch to app page
        set_page4 = lambda: self.stack.setCurrentWidget(self.page4)
        for button in [self.manage_apps1, self.manage_apps2, self.manage_apps3, self.manage_apps4]:
            button.clicked.connect(set_page4)
            button.clicked.connect(self.clear_directories)

        # Switch to settings page
        set_page5 = lambda: self.stack.setCurrentWidget(self.page5)
        for button in [self.settings1, self.settings2, self.settings3, self.settings4]:
            button.clicked.connect(set_page5)
            button.clicked.connect(self.clear_directories)

        # Toggle window settings
        self.fixed_window_size.toggled.connect(self.window_settings)

        # Change window size
        self.window_size.activated.connect(self.change_window_size)

        # Change theme
        self.change_theme.activated.connect(self.window_color_mode)

        # Handle file opening, context menu pop-up, syncing list items to home screen, and showing item directory
        for item in lists:
            # Open folders, files, and apps within each list
            item.itemDoubleClicked.connect(self.open_item)
            h_lists[lists.index(item)].itemDoubleClicked.connect(self.open_item)

            # Open context menu when a QListWidgetItem is right-clicked
            item.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
            item.customContextMenuRequested.connect(partial(self.context_menu, item))

            # Sync list to corresponding menu list
            self.stack.currentChanged.connect(partial(self.sync, item, h_lists[lists.index(item)]))

            # Show directory of selected item
            item.itemClicked.connect(self.show_directory)
            h_lists[lists.index(item)].itemClicked.connect(self.show_directory)

            # Install event filter on each QListWidget
            item.viewport().installEventFilter(self)
            h_lists[lists.index(item)].viewport().installEventFilter(self)

        # Open File Explorer to browse folders, files, and apps
        self.add_folders.clicked.connect(self.browse_folders)
        self.add_files.clicked.connect(self.browse_files)
        self.add_apps.clicked.connect(self.browse_apps)

    # Browse folders, files, and apps in File Explorer and add to respective lists
    def browse_folders(self):
        home_dir = os.path.expanduser("~")
        folder_path = QFileDialog.getExistingDirectory(self, "Browse Folders", home_dir)

        icon = QIcon(os.path.join(self.icons, "folder item icon.png"))

        if not folder_path:
            return
        else:
            folder_name = os.path.basename(folder_path)
            folder_item = QListWidgetItem(icon, folder_name)
            folder_item.setData(QtCore.Qt.ItemDataRole.UserRole, folder_path)
            self.folder_list.addItem(folder_item)

    def browse_files(self):
        home_dir = os.path.expanduser("~")
        file_path = QFileDialog.getOpenFileName(self, "Open File", home_dir)[0]

        icon = QIcon(os.path.join(self.icons, "file item icon.png"))

        if not file_path:
            return
        else:
            file_name = os.path.basename(file_path)
            file_item = QListWidgetItem(icon, file_name)
            file_item.setData(QtCore.Qt.ItemDataRole.UserRole, file_path)
            self.file_list.addItem(file_item)

    def browse_apps(self):
        home_dir = os.path.expanduser("~")
        app_path = QFileDialog.getOpenFileName(self, "Open App", home_dir, "Apps (*.exe *.url)")[0]

        info = QtCore.QFileInfo(app_path)
        icon = QFileIconProvider().icon(info)

        if not app_path:
            return
        else:
            app_name = os.path.basename(app_path)
            app_name, _ = os.path.splitext(app_name)
            app_item = QListWidgetItem(icon, app_name)
            app_item.setData(QtCore.Qt.ItemDataRole.UserRole, app_path)
            self.app_list.addItem(app_item)

    # Display directory of selected item in text box
    def show_directory(self, item):
        if not self.directory_toggle.isChecked():
            return

        data = item.data(QtCore.Qt.ItemDataRole.UserRole)

        if data is None:
            return

        if self.stack.currentWidget() == self.page1:
            self.show_dir1.setPlainText(data)
        elif self.stack.currentWidget() == self.page2:
            self.show_dir2.setPlainText(data)
        elif self.stack.currentWidget() == self.page3:
            self.show_dir3.setPlainText(data)
        else:
            self.show_dir4.setPlainText(data)

    # Clear all displayed directories
    def clear_directories(self):
        self.show_dir1.clear()
        self.show_dir2.clear()
        self.show_dir3.clear()
        self.show_dir4.clear()

    # Open context menu to rename or remove items
    def context_menu(self, items, pos):
        item = items.itemAt(pos)

        if item is not None:
            menu = QMenu(self.window())

            rename = menu.addAction("Rename")
            remove = menu.addAction("Remove")

            # Call either "rename" or "remove" on corresponding button press
            rename.triggered.connect(partial(self.rename, item))
            remove.triggered.connect(partial(self.remove, items, item))

            menu.popup(QCursor.pos())

    # Rename selected list item
    def rename(self, item):
        name, ok_clicked = QInputDialog.getText(self, "Rename", "", text=item.text())

        if ok_clicked and name != "":
            item.setText(name)

    # Default window settings
    def window_default(self):
        self.resize(1000, 660)
        self.setMinimumSize(700, 500)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # Center window
        window = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        window.moveCenter(center)
        self.move(window.topLeft())

        # Create a container and round corners
        self.container = QWidget(self)
        self.container.setObjectName("container")

        self.container.setStyleSheet("""
            #container {
                background-color: #454750;
                border-radius: 14px;
            }
            """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)

        self.inner_layout = QVBoxLayout(self.container)

    # Fixed window size window toggle
    def window_settings(self):
        if self.fixed_window_size.isChecked():
            if self.title_bar.is_maximized:
                self.title_bar.maximize_toggle()

            self.enable_grips(False)
            self.window_size.setEnabled(True)
            self.title_bar.max_button.setVisible(False)
            self.setFixedSize(1000, 660)
        else:
            self.enable_grips(True)
            self.window_size.setEnabled(False)
            self.title_bar.max_button.setVisible(True)
            self.setMinimumSize(700, 500)
            self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)

    # Change window size for fixed-size window
    def change_window_size(self, index):
        match index:
            case 0:
                self.setFixedSize(1280, 720)
            case 1:
                self.setFixedSize(1200, 600)
            case 2:
                self.setFixedSize(1000, 660)
            case 3:
                self.setFixedSize(800, 550)
            case 4:
                self.setFixedSize(700, 500)

    # Choose window_color or window_max_color depending on window state
    def window_color_mode(self, index):
        if self.title_bar.is_maximized:
            self.window_max_color(index)
        else:
            self.window_color(index)

    # Set window color to match current theme
    def window_color(self, index):
        match index:
            # Default theme
            case 0:
                self.directory_toggle.set_bg_color("#51587a")
                self.directory_toggle.set_active_color("#7285e0")
                self.fixed_window_size.set_bg_color("#51587a")
                self.fixed_window_size.set_active_color("#7285e0")
                self.default_icons()
                self.theme = self.default_theme
                self.color = "#343642"
                self.style_sheet()
                self.container.setStyleSheet("""
                    #container {
                        background-color: #454750;
                        border-radius: 14px;
                    }
                    """)
            # Dark theme
            case 1:
                self.directory_toggle.set_bg_color("#444444")
                self.directory_toggle.set_active_color("#7d7d7d")
                self.fixed_window_size.set_bg_color("#444444")
                self.fixed_window_size.set_active_color("#7d7d7d")
                self.default_icons()
                self.theme = self.dark_theme
                self.color = "#202020"
                self.style_sheet()
                self.container.setStyleSheet("""
                    #container {
                        background-color: #353535;
                        border-radius: 14px;
                    }
                    """)
            # Light theme
            case 2:
                self.directory_toggle.set_bg_color("#999999")
                self.directory_toggle.set_active_color("#FFFFFF")
                self.fixed_window_size.set_bg_color("#999999")
                self.fixed_window_size.set_active_color("#FFFFFF")
                self.light_icons()
                self.theme = self.light_theme
                self.color = "#d2d2d2"
                self.style_sheet()
                self.container.setStyleSheet("""
                    #container {
                        background-color: #FFFFFF;
                        border-radius: 14px;
                    }
                    """)

    # Set window color to match current theme for maximized window
    def window_max_color(self, index):
        match index:
            # Default theme
            case 0:
                self.directory_toggle.set_bg_color("#51587a")
                self.directory_toggle.set_active_color("#7285e0")
                self.fixed_window_size.set_bg_color("#51587a")
                self.fixed_window_size.set_active_color("#7285e0")
                self.default_icons()
                self.theme = self.default_theme
                self.color = "#343642"
                self.style_sheet()
                self.container.setStyleSheet("""
                            #container {
                                background-color: #454750;
                                border-radius: 0px;
                            }
                            """)
            # Dark theme
            case 1:
                self.directory_toggle.set_bg_color("#444444")
                self.directory_toggle.set_active_color("#7d7d7d")
                self.fixed_window_size.set_bg_color("#444444")
                self.fixed_window_size.set_active_color("#7d7d7d")
                self.default_icons()
                self.theme = self.dark_theme
                self.color = "#202020"
                self.style_sheet()
                self.container.setStyleSheet("""
                            #container {
                                background-color: #353535;
                                border-radius: 0px;
                            }
                            """)
            # Light theme
            case 2:
                self.directory_toggle.set_bg_color("#999999")
                self.directory_toggle.set_active_color("#FFFFFF")
                self.fixed_window_size.set_bg_color("#999999")
                self.fixed_window_size.set_active_color("#FFFFFF")
                self.light_icons()
                self.theme = self.light_theme
                self.color = "#d2d2d2"
                self.style_sheet()
                self.container.setStyleSheet("""
                            #container {
                                background-color: #FFFFFF;
                                border-radius: 0px;
                            }
                            """)

    # Switch to light mode icons
    def light_icons(self):
        self.title_bar.min_button.setIcon(self.min_icon_light)
        self.title_bar.max_button.setIcon(self.max_icon_light)
        self.title_bar.close_button.setIcon(self.close_icon_light)
        self.title_bar.normal_button.setIcon(self.normal_icon_light)

    # Switch to default icons
    def default_icons(self):
        self.title_bar.min_button.setIcon(self.min_icon)
        self.title_bar.max_button.setIcon(self.max_icon)
        self.title_bar.close_button.setIcon(self.close_icon)
        self.title_bar.normal_button.setIcon(self.normal_icon)

    # Always resize container to window size
    def resizeEvent(self, event):
        self.container.resize(self.size())
        super().resizeEvent(event)
        self.update_grips()

    # Update window upon maximization/restoration
    def apply_max_state(self, maximized: bool):
        # Disable/enable size grips and update corners of container
        if maximized:
            self.enable_grips(False)
            self.inner_layout.setContentsMargins(0, 0, 0, 0)
            self.window_max_color(self.change_theme.currentIndex())
        else:
            self.enable_grips(True)
            self.inner_layout.setContentsMargins(9, 9, 9, 9)
            self.window_color(self.change_theme.currentIndex())

    # Call container_paint_event on page change
    def on_page_change(self):
        self.container.update()

    # Custom background
    def container_paint_event(self, event):
        page = self.stack.currentWidget()

        painter = QPainter(self.container)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set pen
        pen = QPen(QColor(self.color), 2)
        painter.setPen(pen)

        # Set brush
        brush = QBrush(QColor(self.color))
        painter.setBrush(brush)

        # Set width and align top edge
        if page == self.page1:
            # Set width for page1 background and set top edge to align with top of dir1
            rect_width = self.h_app_list.mapTo(self.container, QtCore.QPoint(0, 0)).x() + self.h_app_list.width()
            top_edge = self.show_dir1.mapTo(self.container, QtCore.QPoint(0, 0)).y() + 1
        elif page == self.page2:
            # Set width for page2 background and set top edge to align with top of dir2
            rect_width = self.folder_list.mapTo(self.container, QtCore.QPoint(0, 0)).x() + self.folder_list.width()
            top_edge = self.show_dir2.mapTo(self.container, QtCore.QPoint(0, 0)).y() + 1
        elif page == self.page3:
            # Set width for page3 background and set top edge to align with top of dir3
            rect_width = self.file_list.mapTo(self.container, QtCore.QPoint(0, 0)).x() + self.file_list.width()
            top_edge = self.show_dir3.mapTo(self.container, QtCore.QPoint(0, 0)).y() + 1
        elif page == self.page4:
            # Set width for page4 background and set top edge to align with top of dir4
            rect_width = self.app_list.mapTo(self.container, QtCore.QPoint(0, 0)).x() + self.app_list.width()
            top_edge = self.show_dir4.mapTo(self.container, QtCore.QPoint(0, 0)).y() + 1
        else:
            rect_width = self.manage_folders4.mapTo(self.container, QtCore.QPoint(0, 0)).x() - 20
            top_edge = self.manage_folders4.mapTo(self.container, QtCore.QPoint(0, 0)).y() + 1

        # Clip bottom-left corner when window is not maximized
        clip_path = QPainterPath()
        if self.title_bar.is_maximized:
            clip_path.addRect(QtCore.QRectF(self.container.rect()))
        else:
            clip_path.addRoundedRect(QtCore.QRectF(self.container.rect()), 14, 14)

        painter.setClipPath(clip_path)

        painter.drawRoundedRect(-10, top_edge, rect_width + 10, self.height(), 14, 14)

        painter.end()

    # Manage window grips; Adapted from Stack Overflow
    @property
    def grip_size(self):
        return self._grip_size

    def set_grip_size(self, size):
        if size == self._grip_size:
            return

        self._grip_size = max(2, size)
        self.update_grips()

    def update_grips(self):
        parent = self.container
        g_size = self.grip_size
        w, h = parent.width(), parent.height()

        # Corner grips
        self.cornerGrips[0].setGeometry(0, 0, g_size, g_size)  # top-left
        self.cornerGrips[1].setGeometry(w - g_size, 0, g_size, g_size)  # top-right
        self.cornerGrips[2].setGeometry(w - g_size, h - g_size, g_size, g_size)  # bottom-right
        self.cornerGrips[3].setGeometry(0, h - g_size, g_size, g_size)  # bottom-left

        # Side grips
        self.sideGrips[0].setGeometry(0, g_size, g_size, h - 2 * g_size)  # left
        self.sideGrips[1].setGeometry(g_size, 0, w - 2 * g_size, g_size)  # top
        self.sideGrips[2].setGeometry(w - g_size, g_size, g_size, h - 2 * g_size)  # right
        self.sideGrips[3].setGeometry(g_size, h - g_size, w - 2 * g_size, g_size)  # bottom

    # Enable/disable grips
    def enable_grips(self, enabled: bool):
        for grip in self.sideGrips:
            grip.setEnabled(enabled)
            grip.setVisible(enabled)

        for grip in self.cornerGrips:
            grip.setEnabled(enabled)
            grip.setVisible(enabled)

        if enabled:
            self.update_grips()

    # Clear all QListWidgetItem selections if left-click is detected within empty space of QListWidget
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:

                item = None

                for list_widget in [
                    self.h_folder_list,
                    self.h_file_list,
                    self.h_app_list,
                    self.folder_list,
                    self.file_list,
                    self.app_list
                ]:
                    if obj == list_widget.viewport():
                        item = list_widget.itemAt(event.pos())
                        break

                # If an empty area in any list is clicked
                if item is None:
                    self.clear_selections()

        return super().eventFilter(obj, event)

    # Clear QListWidgetItem selections
    def clear_selections(self):
        self.h_folder_list.clearSelection()
        self.h_file_list.clearSelection()
        self.h_app_list.clearSelection()
        self.folder_list.clearSelection()
        self.file_list.clearSelection()
        self.app_list.clearSelection()

    # Read stylesheet for current theme
    def style_sheet(self):
        application = QApplication.instance()
        if application:
            with open(self.theme, "r") as fh:
                application.setStyleSheet(fh.read())

    def read_settings(self):
        geometry = self.settings.value("geometry", QtCore.QByteArray())

        # Restore window geometry from previous session
        if geometry:
            self.restoreGeometry(geometry)

        # Restore general settings from previous session
        if self.settings.value("show_directory"):
            self.directory_toggle.setChecked(self.settings.value("show_directory", True, bool))
            self.directory_toggle.start_animation(self.directory_toggle.isChecked())

        if self.settings.value("fixed_size"):
            self.fixed_window_size.setChecked(self.settings.value("fixed_size", False, bool))
            self.fixed_window_size.start_animation(self.fixed_window_size.isChecked())

            if self.fixed_window_size.isChecked():
                self.window_size.setEnabled(True)

        if self.settings.value("window_size"):
            self.window_size.setCurrentIndex(self.settings.value("window_size"))

        if self.settings.value("theme"):
            self.change_theme.setCurrentIndex(self.settings.value("theme"))

        if self.settings.value("maximized", False, bool):
            self.title_bar.maximize_toggle()
            self.window_max_color(self.settings.value("theme"))
        else:
            self.window_color(self.settings.value("theme"))

        # Restore list items
        lists = {
            "folders": self.folder_list,
            "files": self.file_list,
            "apps": self.app_list
        }

        for name, list_widget in lists.items():
            size = self.settings.beginReadArray(name)

            for i in range(size):
                self.settings.setArrayIndex(i)

                text = self.settings.value("text")
                path = self.settings.value("path")
                item_type = self.settings.value("type")

                # Restore respective icon
                if item_type == "folder":
                    icon = QIcon(os.path.join(self.icons, "folder item icon.png"))
                elif item_type == "file":
                    icon = QIcon(os.path.join(self.icons, "file item icon.png"))
                else:
                    info = QtCore.QFileInfo(path)
                    icon = QFileIconProvider().icon(info)

                item = QListWidgetItem(icon, text)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, path)

                list_widget.addItem(item)

            self.settings.endArray()

        self.sync(self.folder_list, self.h_folder_list)
        self.sync(self.file_list, self.h_file_list)
        self.sync(self.app_list, self.h_app_list)

    def closeEvent(self, event):
        # Save current window size
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("maximized", self.title_bar.is_maximized)

        # Save current settings
        self.settings.setValue("show_directory", self.directory_toggle.isChecked())
        self.settings.setValue("fixed_size", self.fixed_window_size.isChecked())
        self.settings.setValue("window_size", self.window_size.currentIndex())
        self.settings.setValue("theme", self.change_theme.currentIndex())

        # Save list items
        lists = {
            "folders": (self.folder_list, "folder"),
            "files": (self.file_list, "file"),
            "apps": (self.app_list, "app")
        }

        for name, (list_widget, item_type) in lists.items():
            self.settings.beginWriteArray(name)

            for i in range(list_widget.count()):
                self.settings.setArrayIndex(i)
                item = list_widget.item(i)

                self.settings.setValue("text", item.text())
                self.settings.setValue("path", item.data(QtCore.Qt.ItemDataRole.UserRole))
                self.settings.setValue("type", item_type)

            self.settings.endArray()

        self.settings.sync()
        super().closeEvent(event)
        event.accept()

    # Remove selected list item
    @staticmethod
    def remove(items, item):
        items.takeItem(items.row(item))

    # Open selected folder, file, or app
    @staticmethod
    def open_item(item):
        path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path))

    # Sync corresponding list in home with edited list
    @staticmethod
    def sync(items, home_list):
        home_list.clear()

        for i in range(items.count()):
            src_item = items.item(i)
            item_clone = items.item(i).clone()
            item_clone.setData(QtCore.Qt.ItemDataRole.UserRole, src_item.data(QtCore.Qt.ItemDataRole.UserRole))
            home_list.addItem(item_clone)


# Run application
if __name__ in "__main__":
    app = QApplication([])
    main = Manager()
    main.show()
    app.exec()
