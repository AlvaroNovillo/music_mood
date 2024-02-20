library(shiny)
library(flexdashboard)
library(ggplot2)
library(shinycssloaders)

library(shinythemes)
fluidPage(
  theme = shinytheme("united"),
  titlePanel("Mood-Based Song Classifier"),
  sidebarLayout(
    sidebarPanel(
      textInput("input_value", "Enter artist name or playlist link:"),
      actionButton("submit_button", "Submit")
    ),
    mainPanel(
      conditionalPanel(
        condition = "input.submit_button > 0",
        withSpinner(plotOutput("mood_distribution_plot"), color="#0dc5c1")
      ),
      conditionalPanel(
        condition = "input.submit_button > 0",
        withSpinner(plotOutput("radar_chart"), color="#0dc5c1")
      )
    )
  )
)

