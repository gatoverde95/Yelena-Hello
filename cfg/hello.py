import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GdkPixbuf

class WelcomeWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="CuerdOS Yelena Hello 1.0 Katie")
        self.set_border_width(20)
        self.set_default_size(600, 400)
        self.set_resizable(False)  # Prevent window resizing
        
        # Set the window to open in the center of the screen
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Get the current execution directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load the window icon
        icon_file = os.path.join(current_dir, "cuerdos.svg")
        try:
            icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_file)
            self.set_icon(icon_pixbuf)
        except Exception as e:
            print(f"Error loading window icon: {e}")
        
        # Create the logo image
        logo_file = os.path.join(current_dir, "cuerdos.svg")
        logo = Gtk.Image()
        try:
            logo.set_from_file(logo_file)
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        # Welcome label with description
        self.welcome_label = Gtk.Label()
        self.welcome_label.set_markup("<span size='x-large' weight='bold' foreground='#333333'>¡Bienvenido a <b>CuerdOS</b>!</span>\n\n"
                                      "Bienvenido a CuerdOS GNU/Linux, Optimizado hasta el ultimo pixel para ti.")
        self.welcome_label.set_halign(Gtk.Align.CENTER)
        self.welcome_label.set_line_wrap(True)
        
        # Main buttons
        self.buttons = {
            "Español": ["Más...", "Sourceforge", "Acerca de Yelena", "Novedades", "Wiki", "Spins", "Dev. Team", "Página Web", "CuerdOS Feedback"],
            "English": ["More...", "Sourceforge", "About Yelena", "News", "Wiki", "Spins", "Dev. Team", "Webpage", "CuerdOS Feedback"],
            "Português": ["Mais...", "Sourceforge", "Sobre Yelena", "Notícias", "Wiki", "Spins", "Dev. Team", "Página Web", "CuerdOS Feedback"]
        }
        
        self.mas_button = Gtk.Button.new_with_label(self.buttons["Español"][0])
        self.sourceforge_button = Gtk.Button.new_with_label(self.buttons["Español"][1])
        self.about_button = Gtk.Button.new_with_label(self.buttons["Español"][2])
        self.news_button = Gtk.Button.new_with_label(self.buttons["Español"][3])
        self.wiki_button = Gtk.Button.new_with_label(self.buttons["Español"][4])
        self.spins_button = Gtk.Button.new_with_label(self.buttons["Español"][5])
        self.dev_team_button = Gtk.Button.new_with_label(self.buttons["Español"][6])
        self.webpage_button = Gtk.Button.new_with_label(self.buttons["Español"][7])
        self.feedback_button = Gtk.Button.new_with_label(self.buttons["Español"][8])
        
        # Close button
        close_button = Gtk.Button.new_with_label("Cerrar")
        close_button.connect("clicked", self.close_application)
        
        # Language switcher
        self.languages = [("Español", "¡Bienvenido a <b>CuerdOS</b> Cessna!\n\n"
                                        "Bienvenido a CuerdOS GNU/Linux, Optimizado hasta el ultimo pixel para ti."),
                          ("English", "Welcome to <b>CuerdOS</b> Cessna!\n\n"
                                      "Welcome to CuerdOS GNU/Linux, Optimized to the last pixel for you."),
                          ("Português", "Bem-vindo à <b>CuerdOS</b> Cessna!\n\n"
                                         "Bem-vindo ao CuerdOS GNU/Linux, Otimizado até o último pixel para você.")]
        
        self.language_store = Gtk.ListStore(str)
        for language, _ in self.languages:
            self.language_store.append([language])
        
        self.language_combo = Gtk.ComboBox.new_with_model(self.language_store)
        renderer_text = Gtk.CellRendererText()
        self.language_combo.pack_start(renderer_text, True)
        self.language_combo.add_attribute(renderer_text, "text", 0)
        
        def on_language_changed(combo):
            index = combo.get_active()
            if index > -1:
                language, _ = self.languages[index]
                self.update_button_labels(language)
                _, description = self.languages[index]
                self.welcome_label.set_markup(description)
        
        self.language_combo.connect("changed", on_language_changed)
        self.language_combo.set_active(0)  # Set initial language
        
        # Connect buttons to their respective web page opening functions
        self.mas_button.connect("clicked", self.open_url, "https://github.com/CuerdOS")
        self.sourceforge_button.connect("clicked", self.open_url, "https://sourceforge.net/projects/cuerdos/")
        self.about_button.connect("clicked", self.show_about_dialog)
        self.news_button.connect("clicked", self.open_url, "https://cuerdos.github.io/changelog_es.html#changelog")
        self.wiki_button.connect("clicked", self.open_url, "https://cuerdoswiki.blogspot.com/")
        self.spins_button.connect("clicked", self.open_url, "https://cuerdos.github.io/spins.html")
        self.dev_team_button.connect("clicked", self.open_url, "https://cuerdos.github.io/index.html#descarga")
        self.webpage_button.connect("clicked", self.open_url, "https://cuerdos.github.io/index.html")
        self.feedback_button.connect("clicked", self.open_url, "https://t.me/+GibSWjFc89Q2ODU8")
        
        # Grid layout for buttons
        button_grid = Gtk.Grid()
        button_grid.set_column_homogeneous(True)
        button_grid.set_row_homogeneous(True)
        button_grid.set_column_spacing(10)
        
        # Add buttons to the grid
        button_grid.attach(self.mas_button, 0, 0, 1, 1)
        button_grid.attach(self.sourceforge_button, 1, 0, 1, 1)
        button_grid.attach(self.about_button, 2, 0, 1, 1)
        button_grid.attach(self.news_button, 0, 1, 1, 1)
        button_grid.attach(self.wiki_button, 1, 1, 1, 1)
        button_grid.attach(self.spins_button, 2, 1, 1, 1)
        button_grid.attach(self.dev_team_button, 0, 2, 1, 1)
        button_grid.attach(self.webpage_button, 1, 2, 1, 1)
        button_grid.attach(self.feedback_button, 2, 2, 1, 1)
        
        # Footer box with language switcher and close button
        footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        footer_box.pack_start(self.language_combo, False, False, 0)
        footer_box.pack_end(close_button, False, False, 0)
        
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_homogeneous(False)
        main_box.pack_start(logo, True, True, 0)
        main_box.pack_start(self.welcome_label, True, True, 0)
        main_box.pack_start(button_grid, True, True, 0)  # Add button grid
        main_box.pack_end(footer_box, False, False, 0)  # Add footer with switcher and close button
        
        self.add(main_box)
        
        # Connect signals
        self.connect("destroy", Gtk.main_quit)
    
    def update_button_labels(self, language):
        labels = self.buttons[language]
        self.mas_button.set_label(labels[0])
        self.sourceforge_button.set_label(labels[1])
        self.about_button.set_label(labels[2])
        self.news_button.set_label(labels[3])
        self.wiki_button.set_label(labels[4])
        self.spins_button.set_label(labels[5])
        self.dev_team_button.set_label(labels[6])
        self.webpage_button.set_label(labels[7])
        self.feedback_button.set_label(labels[8])
    
    def open_url(self, button, url):
        Gio.AppInfo.launch_default_for_uri(url, None)
    
    def show_about_dialog(self, button):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name("CuerdOS Yelena Hello")
        about_dialog.set_version("1.0 Katie | v.1.0.1a200724s")
        about_dialog.set_comments("Bienvenida de CuerdOS GNU/Linux, para darle su primer bienvenida a nuestra distribución. Potenciada por Software libre y tecnologias libres como Python & Thonny, R & RStudio y Go & Geany.")
        about_dialog.set_website("https://github.com/CuerdOS")
        about_dialog.set_website_label("Página de GitHub | Codigo Fuente")
        about_dialog.set_authors(["Leo H. Pérez (GatoVerde95)", "Pablo G.", "Ale D.M"])
        about_dialog.set_copyright("© 2024 CuerdOS")
        
        # Set icon
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_file = os.path.join(current_dir, "yel.svg")
            icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_file)
            about_dialog.set_logo(icon_pixbuf)
        except Exception as e:
            print(f"Error loading icon: {e}")
        
        about_dialog.run()
        about_dialog.destroy()
    
    def close_application(self, button):
        self.destroy()

if __name__ == "__main__":
    win = WelcomeWindow()
    win.show_all()
    Gtk.main()
