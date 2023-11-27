library(shiny)
library(DT)

# Load your CSV data
csv_data <- read.csv("sequencing_statistics.csv")

# Define the UI
ui <- fluidPage(
  titlePanel("CSV Table Viewer"),
  mainPanel(
    # Output: Display the DataTable
    DTOutput("table")
  )
)

# Define the server logic
server <- function(input, output) {
  # Render the DataTable with the loaded CSV data
  output$table <- renderDT({
    datatable(csv_data)
  })
}

# Run the Shiny app
shinyApp(ui, server)