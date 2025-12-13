from shiny import ui

def get_ui():
    """
    Returns the UI components for the About tab.
    
    Creates a navigation panel containing information about the Countess
    application, including its purpose and functionality.
    
    Returns:
        ui.nav_panel: A Shiny navigation panel containing the About tab UI
    """
    return ui.nav_panel(
        "About",
        ui.h3("About Countess"),
        ui.p("Countess is an application for automatically counting eggs in images using machine learning."),
        ui.p("This tool helps researchers and professionals quickly analyze large batches of images to count eggs with high accuracy."),
    )

