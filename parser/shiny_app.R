library(shiny)
library(shinydashboard)
library(DT)
library(ggplot2)
library(plotly)

# Load your CSV data
csv_data <- read.csv("sequencing_statistics.csv")

# Define the UI
ui <- dashboardPage(
  dashboardHeader(title = "CSV Table Viewer with Plots"),
  dashboardSidebar(
    selectInput("plot_type", "Choose Plot Type",
                choices = c("Scatter Plot", "Bar Plot"),
                selected = "Scatter Plot"),
    dateRangeInput("date_range_filter", "Date Range Filter", start = "2022-01-01", end = format(Sys.Date(), "%Y-%m-%d")),
    checkboxGroupInput("sequencer_filter", "Sequencer Filter", choices = unique(csv_data$Sequencer), selected = unique(csv_data$Sequencer)),
    actionButton("reset_filters", "Reset Filters")
  ),
  dashboardBody(
    fluidRow(
      tabsetPanel(
        tabPanel(
          title = "q 30",
          icon = icon("chart-line"),
          plotlyOutput("selected_plot")
        ),
        tabPanel(
          title = "Coefficient of Variation",
          icon = icon("chart-line"),
          plotlyOutput("selected_plot_2")
        ),
        tabPanel(
          title = "Total Read Count",
          icon = icon("chart-line"),
          plotlyOutput("selected_plot_3")
        ),
        # New tab panels
        tabPanel(
          title = "Undetermined Reads Percentage",
          icon = icon("chart-line"),
          plotlyOutput("selected_plot_4")
        ),
        tabPanel(
          title = "Read to Expected Clusters Ratio",
          icon = icon("chart-line"),
          plotlyOutput("selected_plot_5")
        ),
      )
    ),
    tags$hr(), # Add a horizontal line for visual separation
    tags$hr(),
    tags$hr(),
    tags$hr(),
    fluidRow(
      box(
        title = "Look Up Table",
        status = "info",
        solidHeader = TRUE,
        width = 12, # Set the width to 12 to take the entire row
        DTOutput("selected_columns_table"),
        style = "overflow-x: auto;" # Add horizontal scrolling
      )
    ),
    tags$hr(), # Add a horizontal line for visual separation
    fluidRow(
      box(
        title = "Data Table",
        status = "info",
        solidHeader = TRUE,
        width = 12, # Set the width to 12 to take the entire row
        DTOutput("table"),
        style = "overflow-x: auto;" # Add horizontal scrolling
      )
    )
  )
)

# Define the server logic
server <- function(input, output, session) {
  # Reactive values for date and sequencer filtering
  date_range_selected <- reactiveVal(NULL)
  sequencer_selected <- reactiveVal(unique(csv_data$Sequencer))
  
  observeEvent(input$date_range_filter, {
    date_range_selected(input$date_range_filter)
  })
  
  observeEvent(input$sequencer_filter, {
    sequencer_selected(input$sequencer_filter)
  })
  
  observeEvent(input$reset_filters, {
    date_range_selected(NULL)
    sequencer_selected(unique(csv_data$Sequencer))
  })
  
  # Render the DataTable with the loaded CSV data
  output$table <- renderDT({
    filtered_data <- csv_data
    if (!is.null(date_range_selected())) {
      filtered_data <- subset(filtered_data, Date >= date_range_selected()[1] & Date <= date_range_selected()[2])
    }
    if (!is.null(sequencer_selected())) {
      filtered_data <- subset(filtered_data, Sequencer %in% sequencer_selected())
    }
    datatable(filtered_data)
  })
  
  # Render the selected columns table
  output$selected_columns_table <- renderDT({
    selected_columns <- c("Project.Name", "Date", "Sequencer", "most.common.undetermined.barcode", "undetermined.reads.percentage")  # Add the columns you want to display
    filtered_data <- csv_data
    if (!is.null(date_range_selected())) {
      filtered_data <- subset(filtered_data, Date >= date_range_selected()[1] & Date <= date_range_selected()[2])
    }
    if (!is.null(sequencer_selected())) {
      filtered_data <- subset(filtered_data, Sequencer %in% sequencer_selected())
    }
    datatable(filtered_data[, selected_columns, drop = FALSE])
  })
  
  # Render the selected plot based on user input (Plot 1)
  output$selected_plot <- renderPlotly({
    render_selected_plot("q_30", "q30", date_range_selected(), sequencer_selected())
  })
  
  # Render the selected plot based on user input (Plot 2)
  output$selected_plot_2 <- renderPlotly({
    render_selected_plot("cv", "coefficient of variation", date_range_selected(), sequencer_selected())
  })
  
  # Render the selected plot based on user input (Plot 3)
  output$selected_plot_3 <- renderPlotly({
    render_selected_plot("total.read.count", "Read Count", date_range_selected(), sequencer_selected())
  })
  # Render the selected plot based on user input (Plot 4)
  output$selected_plot_4<- renderPlotly({
    render_selected_plot("undetermined.reads.percentage", "Percentage", date_range_selected(), sequencer_selected())
  })
  
  # Render the selected plot based on user input (Plot 5)
  output$selected_plot_5 <- renderPlotly({
    render_selected_plot("ratio_totalReadCount_expectedCluster", "Ratio", date_range_selected(), sequencer_selected())
  })
  
  # Function to render selected plot
  render_selected_plot <- function(y_variable, y_axis_label, selected_date_range, selected_sequencers) {
    filtered_data <- csv_data
    if (!is.null(selected_date_range)) {
      filtered_data <- subset(filtered_data, Date >= selected_date_range[1] & Date <= selected_date_range[2])
    }
    if (!is.null(selected_sequencers)) {
      filtered_data <- subset(filtered_data, Sequencer %in% selected_sequencers)
    }
    
    color_variable <- "Sequencer"  # Specify the column for coloring
    
    if (input$plot_type == "Scatter Plot") {
      p <- ggplot(filtered_data, aes(x = Date, y = !!sym(y_variable), text = Project.Name, color = !!sym(color_variable))) +
        geom_point() +
        labs(title = "Scatter Plot", x = "X Axis", y = y_axis_label) +
        theme(axis.text.x = element_text(angle = 90, hjust = 1))
    } else if (input$plot_type == "Bar Plot") {
      p <- ggplot(filtered_data, aes(x = Date, y = !!sym(y_variable), text = Project.Name, fill = !!sym(color_variable))) +
        geom_bar(stat = "identity") +
        labs(title = "Bar Plot", x = "X Axis", y = y_axis_label) +
        theme(axis.text.x = element_text(angle = 90, hjust = 1))
    }
    
    ggplotly(p, tooltip = "text", width = 1000, height = 500, dynamicTicks = TRUE, margin = list(l = 0, r = 0, b = 0, t = 0))
  }
}

# Run the Shiny app
shinyApp(ui, server)
