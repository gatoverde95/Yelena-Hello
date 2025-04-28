import gi
import os
import webbrowser
from pathlib import Path
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib

# Importar nuestro sistema de traducciones y configuración
from translations import Translator
from config import load_config, save_config

class WelcomeWindow(Gtk.Window):
    def __init__(self):
        # Cargar configuración
        self.config = load_config()
        
        # Inicializar traductor con el idioma guardado
        self.translator = Translator(self.config.get('language', 'es'))
        
        super().__init__(title=self.translator.get('window_title'))
        self.set_default_size(600, 400)
        self.set_resizable(False)
        self.set_icon_from_file("/usr/share/yel-hello/icons/prog1.svg")
        self.set_border_width(10)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Configuración principal
        self.setup_ui()
        
        # Crear archivo autostart según la configuración
        if self.config.get('autostart', True):
            self.create_autostart_file()
        
        # Iniciar animaciones
        GLib.timeout_add(30, self.fade_in_logo)
        GLib.timeout_add(3000, self.next_phrase)

    def setup_ui(self):
        # Contenedor principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)
        
        # Barra de menús
        main_box.pack_start(self.create_menu_bar(), False, False, 0)
        
        # Encabezado con animación
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        header_box.set_margin_top(10)
        header_box.set_margin_bottom(15)
        
        # Texto de bienvenida con estilo mejorado
        welcome_label = Gtk.Label(
            label=f"<span size='xx-large' font_weight='bold'>{self.translator.get('welcome_title')}</span>",
            use_markup=True,
            halign=Gtk.Align.CENTER
        )
        subtitle_label = Gtk.Label(
            label=f"<span size='large' font_style='italic'>{self.translator.get('welcome_subtitle')}</span>",
            use_markup=True,
            halign=Gtk.Align.CENTER
        )
        
        header_box.pack_start(welcome_label, False, False, 0)
        header_box.pack_start(subtitle_label, False, False, 0)
        main_box.pack_start(header_box, False, False, 0)
        
        # Contenedor central con logo y botones
        central_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        central_box.set_margin_top(10)
        central_box.set_margin_bottom(10)
        main_box.pack_start(central_box, True, True, 0)
        
        # Botones izquierda
        left_box = self.create_button_group([
            (self.translator.get('btn_official_page'), "web-browser", "https://cuerdos.github.io"),
            (self.translator.get('btn_editions'), "preferences-desktop", "https://cuerdos.github.io/spins.html"),
            (self.translator.get('btn_feedback'), "mail-send", "https://t.me/+GibSWjFc89Q2ODU8")
        ])
        central_box.pack_start(left_box, False, True, 0)
        
        # Logo central con efectos (sin borde)
        self.logo_image = Gtk.Image()
        self.logo_size = 200
        self.opacity = 0
        self.update_logo()
        central_box.pack_start(self.logo_image, True, True, 0)
        
        # Botones derecha
        right_box = self.create_button_group([
            (self.translator.get('btn_github'), "folder", "https://github.com/CuerdOS"),
            (self.translator.get('btn_wiki'), "help-browser", "https://cuerdoswiki.blogspot.com/"),
            (self.translator.get('btn_search'), "search", "https://cuerdos.github.io/search.html")
        ])
        central_box.pack_start(right_box, False, True, 0)
        
        # Slider con frases
        self.slider_phrases = self.translator.get('slider_phrases')
        self.current_phrase = 0
        
        # Marco para el slider
        slider_frame = Gtk.Frame()
        slider_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        
        self.slider_label = Gtk.Label(
            label=self.slider_phrases[self.current_phrase],
            halign=Gtk.Align.CENTER
        )
        self.slider_label.set_margin_top(5)
        self.slider_label.set_margin_bottom(5)
        self.slider_label.set_margin_start(10)
        self.slider_label.set_margin_end(10)
        
        slider_frame.add(self.slider_label)
        main_box.pack_start(slider_frame, False, False, 10)
        
        # Botones inferiores
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.END)
        
        # Botón de novedades
        news_button = Gtk.Button()
        news_icon = Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON)
        news_button.add(news_icon)
        news_button.set_tooltip_text(self.translator.get('btn_news'))
        news_button.connect("clicked", lambda _: webbrowser.open("https://cuerdos.github.io/changelog_es.html"))
        
        # Botón de configuración
        config_button = Gtk.Button()
        config_icon = Gtk.Image.new_from_icon_name("preferences-system", Gtk.IconSize.BUTTON)
        config_button.add(config_icon)
        config_button.set_tooltip_text(self.translator.get('btn_config'))
        config_button.connect("clicked", self.on_config_clicked)
        
        # Botón de cerrar
        close_button = Gtk.Button(label=self.translator.get('btn_close'))
        close_button.connect("clicked", self.on_close_clicked)
        
        button_box.pack_start(news_button, False, False, 0)
        button_box.pack_start(config_button, False, False, 0)
        button_box.pack_start(close_button, False, False, 0)
        main_box.pack_start(button_box, False, False, 5)

    def create_menu_bar(self):
        menu_bar = Gtk.MenuBar()
        
        # Menú Archivo
        file_menu = Gtk.MenuItem(label=self.translator.get('menu_file'))
        file_submenu = Gtk.Menu()
        
        # Opción: Novedades
        file_news = Gtk.MenuItem(label=self.translator.get('menu_news'))
        file_news.connect("activate", lambda _: webbrowser.open("https://cuerdos.github.io/changelog_es.html"))
        file_submenu.append(file_news)
        
        # Opción: Buscador
        file_search = Gtk.MenuItem(label=self.translator.get('menu_search'))
        file_search.connect("activate", lambda _: webbrowser.open("https://cuerdos.github.io/search.html"))
        file_submenu.append(file_search)
        
        file_submenu.append(Gtk.SeparatorMenuItem())
        
        file_quit = Gtk.MenuItem(label=self.translator.get('menu_quit'))
        file_quit.connect("activate", self.on_close_clicked)
        file_submenu.append(file_quit)
        file_menu.set_submenu(file_submenu)
        
        # Menú Ayuda
        help_menu = Gtk.MenuItem(label=self.translator.get('menu_help'))
        help_submenu = Gtk.Menu()
        
        help_docs = Gtk.MenuItem(label=self.translator.get('menu_docs'))
        help_docs.connect("activate", lambda _: webbrowser.open("https://cuerdoswiki.blogspot.com/"))
        help_submenu.append(help_docs)
        
        help_submenu.append(Gtk.SeparatorMenuItem())
        
        help_about = Gtk.MenuItem(label=self.translator.get('menu_about'))
        help_about.connect("activate", self.show_about_dialog)
        help_submenu.append(help_about)
        help_menu.set_submenu(help_submenu)
        
        # Añadir un menú para selección de idioma
        lang_menu = Gtk.MenuItem(label="Idioma/Language")
        lang_submenu = Gtk.Menu()
        
        # Crear opciones para cada idioma disponible
        for lang_code in self.translator.get_available_languages():
            lang_name = {"es": "Español", "en": "English", "pt": "Português", "it": "Italiano", "de": "Deutsch", "ja": "日本語", "ko": "한국어"}.get(lang_code, lang_code.upper())
            lang_item = Gtk.MenuItem(label=lang_name)
            lang_item.connect("activate", lambda _, code=lang_code: self.change_language(code))
            lang_submenu.append(lang_item)
            
        lang_menu.set_submenu(lang_submenu)
        
        menu_bar.append(file_menu)
        menu_bar.append(help_menu)
        menu_bar.append(lang_menu)  # Agregar menú de idiomas
        return menu_bar
    
    def change_language(self, lang_code):
        """Cambia el idioma de la aplicación y actualiza la interfaz"""
        if self.translator.set_language(lang_code):
            # Guardar la preferencia de idioma
            self.config['language'] = lang_code
            save_config(self.config)
            
            # Actualizar título de la ventana
            self.set_title(self.translator.get('window_title'))
            
            # Mostrar mensaje informativo
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Idioma cambiado a " + {"es": "Español", "en": "English", "pt": "Português", "it": "Italiano", "de": "Deutsch", "ja": "日本語", "ko": "한국어"}.get(lang_code, lang_code)
            )
            dialog.format_secondary_text("Por favor, reinicie la aplicación para aplicar los cambios.")
            dialog.run()
            dialog.destroy()

    def create_button_group(self, button_data):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        for label, icon_name, url in button_data:
            button = Gtk.Button()
            button.set_size_request(180, 60)
            
            # Contenedor para ícono y texto
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            hbox.set_margin_start(5)
            hbox.set_margin_end(5)
            
            # Ícono
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
            
            # Texto
            button_label = Gtk.Label(label=label)
            button_label.set_halign(Gtk.Align.START)
            
            hbox.pack_start(icon, False, False, 0)
            hbox.pack_start(button_label, True, True, 0)
            
            button.add(hbox)
            button.connect("clicked", lambda _, link=url: webbrowser.open(link))
            
            box.pack_start(button, False, False, 0)
        
        return box

    def update_logo(self):
        try:
            logo = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                "/usr/share/yel-hello/icons/prog1.svg",
                width=self.logo_size,
                height=self.logo_size,
                preserve_aspect_ratio=True
            )
            self.logo_image.set_from_pixbuf(logo)
            self.logo_image.set_opacity(self.opacity)
        except GLib.Error:
            print("Error al cargar el logo. Verificar ruta.")

    def fade_in_logo(self):
        if self.opacity < 2:
            self.opacity += 0.04
            self.update_logo()
            return True
        return False

    def next_phrase(self):
        self.current_phrase = (self.current_phrase + 1) % len(self.slider_phrases)
        self.slider_label.set_text(self.slider_phrases[self.current_phrase])
        return True

    def create_autostart_file(self):
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        autostart_file = autostart_dir / "yelena-hello.desktop"
        
        autostart_content = f"""[Desktop Entry]
Type=Application
Name=Yelena Hello
Exec=python3 {os.path.abspath(__file__)}
Icon=system-software-install
Comment={self.translator.get('about_comments')}
X-GNOME-Autostart-enabled=true
"""
        autostart_file.write_text(autostart_content)

    def remove_autostart_file(self):
        autostart_file = Path.home() / ".config" / "autostart" / "yelena-hello.desktop"
        if autostart_file.exists():
            autostart_file.unlink()

    def show_about_dialog(self, _):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name("Yelena Hello")
        about_dialog.set_version("2.0 250425")
        about_dialog.set_comments(self.translator.get('about_comments'))
        about_dialog.set_website("https://github.com/CuerdOS")
        about_dialog.set_website_label("GitHub")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.set_authors([
            "Ale D.M", "Leo H. Pérez (GatoVerde95)", "Pablo G.", "Welkis",
            "GatoVerde95 Studios", "CuerdOS Community"
        ])
        about_dialog.set_copyright("© 2025 CuerdOS")
        
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale("/usr/share/yel-hello/icons/prog1.svg", 128, 128, True)
            about_dialog.set_logo(pixbuf)
        except GLib.Error:
            pass
            
        about_dialog.run()
        about_dialog.destroy()

    def on_close_clicked(self, _):
        self.destroy()
        
    def on_config_clicked(self, _):
        # Diálogo de configuración simplificado
        dialog = Gtk.Dialog(
            title=self.translator.get('config_title'),
            parent=self,
            flags=Gtk.DialogFlags.MODAL,
            buttons=(
                self.translator.get('btn_cancel'), Gtk.ResponseType.CANCEL,
                self.translator.get('btn_save'), Gtk.ResponseType.OK
            )
        )
        dialog.set_default_size(400, 150)
        
        content_area = dialog.get_content_area()
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)
        content_area.set_spacing(10)
        
        # Opciones de configuración
        
        # Autostart
        autostart_check = Gtk.CheckButton(label=self.translator.get('config_autostart'))
        autostart_check.set_active(self.config.get('autostart', True))
        content_area.pack_start(autostart_check, False, False, 0)
        
        # Selector de idioma
        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lang_label = Gtk.Label(label="Idioma/Language:")
        lang_box.pack_start(lang_label, False, False, 0)
        
        lang_combo = Gtk.ComboBoxText()
        for lang_code in self.translator.get_available_languages():
            lang_name = {"es": "Español", "en": "English", "pt": "Português", "it": "Italiano", "de": "Deutsch", "ja": "日本語", "ko": "한국어"}.get(lang_code, lang_code.upper())
            lang_combo.append(lang_code, lang_name)
        lang_combo.set_active_id(self.translator.language)  # Establecer idioma actual
        lang_box.pack_start(lang_combo, True, True, 0)
        
        content_area.pack_start(lang_box, False, False, 0)
        
        # Mostrar el diálogo
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            # Guardar configuración de autostart
            self.config['autostart'] = autostart_check.get_active()
            
            if autostart_check.get_active():
                self.create_autostart_file()
            else:
                self.remove_autostart_file()
            
            # Cambiar idioma si es necesario
            new_lang = lang_combo.get_active_id()
            if new_lang != self.translator.language:
                self.change_language(new_lang)
            
            # Guardar toda la configuración
            save_config(self.config)
                    
        dialog.destroy()


if __name__ == "__main__":
    win = WelcomeWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
