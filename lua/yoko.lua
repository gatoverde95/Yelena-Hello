local lgi = require 'lgi'
local Gtk = lgi.Gtk
local Gio = lgi.Gio
local GdkPixbuf = lgi.GdkPixbuf

local WelcomeWindow = {}
WelcomeWindow.__index = WelcomeWindow

function WelcomeWindow:new()
    local self = setmetatable({}, WelcomeWindow)
    self.window = Gtk.Window {
        title = "Yelena Hello",
        border_width = 20,
        default_width = 600,
        default_height = 480,
        resizable = false,
        window_position = Gtk.WindowPosition.CENTER
    }

    local user_name = os.getenv("USER") or os.getenv("USERNAME")
    self.window.title = string.format("¡Hola, %s! - CuerdOS 1.3", user_name)

    local current_dir = debug.getinfo(1).source:match("@?(.*/)")
    local icon_file = current_dir .. "icon/prog1.svg"
    local icon_pixbuf
    pcall(function()
        icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_file)
        self.window:set_icon(icon_pixbuf)
    end)

    local logo_file = current_dir .. "icon/cuerdos.svg"
    local logo = Gtk.Image()
    pcall(function()
        logo:set_from_file(logo_file)
    end)

    self.welcome_label = Gtk.Label {
        halign = Gtk.Align.CENTER,
        line_wrap = true
    }

    self.buttons = {}
    self:load_languages(current_dir)

    self.mas_button = self:create_button_with_icon("icon/github.svg")
    self.sourceforge_button = self:create_button_with_icon("icon/sourceforge.svg")
    self.news_button = self:create_button_with_icon("icon/news.svg")
    self.wiki_button = self:create_button_with_icon("icon/wiki.svg")
    self.spins_button = self:create_button_with_icon("icon/spins.svg")
    self.dev_team_button = self:create_button_with_icon("icon/dev_team.svg")
    self.webpage_button = self:create_button_with_icon("icon/webpage.svg")
    self.feedback_button = self:create_button_with_icon("icon/feedback.svg")
    self.bauh_button = self:create_button_with_icon("icon/bauh.svg")

    self.autostart_switch = Gtk.Switch()
    self.autostart_switch.on_state_set = function(switch, state)
        self:on_autostart_switch_toggled(switch, state)
    end

    local close_button = Gtk.Button { label = ">>" }
    close_button.on_clicked = function()
        self:close_application()
    end

    self.language_store = Gtk.ListStore.new { GObject.Type.STRING }
    for language in pairs(self.buttons) do
        self.language_store:append { language }
    end

    self.language_combo = Gtk.ComboBox {
        model = self.language_store
    }
    local renderer_text = Gtk.CellRendererText()
    self.language_combo:pack_start(renderer_text, true)
    self.language_combo:add_attribute(renderer_text, "text", 0)

    self.language_combo.on_changed = function(combo)
        local index = combo:get_active()
        if index > -1 then
            local language = self.language_store:get_iter(index)
            language = language[1]
            self:update_button_labels(language)
            self.welcome_label:set_markup(self.buttons[language].description)
            self:save_language_setting(language)
        end
    end

    self:load_language_setting()
    self:load_autostart_setting()

    self.mas_button.on_clicked = function()
        self:open_url("https://github.com/CuerdOS")
    end
    self.sourceforge_button.on_clicked = function()
        self:open_url("https://sourceforge.net/projects/cuerdos/")
    end
    self.news_button.on_clicked = function()
        self:open_url("https://cuerdos.github.io/changelog_es.html#changelog")
    end
    self.wiki_button.on_clicked = function()
        self:open_url("https://cuerdoswiki.blogspot.com/")
    end
    self.spins_button.on_clicked = function()
        self:open_url("https://cuerdos.github.io/spins.html")
    end
    self.dev_team_button.on_clicked = function()
        self:open_url("https://cuerdos.github.io/index.html#descarga")
    end
    self.webpage_button.on_clicked = function()
        self:open_url("https://cuerdos.github.io/index.html")
    end
    self.feedback_button.on_clicked = function()
        self:open_url("https://t.me/+GibSWjFc89Q2ODU8")
    end
    self.bauh_button.on_clicked = function()
        self:open_bauh()
    end

    local button_grid = Gtk.Grid {
        column_homogeneous = true,
        row_homogeneous = true,
        column_spacing = 10
    }

    button_grid:attach(self.mas_button, 0, 0, 1, 1)
    button_grid:attach(self.sourceforge_button, 1, 0, 1, 1)
    button_grid:attach(self.bauh_button, 2, 0, 1, 1)
    button_grid:attach(self.news_button, 0, 1, 1, 1)
    button_grid:attach(self.wiki_button, 1, 1, 1, 1)
    button_grid:attach(self.spins_button, 2, 1, 1, 1)
    button_grid:attach(self.dev_team_button, 0, 2, 1, 1)
    button_grid:attach(self.webpage_button, 1, 2, 1, 1)
    button_grid:attach(self.feedback_button, 2, 2, 1, 1)

    -- Create menu bar
    local menu_bar = Gtk.MenuBar()

    -- Create the Help menu
    local help_menu = Gtk.Menu()
    local help_menu_item = Gtk.MenuItem { label = "Ayuda" }
    help_menu_item:set_submenu(help_menu)

    -- Create the About menu item
    local about_menu_item = Gtk.MenuItem { label = "Acerca de..." }
    about_menu_item.on_activate = function()
        self:show_about_dialog()
    end
    help_menu:append(about_menu_item)

    menu_bar:append(help_menu_item)

    local footer_box = Gtk.Box {
        orientation = Gtk.Orientation.HORIZONTAL,
        spacing = 10,
        self.language_combo,
        self.autostart_switch,
        close_button
    }

    local main_box = Gtk.Box {
        orientation = Gtk.Orientation.VERTICAL,
        spacing = 10,
        homogeneous = false,
        menu_bar,
        logo,
        self.welcome_label,
        button_grid,
        footer_box
    }

    self.window:add(main_box)
    self.window.on_destroy = Gtk.main_quit

    return self
