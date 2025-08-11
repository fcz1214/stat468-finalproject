
from shiny import App, ui, render

# Minimal test app
app_ui = ui.page_fluid(
    ui.h1("Hello World"),
    ui.p("This is a test app"),
    ui.input_text("name", "Enter your name:", value="World"),
    ui.output_text_verbatim("greeting")
)

def server(input, output, session):
    @output
    @render.text
    def greeting():
        return f"Hello {input.name()}!"

app = App(app_ui, server)