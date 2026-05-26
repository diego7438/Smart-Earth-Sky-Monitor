setwd("/Users/diegoanderson/Desktop/Smart Earth and Sky Monitor")

library(shiny)
library(leaflet)
library(DBI)
library(RSQLite)
library(dplyr)

# UI - what it looks like
ui <- fluidPage(
  tags$style(HTML("
                  body { margin: 0; padding: 0; background-color: #0a0e27; }
                  .container-fluid { padding: 0; }
                  #map {
                    position: fixed;
                    top: 0; left: 0;
                    width: 100vw;
                    height: 100vh; 
                  }
                  .title-panel {
                    color: #00d4ff;
                    font-family: 'Courier New', monospace;
                    font-size: 20px;
                    font-weight: bold;
                    text-shadow: 0 0 10px #00d4ff;
                    background: rgba(10, 14, 39, 0.85);
                    padding: 10px 20px;
                    border: 1px solid #00d4ff;
                    border-radius: 4px;
                  }
                  .legend {
                    background: rgba(10, 14, 39, 0.85) !important;
                    color: #00d4ff !important;
                    border: 1px solid #00d4ff;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                  }
                  ")),
  absolutePanel(
    top = 10, left = 50,
    style = "z-index: 1000;",
    div(class = "title-panel", "🌎 Live Earthquake & Weather Monitor")
  ),
  leafletOutput("map", height = "100vh")
)

# SERVER - what it does
server <- function(input, output, session) {
  
  # Read the fresh data every 60 seconds
  data <- reactivePoll(
    intervalMillis = 60000,
    session = session,
    checkFunc = function() {
      conn <- dbConnect(RSQLite::SQLite(), "monitor.db")
      count <- dbGetQuery(conn, "SELECT COUNT(*) FROM earthquakes")
      dbDisconnect(conn)
      return(count)
    },
    valueFunc = function() {
      conn <- dbConnect(RSQLite::SQLite(), "monitor.db")
      earthquakes <- dbReadTable(conn, "earthquakes")
      weather <- dbReadTable(conn, "weather") %>%
        group_by(latitude, longitude) %>%
        slice_max(time, n = 1) %>% # keep only most recent weather per location
        ungroup()
      # Check if anomalies table exists yet
      if ("anomalies" %in% dbListTables(conn)) {
        anomalies <- dbGetQuery(conn, "
        SELECT e.latitude, e.longitude, e.magnitude, e.place, a.anomaly
        FROM earthquakes e
        JOIN anomalies a ON e.id = a.id
        WHERE a.anomaly = 'anomaly'
        ") 
      } else {
        anomalies <- data.frame() # empty dataframe if no anomalies yet
      }
      dbDisconnect(conn)
      # print(nrow(weather)) for debugging only
      # print(head(weather)) for debugging only
      list(earthquakes = earthquakes, weather = weather, anomalies = anomalies)
    }
  )
  
  
  # Render the map
  output$map <- renderLeaflet({
    earthquakes <- data()$earthquakes
    weather <- data()$weather
    anomalies <- data()$anomalies
    
    # Creates a function that converts magnitude to a color
    pal <- colorNumeric(
      palette = c("yellow", "orange", "red"),
      domain = earthquakes$magnitude
    )
  
    leaflet_map <- leaflet(options = leafletOptions(worldCopyJump = TRUE)) %>%
      addProviderTiles(providers$CartoDB.DarkMatter) %>%
      setView(lng = 0, lat = 20, zoom = 2) %>% 
      # Earthquake layer
      addCircleMarkers(
        data = earthquakes,
        lng = ~longitude,
        lat = ~latitude,
        radius = ~magnitude * 3,
        color = ~pal(magnitude),
        fillOpacity = 0.8,
        weight = 2,
        popup = ~paste("Magnitude:", magnitude, "<br>Location:", place)
      ) %>%
      # Weather layer
      addCircleMarkers(
        data = weather,
        lng = ~longitude,
        lat = ~latitude,
        radius = 5,
        color = "steelblue",
        opacity = 0.7,
        popup = ~paste(
          "Temp:", temperature, "°C<br>",
          "Conditions:", weather_main, "<br>",
          "Humidity:", humidity, "%<br>",
          "Pressure:", pressure, "hPa")
      ) %>%
      addLegend(
        position = "bottomright",
        pal = pal,
        values = earthquakes$magnitude,
        title = "Magnitude"
      )
    
    # Only add anomaly layer if data exists
    if (nrow(anomalies) > 0) {
      leaflet_map <- leaflet_map %>%
        addCircleMarkers(
          data = anomalies,
          lng = ~longitude,
          lat = ~latitude,
          radius = ~magnitude * 4,
          color = "#00d4ff",
          weight = 3,
          fillOpacity = 0.5,
          popup = ~paste("⚠️ ANOMALY<br>Magnitude:", magnitude, "<br>Location:", place)
        )
    }
    
    # Always return the map
    leaflet_map
  })
}

shinyApp(ui, server)