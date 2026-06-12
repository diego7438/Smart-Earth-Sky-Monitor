library(DBI)
library(RSQLite)

conn <- dbConnect(
    RSQLite::SQLite(),
    "/Users/diegoanderson/Desktop/Smart Earth and Sky Monitor/monitor.db"
)

# Show all tables
cat("=== TABLES IN DATABASE ===\n")
print(dbListTables(conn))

# Earthquakes
cat("\n=== EARTHQUAKES ===\n")
earthquakes <- dbReadTable(conn, "earthquakes")
cat("Rows:", nrow(earthquakes), "\n")
print(head(earthquakes))

# Weather
cat("\n=== WEATHER ===\n")
weather <- dbReadTable(conn, "weather")
cat("Rows:", nrow(weather), "\n")
print(head(weather))

# Anomalies
cat("\n=== ANOMALIES ===\n")
if ("anomalies" %in% dbListTables(conn)) {
    anomalies <- dbReadTable(conn, "anomalies")
    cat("Rows:", nrow(anomalies), "\n")
    print(head(anomalies))
} else {
    cat("No anomalies table yet\n")
}

# Model Performance
cat("\n=== MODEL PERFORMANCE ===\n")
if ("model_performance" %in% dbListTables(conn)) {
    perf <- dbReadTable(conn, "model_performance")
    cat("Rows:", nrow(perf), "\n")
    print(perf)
} else {
    cat("No model performance table yet\n")
}

# Magnitude Predictions
cat("\n=== MAGNITUDE PREDICTIONS ===\n")
if ("magnitude_predictions" %in% dbListTables(conn)) {
    preds <- dbReadTable(conn, "magnitude_predictions")
    cat("Rows:", nrow(preds), "\n")
    print(head(preds))
} else {
    cat("No predictions table yet sadly\n")
}

dbDisconnect(conn)
cat("\n=== DATABASE CHECK COMPLETE ===\n")
