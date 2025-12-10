import gi
import os
import subprocess
import webbrowser
import math
import sys
from pathlib import Path
import shlex 
import time
import locale

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib

from translations import Translator
from config import load_config, save_config 

class WelcomeWindow(Gtk.Window):
    
    def _check_autostart_status(self):
        """
        Detecta el estado de Autostart:
        - El inicio automático está ACTIVO si el archivo .desktop EXISTE en ~/.config/autostart/.
        - Está DESACTIVADO si el archivo NO EXISTE.
        """
        desktop_dir = Path.home() / ".config" / "autostart"
        desktop_file = desktop_dir / "yelena-hello.desktop"

        # Está activo si el archivo existe.
        is_active = desktop_file.exists()
        return is_active

    def _get_system_language(self):
        """
        Detecta el idioma preferido del sistema y lo mapea a uno disponible.
        Prioriza las variables de entorno LANG y LC_ALL sobre locale.getlocale().
        """
        supported_langs = ["es", "en", "pt", "it", "de", "ja", "ko", "ca"]
        
        system_locale = None
        
        # 1. PRIORIDAD: Leer variables de entorno (más confiables)
        for env_var in ['LANG', 'LC_ALL', 'LC_MESSAGES']:
            system_locale = os.environ.get(env_var)
            if system_locale:
                print(f"DIAGNOSTICO: Idioma detectado desde {env_var}: {system_locale}")
                break
        
        # 2. Intento con locale.getlocale() (fallback)
        if not system_locale or system_locale == 'C':
            try:
                system_locale = locale.getlocale()[0]
                if system_locale and system_locale != 'C':
                    print(f"DIAGNOSTICO: Idioma detectado desde locale.getlocale(): {system_locale}")
            except Exception:
                pass

        # 3. Intento con locale.getdefaultlocale() (último recurso)
        if not system_locale or system_locale == 'C':
            try:
                system_locale = locale.getdefaultlocale()[0]
                if system_locale and system_locale != 'C':
                    print(f"DIAGNOSTICO: Idioma detectado desde locale.getdefaultlocale(): {system_locale}")
            except Exception:
                pass
        
        # 4. Extraer código de idioma
        if system_locale and system_locale != 'C':
            try:
                # Extraer solo el código de dos letras, e.g., 'ca' de 'ca_ES.UTF-8'
                lang_code = system_locale.split('_')[0].split('.')[0].lower()
                
                if lang_code in supported_langs:
                    print(f"DIAGNOSTICO: Código de idioma extraído: {lang_code}")
                    return lang_code
            except Exception as e:
                print(f"DIAGNOSTICO: Error al extraer código de idioma: {e}")
        
        # Fallback si todo falla
        print("DIAGNOSTICO: Usando idioma por defecto: es")
        return 'es'


    def __init__(self):
        
        # --- LÓGICA DE INICIO (CRÍTICA) ---
        self.config = load_config()
        
        # 1. Detección y Configuración de Idioma
        # CAMBIO: SIEMPRE detecta el idioma del sistema y sobrescribe la configuración
        system_lang = self._get_system_language()
        print(f"Idioma del sistema detectado: {system_lang}")
        
        # Sobrescribir la configuración con el idioma del sistema
        self.config['language'] = system_lang
        save_config(self.config)
        print(f"Configuración actualizada con idioma: {system_lang}")
        
        # Cargar el traductor con el idioma del sistema
        self.translator = Translator(system_lang)

        # 2. Detección y Sincronización de Autostart
        current_autostart_status = self._check_autostart_status()
        
        if self.config.get('autostart', True) != current_autostart_status:
            print(f"Estado de Autostart detectado ({current_autostart_status}) difiere de la config guardada. Actualizando y guardando.")
            self.config['autostart'] = current_autostart_status
            save_config(self.config)
        # --- FIN LÓGICA DE INICIO ---
        
        super().__init__(title="Yelena Hello") 
        self.set_default_size(600, 420)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(10)
        
        self.logo_opacity = 1.0
        self.current_phrase = 0
        self.logo_scale = 1.0
        self.click_count = 0
        
        self.title_label = None
        self.subtitle_label = None
        self.logo_event_box = None
        self.bottom_buttons = []
        
        self.logo_paths = [
            "/usr/share/yel-hello/icons/hello.svg",
            "icons/hello.svg",
            "hello.svg",
            "./icons/hello.svg",
            os.path.join(os.path.dirname(__file__), "icons", "hello.svg"),
            os.path.join(os.path.dirname(__file__), "hello.svg")
        ]
        self.logo_found = False
        self.current_logo_path = None
        self.logo_pixbuf = None
        
        self._find_logo()
        
        if self.current_logo_path:
            self._set_icon_from_file(self.current_logo_path)
            
        self.setup_ui()
        self.start_animations()

    def _find_logo(self):
        """Find logo file and load it"""
        for path in self.logo_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path) and os.path.isfile(abs_path):
                try:
                    test_pixbuf = GdkPixbuf.Pixbuf.new_from_file(abs_path)
                    if test_pixbuf:
                        self.current_logo_path = abs_path
                        self.logo_found = True
                        return
                except Exception:
                    pass
        pass

    def _set_icon_from_file(self, path):
        """Set window icon from file"""
        try:
            self.set_icon_from_file(path)
        except Exception:
            pass

    def setup_ui(self):
        """Configuración de la interfaz de usuario"""
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.props.title = "Yelena Hello"
        self.set_titlebar(header_bar)
        
        settings_button = Gtk.Button.new_from_icon_name("preferences-system", Gtk.IconSize.MENU)
        settings_button.set_tooltip_text(self.translator.get('btn_config'))
        settings_button.connect("clicked", self.on_config_clicked)
        header_bar.pack_end(settings_button)
        
        menu_button = Gtk.MenuButton()
        menu_button.set_image(Gtk.Image.new_from_icon_name("start", Gtk.IconSize.MENU))
        menu_button.set_popup(self.create_menu_popup())
        header_bar.pack_end(menu_button)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)
        
        components = [
            (self.create_header(), False, False, 0),
            (self.create_central_content(), True, True, 10),
            (self.create_phrase_slider(), False, False, 0),
            (self.create_bottom_buttons(), False, False, 0)
        ]
        
        for component, expand, fill, padding in components:
            main_box.pack_start(component, expand, fill, padding)
            
    def create_menu_popup(self):
        """Create popup menu for the HeaderBar"""
        menu = Gtk.Menu()
        menu_items = [
            (self.translator.get('menu_news'), lambda: webbrowser.open("https://cuerdos.github.io/changelog_es.html")),
            (self.translator.get('menu_search'), lambda: webbrowser.open("https://cuerdos.github.io/search.html")),
            (None, None), 
            (self.translator.get('menu_docs'), lambda: webbrowser.open("https://cuerdoswiki.blogspot.com/")),
            (None, None), 
            (self.translator.get('menu_about'), self.show_about_dialog),
            (self.translator.get('menu_quit'), self.destroy)
        ]

        for item in menu_items:
            label, callback = item
            if label is None:
                menu.append(Gtk.SeparatorMenuItem())
            else:
                menu_entry = Gtk.MenuItem(label=label)
                menu_entry.connect("activate", lambda _, cb=callback: cb())
                menu.append(menu_entry)
        
        menu.show_all()
        return menu

    def create_header(self):
        """Create header with title and subtitle"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        header_box.set_margin_top(10)
        header_box.set_margin_bottom(15)
        
        title_text = self.translator.get('welcome_title')
        self.title_label = Gtk.Label(label=f"<span size='xx-large' weight='bold'>{title_text}</span>",
                            use_markup=True, halign=Gtk.Align.CENTER)
        header_box.pack_start(self.title_label, False, False, 0)

        subtitle_text = self.translator.get('welcome_subtitle')
        self.subtitle_label = Gtk.Label(label=f"<span size='large' style='italic'>{subtitle_text}</span>",
                            use_markup=True, halign=Gtk.Align.CENTER)
        header_box.pack_start(self.subtitle_label, False, False, 0)
        
        return header_box

    def create_central_content(self):
        """Create central content with buttons and animated logo"""
        central_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        central_box.set_margin_top(10)
        central_box.set_margin_bottom(10)
        
        left_buttons = [
            (self.translator.get('btn_official_page'), "web-browser", lambda: webbrowser.open("https://cuerdos.github.io")),
            (self.translator.get('btn_app_store'), "applications-accessories", lambda: self.run_command("yel-store")),
            (self.translator.get('btn_feedback'), "mail-send", lambda: webbrowser.open("https://t.me/+GibSWjFc89Q2ODU8")),
            (self.translator.get('btn_system_info'), "dialog-information", lambda: self.run_command("eclair"))
        ]
        
        right_buttons = [
            (self.translator.get('btn_system_update'), "system-software-update", lambda: self.run_command("cuerdtoken")),
            (self.translator.get('btn_browser'), "web-browser", lambda: self.run_command("xdg-open https://cuerdos.github.io")),
            (self.translator.get('btn_recovery_manager'), "drive-harddisk", lambda: self.run_command("timeshift-launcher")),
            (self.translator.get('btn_wiki'), "help-browser", lambda: webbrowser.open("https://cuerdoswiki.blogspot.com/"))
        ]
        
        central_box.pack_start(self.create_button_group(left_buttons), False, True, 0)
        central_box.pack_start(self.create_logo_widget(), True, True, 0)
        central_box.pack_start(self.create_button_group(right_buttons), False, True, 0)
        
        return central_box
        
    def create_logo_widget(self):
        """Create interactive logo widget (AHORA SOLO VISUAL)"""
        self.logo_event_box = Gtk.EventBox()
        self.logo_event_box.set_size_request(250, 250)
        
        if not self.logo_found:
            placeholder = Gtk.Label()
            placeholder.set_markup(f"<span size='x-large' weight='bold'>🖥️\n{self.translator.get('logo_not_found', 'Logo no encontrado')}</span>")
            placeholder.set_halign(Gtk.Align.CENTER)
            placeholder.set_valign(Gtk.Align.CENTER)
            self.logo_event_box.add(placeholder)
        else:
            self.logo_image = Gtk.Image()
            self.logo_event_box.add(self.logo_image)
            self.update_logo() 
            
        self.logo_event_box.set_tooltip_text(self.translator.get('logo_static_tooltip', 'Logo estático'))
        
        return self.logo_event_box

    def create_button_group(self, button_data):
        """Create a group of buttons"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        for label, icon_name, callback in button_data:
            button = Gtk.Button()
            button.set_size_request(180, 60)
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            hbox.set_margin_start(5)
            hbox.set_margin_end(5)
            
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
            button_label = Gtk.Label(label=label)
            button_label.set_halign(Gtk.Align.START)
            
            hbox.pack_start(icon, False, False, 0)
            hbox.pack_start(button_label, True, True, 0)
            
            button.add(hbox)
            button.connect("clicked", lambda _, cb=callback: cb())
            
            button.connect("enter-notify-event", lambda w, e: w.set_opacity(0.8))
            button.connect("leave-notify-event", lambda w, e: w.set_opacity(1.0))
            
            box.pack_start(button, False, False, 0)
        
        return box

    def create_phrase_slider(self):
        """Create phrase slider"""
        self.slider_phrases = self.translator.get('slider_phrases')
        
        slider_frame = Gtk.Frame()
        slider_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        
        self.slider_label = Gtk.Label(
            label=self.slider_phrases[self.current_phrase],
            halign=Gtk.Align.CENTER
        )
        
        for margin in ['top', 'bottom', 'start', 'end']:
            getattr(self.slider_label, f'set_margin_{margin}')(5 if margin in ['top', 'bottom'] else 10)
        
        slider_frame.add(self.slider_label)
        return slider_frame

    def create_bottom_buttons(self):
        """Create bottom button bar"""
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        btn_cuerdos_news = Gtk.Button(label=self.translator.get('btn_cuerdos_news', "CuerdOS Noticias"))
        btn_cuerdos_news.connect("clicked", lambda w: webbrowser.open("https://t.me/CuerdOS_Noticias"))
        btn_cuerdos_news.connect("enter-notify-event", lambda w, e: w.set_opacity(0.8))
        btn_cuerdos_news.connect("leave-notify-event", lambda w, e: w.set_opacity(1.0))
        button_box.pack_start(btn_cuerdos_news, False, False, 0)
        
        spacer = Gtk.Label(label="")
        button_box.pack_start(spacer, True, True, 0) 

        buttons = [
            ("view-refresh", 'btn_news', lambda: webbrowser.open("https://cuerdos.github.io/changelog_es.html")),
            (None, 'btn_close', self.destroy)
        ]
        
        self.bottom_buttons = []

        for icon_name, tooltip_key, callback in buttons:
            button = Gtk.Button()
            tooltip = self.translator.get(tooltip_key) 
            
            if icon_name:
                icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
                button.add(icon)
                button.set_tooltip_text(tooltip)
            else:
                button.set_label(tooltip)
            
            button.connect("clicked", lambda _, cb=callback: cb())
            button.connect("enter-notify-event", lambda w, e: w.set_opacity(0.8))
            button.connect("leave-notify-event", lambda w, e: w.set_opacity(1.0))
            
            button_box.pack_start(button, False, False, 0)
            self.bottom_buttons.append((button, icon_name, tooltip_key))
        
        return button_box

    def run_command(self, command):
        """Execute command independently"""
        try:
            command_list = shlex.split(command)
            subprocess.Popen(command_list, start_new_session=True)
        except FileNotFoundError:
            command_name = shlex.split(command)[0]
            print(f"{self.translator.get('error_executing')} {command}: [Errno 2] No existe el fichero o el directorio: '{command_name}'")
        except Exception as e:
            print(f"{self.translator.get('error_executing')} {command}: {e}")

    def update_logo(self):
        """Update logo - SIMPLIFICADA PARA NO TENER ANIMACIONES"""
        if not self.logo_found or not self.current_logo_path or not hasattr(self, 'logo_image'):
            return
            
        try:
            size = 250
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.current_logo_path, size, size, True)
            
            self.logo_image.set_from_pixbuf(pixbuf)
            
        except Exception as e:
            print(f"Error updating logo: {e}")

    def start_animations(self):
        """Start animations - SE ELIMINA _fade_in_logo"""
        GLib.timeout_add(4000, self._next_phrase) # Mantener la rotación de frases

    def _next_phrase(self):
        """Rotate phrases"""
        if hasattr(self, 'slider_phrases'):
            self.current_phrase = (self.current_phrase + 1) % len(self.slider_phrases)
            self.slider_label.set_text(self.slider_phrases[self.current_phrase])
        return True

    def setup_autostart(self):
        """
        [OBJETIVO: ACTIVAR INICIO AUTOMÁTICO]
        Crea el archivo .desktop en ~/.config/autostart/ para activarlo.
        """
        if not self.config.get('autostart', True):
            return
            
        desktop_dir = Path.home() / ".config" / "autostart"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        desktop_file = desktop_dir / "yelena-hello.desktop"

        # Obtenemos la ruta de ejecución correcta 
        app_path = Path("/usr/bin/yelena-hello")
        if not app_path.exists():
             app_path = Path(os.path.abspath(__file__))
        
        exec_command = str(app_path)
        
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=Yelena Hello
Comment=CuerdOS Welcome Application
Exec={exec_command}
Icon=yelena-hello
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
"""
        try:
            print(f"Autostart ON: Activando el inicio automático al crear el archivo: {desktop_file}")
            desktop_file.write_text(desktop_content, encoding='utf-8')
        except Exception as e:
            print(f"Error al crear el archivo .desktop local (setup_autostart): {e}")
            
    def remove_autostart(self):
        """
        [OBJETIVO: DESACTIVAR INICIO AUTOMÁTICO]
        Elimina el archivo .desktop de ~/.config/autostart/ para desactivarlo.
        """
        # 1. Limpieza de systemd (para compatibilidad/migración)
        service_name = "yelena-hello.service"
        systemd_dir = Path.home() / ".config" / "systemd" / "user"
        service_file = systemd_dir / service_name

        try:
            subprocess.run(["systemctl", "--user", "stop", service_name], check=False, stderr=subprocess.DEVNULL) 
            subprocess.run(["systemctl", "--user", "disable", service_name], check=False, stderr=subprocess.DEVNULL)
            if service_file.exists():
                print(f"Limpiando archivo systemd remanente: {service_file}")
                service_file.unlink()
        except Exception as e:
            print(f"Error al limpiar systemd autostart: {e}") 

        # 2. Eliminación del archivo .desktop local
        desktop_dir = Path.home() / ".config" / "autostart"
        desktop_file = desktop_dir / "yelena-hello.desktop"
        
        try:
            if desktop_file.exists():
                print(f"Autostart OFF: Desactivando el inicio automático al eliminar el archivo: {desktop_file}")
                desktop_file.unlink()
        except Exception as e:
            print(f"Error al eliminar el archivo .desktop local (remove_autostart): {e}")


    def change_language(self, lang_code):
        """Change application language and restart the app."""
        if self.translator.set_language(lang_code):
            self.config['language'] = lang_code
            save_config(self.config)
            
            time.sleep(0.1) 
            
            dialog = Gtk.MessageDialog(
                transient_for=self, modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=self.translator.get('language_changed', 'Language changed')
            )
            dialog.format_secondary_text(self.translator.get('restart_app', 'The application will now restart to apply the new language.'))
            dialog.run()
            dialog.destroy()
            
            python = sys.executable
            os.execv(python, [python, os.path.abspath(__file__)])
            
    def show_about_dialog(self):
        """Show about dialog"""
        about = Gtk.AboutDialog()
        about.set_transient_for(self)
        about.set_modal(True)
        about.set_program_name("Yelena Hello")
        about.set_version("2.4.3")
        about.set_comments(self.translator.get('about_comments'))
        about.set_website("https://github.com/CuerdOS")
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_copyright("© 2025 CuerdOS")
        
        if self.current_logo_path:
            self._set_icon_for_dialog(about, self.current_logo_path, 128)
        about.run()
        about.destroy()

    def _set_icon_for_dialog(self, dialog, path, size):
        """Set icon for dialog"""
        try:
            if Path(path).exists():
                logo = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, size, size, True)
                dialog.set_logo(logo)
        except Exception:
            pass

    def on_config_clicked(self, widget):
        """Show configuration dialog"""
        dialog = Gtk.Dialog(
            title=self.translator.get('config_title'),
            parent=self, 
            modal=True, 
            buttons=(
                self.translator.get('btn_cancel'), Gtk.ResponseType.CANCEL,
                self.translator.get('btn_save'), Gtk.ResponseType.OK
            )
        )
        dialog.set_default_size(400, 150)
        
        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_border_width(10)
        
        # Autostart checkbox: Usa el valor de la configuración cargado que ya fue detectado
        autostart_check = Gtk.CheckButton(label=self.translator.get('config_autostart'))
        autostart_check.set_active(self.config.get('autostart', True))
        content.pack_start(autostart_check, False, False, 0)
        
        # Language selector
        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lang_label = Gtk.Label(label="Idioma/Language:")
        lang_combo = Gtk.ComboBoxText()
        
        languages = [("es", "Español"), ("en", "English"), ("pt", "Português"), 
                    ("it", "Italiano"), ("de", "Deutsch"), ("ja", "日本語"), 
                    ("ko", "한국어"), ("ca", "Català")]
        
        for code, name in languages:
            lang_combo.append(code, name)
        lang_combo.set_active_id(self.translator.language)
        
        lang_box.pack_start(lang_label, False, False, 0)
        lang_box.pack_start(lang_combo, True, True, 0)
        content.pack_start(lang_box, False, False, 0)
        
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            self.config['autostart'] = autostart_check.get_active()
            
            # Aplica el cambio de autostart
            if autostart_check.get_active():
                self.setup_autostart()
            else:
                self.remove_autostart()
            
            new_lang = lang_combo.get_active_id()
            if new_lang != self.translator.language:
                self.change_language(new_lang)
            else:
                save_config(self.config)
        
        dialog.destroy()

if __name__ == "__main__":
    win = WelcomeWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()