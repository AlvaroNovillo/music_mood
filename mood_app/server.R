

library(shiny)
library(flexdashboard)
library(ggplot2)
library(reticulate)
library(fmsb)
library(dplyr)
library(tidyr)



# Set graphic colors
library(RColorBrewer)
coul <- brewer.pal(4, "Spectral")
colors_border <- coul
library(scales)
colors_in <- alpha(coul,0.4)


function(input, output) {
  observeEvent(input$submit_button, {
    # Execute Python script with input value and capture stdout

    reticulate::source_python("spoty_scrapper.py")
    python_output <- main(input$input_value)

    
    # Load the trained model
    log_fit <- readRDS("trained_model.rds")
    
    # Predict mood for output songs
    music_data <- as.data.frame(jsonlite::fromJSON(python_output))
    predicted_mood <- predict(log_fit, newdata = music_data)
    
    # Add predicted mood to output data
    music_data$mood <- predicted_mood
    
    
    # Perform data processing and visualization
    
    # Plot distribution of songs across different moods
    mood_counts <- table(music_data$mood)
    mood_distribution_plot <- ggplot(data = data.frame(mood = names(mood_counts), count = as.numeric(mood_counts)), aes(x = mood, y = count, fill = mood)) +
      geom_bar(stat = "identity") +
      labs(x = "Mood", y = "Number of Songs") +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
      scale_fill_manual(values=coul)
    
    output$mood_distribution_plot <- renderPlot({
      mood_distribution_plot
    })
    
    # Radar Chart
    
    output$radar_chart <- renderPlot({
      vars_of_interest <- c("danceability", "acousticness", "energy", "instrumentalness", "liveness", "valence", "loudness", "speechiness")
      
      averages <- music_data %>%
        group_by(mood) %>%
        summarise(across(vars_of_interest, mean))
      
      
      averages <- as.data.frame(averages)
      rownames(averages) <- averages$mood
      
      
      
      radarchart(averages[,-1]  , axistype=0 , maxmin=F,
                 #custom polygon
                 pcol=colors_border , pfcol=colors_in , plwd=4 , plty=1,
                 #custom the grid
                 cglcol="grey", cglty=1, axislabcol="black", cglwd=0.8, 
                 #custom labels
                 vlcex=0.8 
      )
      
      
    })
  })
}