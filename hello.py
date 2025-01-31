import gi
import os
import json
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GdkPixbuf

class WelcomeWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Yelena Hello")
        self.set_default_size(600, 480)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_file = os.path.join(current_dir, "icons/prog1.svg")
        try:
            icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_file)
            self.set_icon(icon_pixbuf)
        except Exception as e:
            print(f"Error loading window icon: {e}")
        
        logo_file = os.path.join(current_dir, "icons/cuerdos.svg")
        logo = Gtk.Image()
        try:
            logo.set_from_file(logo_file)
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        self.welcome_label = Gtk.Label()
        self.welcome_label.set_halign(Gtk.Align.CENTER)
        self.welcome_label.set_line_wrap(True)
        
        self.buttons: dict[str, dict] = {}
        self.load_languages(current_dir)
        
        self.mas_button = self.create_button_with_icon("/usr/share/yel-hello/icons/github.svg")
        self.sourceforge_button = self.create_button_with_icon("/usr/share/yel-hello/icons/sourceforge.svg")
        self.news_button = self.create_button_with_icon("/usr/share/yel-hello/icons/news.svg")
        self.wiki_button = self.create_button_with_icon("/usr/share/yel-hello/icons/wiki.svg")
        self.spins_button = self.create_button_with_icon("/usr/share/yel-hello/icons/spins.svg")
        self.dev_team_button = self.create_button_with_icon("/usr/share/yel-hello/icons/dev_team.svg")
        self.webpage_button = self.create_button_with_icon("/usr/share/yel-hello/icons/webpage.svg")
        self.feedback_button = self.create_button_with_icon("/usr/share/yel-hello/icons/feedback.svg")
        self.bauh_button = self.create_button_with_icon("/usr/share/yel-hello/icons/bauh.svg")

        self.autostart_switch = Gtk.Switch()
        self.autostart_switch.connect("state-set", self.on_autostart_switch_toggled)
        
        close_button = Gtk.Button.new_with_label(">>")
        close_button.connect("clicked", self.close_application)
        
        self.language_store = Gtk.ListStore(str)
        for language in self.buttons.keys():
            self.language_store.append([language])
        
        self.language_combo = Gtk.ComboBox.new_with_model(self.language_store)
        renderer_text = Gtk.CellRendererText()
        self.language_combo.pack_start(renderer_text, True)
        self.language_combo.add_attribute(renderer_text, "text", 0)
        
        def on_language_changed(combo):
            index = combo.get_active()
            if index > -1:
                language = list(self.buttons.keys())[index]
                self.update_button_labels(language)
                self.welcome_label.set_markup(self.buttons[language]["description"])
                self.save_language_setting(language)
        
        self.language_combo.connect("changed", on_language_changed)
        
        self.load_language_setting()
        self.load_autostart_setting()
        
        self.mas_button.connect("clicked", self.open_url, "https://github.com/CuerdOS")
        self.sourceforge_button.connect("clicked", self.open_url, "https://sourceforge.net/projects/cuerdos/")
        self.news_button.connect("clicked", self.open_url, "https://cuerdos.github.io/changelog_es.html#changelog")
        self.wiki_button.connect("clicked", self.open_url, "https://cuerdoswiki.blogspot.com/")
        self.spins_button.connect("clicked", self.open_url, "https://cuerdos.github.io/spins.html")
        self.dev_team_button.connect("clicked", self.open_url, "https://cuerdos.github.io/index.html#descarga")
        self.webpage_button.connect("clicked", self.open_url, "https://cuerdos.github.io/index.html")
        self.feedback_button.connect("clicked", self.open_url, "https://t.me/+GibSWjFc89Q2ODU8")
        self.bauh_button.connect("clicked", self.open_bauh)
        
        button_grid = Gtk.Grid()
        button_grid.set_column_homogeneous(True)
        button_grid.set_row_homogeneous(True)
        button_grid.set_column_spacing(10)
        
        button_grid.attach(self.mas_button, 0, 0, 1, 1)
        button_grid.attach(self.sourceforge_button, 1, 0, 1, 1)
        button_grid.attach(self.bauh_button, 2, 0, 1, 1)
        button_grid.attach(self.news_button, 0, 1, 1, 1)
        button_grid.attach(self.wiki_button, 1, 1, 1, 1)
        button_grid.attach(self.spins_button, 2, 1, 1, 1)
        button_grid.attach(self.dev_team_button, 0, 2, 1, 1)
        button_grid.attach(self.webpage_button, 1, 2, 1, 1)
        button_grid.attach(self.feedback_button, 2, 2, 1, 1)
        
        # Create menu bar
        menu_bar = Gtk.MenuBar()
        
        # Create the Help menu
        help_menu = Gtk.Menu()
        help_menu_item = Gtk.MenuItem(label="Ayuda")
        help_menu_item.set_submenu(help_menu)
        
        # Create the About menu item
        about_menu_item = Gtk.MenuItem(label="Acerca de...")
        about_menu_item.connect("activate", self.show_about_dialog)
        help_menu.append(about_menu_item)
        
        menu_bar.append(help_menu_item)
        
        footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        footer_box.pack_start(self.language_combo, False, False, 0)
        footer_box.pack_start(self.autostart_switch, False, False, 0)
        footer_box.pack_end(close_button, False, False, 0)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_homogeneous(False)
        main_box.pack_start(menu_bar, False, False, 0) # Add the menu bar to the main box
        main_box.pack_start(logo, True, True, 0)
        main_box.pack_start(self.welcome_label, True, True, 0)
        main_box.pack_start(button_grid, True, True, 0)
        main_box.pack_end(footer_box, False, False, 0)
        
        self.add(main_box)
        self.connect("destroy", Gtk.main_quit)
        
    def create_button_with_icon(self, icon_path):
        button = Gtk.Button()
        icon = Gtk.Image()
        try:
            icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
            # Escalar el icono a 16x16
            scaled_pixbuf = icon_pixbuf.scale_simple(16, 16, GdkPixbuf.InterpType.BILINEAR)
            icon.set_from_pixbuf(scaled_pixbuf)
        except Exception as e:
            print(f"Error loading icon {icon_path}: {e}")
        button.set_image(icon)
        return button
    
    def load_languages(self, current_dir):
        # Load languages from the "languages" folder in the current directory
        languages_dir = os.path.join(current_dir, "languages")
        if not os.path.exists(languages_dir):
            raise FileNotFoundError(f"The directory {languages_dir} does not exist.")
        for file_name in os.listdir(languages_dir):
            if file_name.endswith(".json"):
                language = file_name.split(".")[0].capitalize()
                with open(os.path.join(languages_dir, file_name), "r", encoding="utf-8") as f:
                    self.buttons[language] = json.load(f)
    
    def update_button_labels(self, language):
        labels = self.buttons[language]["buttons"]
        self.mas_button.set_label(labels[0])
        self.sourceforge_button.set_label(labels[1])
        self.news_button.set_label(labels[3])
        self.wiki_button.set_label(labels[4])
        self.spins_button.set_label(labels[5])
        self.dev_team_button.set_label(labels[6])
        self.webpage_button.set_label(labels[7])
        self.feedback_button.set_label(labels[8])
        self.bauh_button.set_label(labels[2])
        
    def open_bauh(self, button): # pylint: disable=unused-argument
        os.system("bauh")
    
    def open_url(self, button, url): # pylint: disable=unused-argument
        Gio.AppInfo.launch_default_for_uri(url, None)
    
    def show_about_dialog(self, button): # pylint: disable=unused-argument
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name("Yelena Hello")
        about_dialog.set_version("1.2 v100125a Elena")
        about_dialog.set_comments("Bienvenida de CuerdOS GNU/Linux.")
        about_dialog.set_website("https://github.com/CuerdOS")
        about_dialog.set_website_label("GitHub")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.set_authors([
            "Ale D.M", "Leo H. Pérez (GatoVerde95)", "Pablo G.", "Welkis", "GatoVerde95 Studios", "CuerdOS Community"
        ])
        about_dialog.set_copyright("© 2025 CuerdOS")
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_file = os.path.join(current_dir, "icons/prog1.svg")
            icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_file)
            about_dialog.set_logo(icon_pixbuf)
        except Exception as e:
            print(f"Error loading icon: {e}")
        
        about_dialog.run()
        about_dialog.destroy()
    
    def close_application(self, button): # pylint: disable=unused-argument
        self.destroy()
    
    def save_language_setting(self, language):
        with open("config.json", "w", encoding="utf-8") as config_file:
            json.dump({"language": language}, config_file)
        
    def load_language_setting(self):
        try:
            with open("config.json", "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
                language = config.get("language", "Español")
                self.language_combo.set_active(list(self.buttons.keys()).index(language))
                self.update_button_labels(language)
                self.welcome_label.set_markup(self.buttons[language]["description"])
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    def load_autostart_setting(self):
        autostart_file = os.path.expanduser("~/.config/autostart/cuerdos.desktop")
        try:
            with open(autostart_file, "r", encoding="utf-8"):
                self.autostart_switch.set_active(True)
        except FileNotFoundError:
            self.autostart_switch.set_active(False)
            
    def on_autostart_switch_toggled(self, switch, state): # pylint: disable=unused-argument
        autostart_file = os.path.expanduser("~/.config/autostart/hello.desktop")
        if state:
            os.makedirs(os.path.dirname(autostart_file), exist_ok=True)
            with open(autostart_file, "w", encoding="utf-8") as f:
                f.write("[Desktop Entry]\n")
                f.write("Type=Application\n")
                f.write("Exec=python3 " + os.path.abspath(__file__) + "\n")
                f.write("Hidden=false\n")
                f.write("NoDisplay=false\n")
                f.write("X-GNOME-Autostart-enabled=true\n")
                f.write("Name=CuerdOS Yelena Hello\n")
                f.write("Comment=Welcome to CuerdOS\n")
        else:
            if os.path.exists(autostart_file):
                os.remove(autostart_file)

if __name__ == "__main__":
    win = WelcomeWindow()
    win.show_all()
    Gtk.main()