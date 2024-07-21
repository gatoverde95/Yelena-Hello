library(RGtk2)

# Define the main function
main <- function() {
  # Create a new window
  window <- gtkWindow(title = "CuerdOS Yelena Hello 1.0 Katie", 
                      width = 600, 
                      height = 400, 
                      window.position = "center")
  
  # Set border width
  gtkContainerSetBorderWidth(window, 20)
  
  # Create a logo image
  logo_file <- "cuerdos.svg"
  logo_image <- gtkImageNewFromFile(logo_file)
  
  # Create a welcome label
  welcome_label <- gtkLabel()
  gtkLabelSetMarkup(welcome_label, "<span size='x-large' weight='bold' foreground='#333333'>¡Bienvenido a <b>CuerdOS</b>!</span>\n\nBienvenido a CuerdOS GNU/Linux, Optimizado hasta el ultimo pixel para ti.")
  gtkWidgetSetHalign(welcome_label, "center")
  
  # Create buttons
  button_labels <- c("Más...", "Sourceforge", "Acerca de Yelena", "Novedades", "Wiki", "Spins", "Dev. Team", "Página Web", "CuerdOS Feedback")
  buttons <- lapply(button_labels, gtkButtonNewWithLabel)
  
  # Close button
  close_button <- gtkButtonNewWithLabel("Cerrar")
  
  # Create a box layout
  vbox <- gtkVBox()
  
  # Add the logo, welcome label, and buttons to the box
  gtkBoxPackStart(vbox, logo_image, expand = TRUE, fill = TRUE, padding = 0)
  gtkBoxPackStart(vbox, welcome_label, expand = TRUE, fill = TRUE, padding = 0)
  
  # Create a grid layout for buttons
  grid <- gtkTable(nrows = 3, ncols = 3, homogeneous = TRUE)
  for (i in seq_along(buttons)) {
    gtkTableAttach(grid, buttons[[i]], (i-1) %% 3, (i %% 3), floor((i-1) / 3), (floor((i-1) / 3) + 1), xpadding = 10, ypadding = 10)
  }
  
  # Add the grid to the box
  gtkBoxPackStart(vbox, grid, expand = TRUE, fill = TRUE, padding = 0)
  
  # Add the close button to the box
  gtkBoxPackEnd(vbox, close_button, expand = FALSE, fill = FALSE, padding = 0)
  
  # Set the box as the main container
  gtkContainerAdd(window, vbox)
  
  # Show all widgets
  gtkWidgetShowAll(window)
  
  # Connect the close button to the window destroy event
  gSignalConnect(close_button, "clicked", function(button) {
    gtkWidgetDestroy(window)
  })
  
  # Start the GTK main loop
  gtkMain()
}

# Run the main function
main()

