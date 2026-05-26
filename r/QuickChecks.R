library(DBI)
library(RSQLite)

setwd("/Users/diegoanderson/Desktop/Smart Earth and Sky Monitor")

conn <- dbConnect(RSQLite::SQLite(), "monitor.db")

# Check both tables
earthquakes <- dbReadTable(conn, "earthquakes")
weather <- dbReadTable(conn, "weather")

dbDisconnect(conn)

print(nrow(earthquakes))
print(nrow(weather))
print(head(weather))