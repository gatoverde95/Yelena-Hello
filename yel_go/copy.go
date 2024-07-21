package main

import (
    "github.com/therecipe/qt/core"
    "github.com/therecipe/qt/gui"
    "github.com/therecipe/qt/widgets"
    "os"
)

func main() {
    // Inicializar el entorno de Qt
    widgets.NewQApplication(len(os.Args), os.Args)

    // Crear una nueva ventana
    window := widgets.NewQMainWindow(nil, 0)
    window.SetWindowTitle("CuerdOS Yelena Hello 1.0 Katie")
    window.SetFixedSize2(600, 400)
    window.SetWindowFlag(core.Qt__WindowStaysOnTopHint, true)

    // Crear un widget central
    centralWidget := widgets.NewQWidget(nil, 0)
    window.SetCentralWidget(centralWidget)

    // Crear un layout vertical
    layout := widgets.NewQVBoxLayout()

    // Cargar y configurar el icono
    iconFile := "cuerdos.svg"
    icon := gui.NewQIcon5(iconFile)
    window.SetWindowIcon(icon)

    // Crear y configurar la imagen del logo
    logoFile := "cuerdos.svg"
    logoPixmap := gui.NewQPixmapFromFile(logoFile, nil)
    logoLabel := widgets.NewQLabel(nil, 0)
    logoLabel.SetPixmap(logoPixmap)

    // Crear y configurar la etiqueta de bienvenida
    welcomeLabel := widgets.NewQLabel(nil, 0)
    welcomeLabel.SetText("<span style='font-size: x-large; font-weight: bold; color: #333333;'>¡Bienvenido a <b>CuerdOS</b>!</span><br/><br/>Bienvenido a CuerdOS GNU/Linux, Optimizado hasta el ultimo pixel para ti.")
    welcomeLabel.SetAlignment(core.Qt__AlignCenter)

    // Crear botones
    buttonLabels := []string{"Más...", "Sourceforge", "Acerca de Yelena", "Novedades", "Wiki", "Spins", "Dev. Team", "Página Web", "CuerdOS Feedback"}
    buttonLayout := widgets.NewQGridLayout()

    for i, label := range buttonLabels {
        button := widgets.NewQPushButton2(label, nil)
        buttonLayout.AddWidget(button, i/3, i%3, 0)
    }

    // Botón de cerrar
    closeButton := widgets.NewQPushButton2("Cerrar", nil)
    closeButton.ConnectClicked(func(checked bool) {
        widgets.QApplication_Quit()
    })

    // Crear un layout horizontal para los botones y el selector de idioma
    footerBox := widgets.NewQHBoxLayout()
    footerBox.AddWidget(closeButton, 0, 0)
    
    // Agregar todos los widgets al layout principal
    layout.AddWidget(logoLabel, 0, 0)
    layout.AddWidget(welcomeLabel, 0, 0)
    layout.AddLayout(buttonLayout, 0)
    layout.AddLayout(footerBox, 0)
    
    // Aplicar el layout al widget central
    centralWidget.SetLayout(layout)
    
    // Mostrar la ventana
    window.Show()

    // Ejecutar la aplicación
    widgets.QApplication_Exec()
}

