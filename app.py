from shiny import App, ui, reactive
import pandas as pd
from tabs import count_eggs, about

app_ui = ui.page_fluid(
    ui.h2("Countess"),
    ui.navset_tab(
        count_eggs.get_ui(),
        about.get_ui()
    )
)

def server(input, output, session):
    """
    Main server function for the Countess Shiny application.
    
    Initializes reactive values for storing application state and registers
    server logic for all tabs. Also includes a keep-alive mechanism to maintain
    the session connection.
    
    Args:
        input: Shiny input object containing user inputs
        output: Shiny output object for rendering UI elements
        session: Shiny session object for managing session state
    """
    # Reactive values for storing data
    counts = reactive.value(pd.DataFrame(columns=["image_name", "count"]))
    processed_image = reactive.value(None)
    processing_done_counter = reactive.value(0)  # Counter for signaling

    @reactive.effect
    def keep_alive():
        """
        Keeps the Shiny session alive by invalidating every 5 seconds.
        
        This prevents the session from timing out during long-running image
        processing operations.
        """
        # This will trigger every 5 seconds
        reactive.invalidate_later(5)
        print("Keeping session alive...")
    
    # Register server logic for each tab
    count_eggs.register_server(input, output, session, counts, processed_image, processing_done_counter)

app = App(app_ui, server)