end

function WelcomeWindow:create_button_with_icon(icon_path)
    local button = Gtk.Button()
    local icon = Gtk.Image()
    local icon_pixbuf
    pcall(function()
        icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
        -- Escalar el icono a 16x16
        local scaled_pixbuf = icon_pixbuf:scale_simple(16, 16, GdkPixbuf.InterpType.BILINEAR)
        icon:set_from_pixbuf(scaled_pixbuf)
    end)
    button:set_image(icon)
    return button
end

function WelcomeWindow:load_languages(current_dir)
    -- Load languages from the "languages" folder in the current directory
    local languages_dir = current_dir .. "languages/"
    local p = io.popen('ls "'..languages_dir..'"')
    for file_name in p:lines() do
        if file_name:match("%.json$") then
            local language = file_name:match("([^%.]+)"):capitalize()
            local f = io.open(languages_dir .. file_name, "r")
            if f then
                local content = f:read("*a")
                f:close()
                self.buttons[language] = json.decode(content)
            end
        end
    end
end

function WelcomeWindow:update_button_labels(language)
    local labels = self.buttons[language].buttons
    self.mas_button:set_label(labels[1])
    self.sourceforge_button:set_label(labels[2])
    self.news_button:set_label(labels[4])
    self.wiki_button:set_label(labels[5])
    self.spins_button:set_label(labels[6])
    self.dev_team_button:set_label(labels[7])
    self.webpage_button:set_label(labels[8])
    self.feedback_button:set_label(labels[9])
    self.bauh_button:set_label(labels[3])
end

function WelcomeWindow:open_bauh()
    os.execute("bauh")
end

function WelcomeWindow:open_url(url)
    Gio.AppInfo.launch_default_for_uri(url, nil)
end

function WelcomeWindow:show_about_dialog()
    local about_dialog = Gtk.AboutDialog {
        program_name = "Yelena Hello",
        version = "1.2 v100125a Elena",
        comments = "Bienvenida de CuerdOS GNU/Linux.",
        website = "https://github.com/CuerdOS",
        website_label = "GitHub",
        license_type = Gtk.License.GPL_3_0,
        authors = {
            "Ale D.M", "Leo H. Pérez (GatoVerde95)", "Pablo G.", "Welkis", "GatoVerde95 Studios", "CuerdOS Community"
        },
        copyright = "© 2025 CuerdOS"
    }
    local current_dir = debug.getinfo(1).source:match("@?(.*/)")
    local icon_file = current_dir .. "icon/prog1.svg"
    pcall(function()
        local icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_file)
        about_dialog:set_logo(icon_pixbuf)
    end)
    about_dialog:run()
    about_dialog:destroy()
end

function WelcomeWindow:close_application()
    self.window:destroy()
end

function WelcomeWindow:save_language_setting(language)
    local f = io.open("config.json", "w")
    if f then
        f:write(json.encode({ language = language }))
        f:close()
    end
end

function WelcomeWindow:load_language_setting()
    local f = io.open("config.json", "r")
    if f then
        local content = f:read("*a")
        f:close()
        local config = json.decode(content)
        local language = config.language or "Español"
        local iter = self.language_store:get_iter_first()
        local i = 0
        while iter do
            if self.language_store:get_value(iter, 0) == language then
                self.language_combo:set_active(i)
                self:update_button_labels(language)
                self.welcome_label:set_markup(self.buttons[language].description)
                break
            end
            i = i + 1
            iter = self.language_store:iter_next(iter)
        end
    end
end

function WelcomeWindow:load_autostart_setting()
    local autostart_file = os.getenv("HOME") .. "/.config/autostart/cuerdos.desktop"
    local f = io.open(autostart_file, "r")
    if f then
        f:close()
        self.autostart_switch:set_active(true)
    else
        self.autostart_switch:set_active(false)
    end
end

function WelcomeWindow:on_autostart_switch_toggled(switch, state)
    local autostart_file = os.getenv("HOME") .. "/.config/autostart/hello.desktop"
    if state then
        os.execute("mkdir -p " .. os.getenv("HOME") .. "/.config/autostart")
        local f = io.open(autostart_file, "w")
        if f then
            f:write("[Desktop Entry]\n")
            f:write("Type=Application\n")
            f:write("Exec=lua " .. debug.getinfo(1).source:match("@?(.*/)") .. "hello.lua\n")
            f:write("Hidden=false\n")
            f:write("NoDisplay=false\n")
            f:write("X-GNOME-Autostart-enabled=true\n")
            f:write("Name=CuerdOS Yelena Hello\n")
            f:write("Comment=Welcome to CuerdOS\n")
            f:close()
        end
    else
        os.remove(autostart_file)
    end
end

function main()
    local app = WelcomeWindow:new()
    app.window:show_all()
    Gtk.main()
end

main()
