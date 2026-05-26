import requests # go get the library we installed

url = "https://earthquake.usgs.gov/fdsnws/event/1/query" # waiters address / USGS API endpoing

# these are your order options. youre asking for geojson format, 
# only quakes magnitude 4.5+, and just 10 results
params = {
    "format": "geojson",
    "minmagnitude": 4.5,
    "limit": 10
}

response = requests.get(url, params=params) # sends request and waits for response
# print(response.status_code)
# print(response.text)
data = response.json() # response comes back as raw text, this converts it 
# into a python dict u can work with

# print(data) # just so u can see what came back

# How many earthquakes came back?
print("Total number of earthquakes:")
print(len(data["features"]))
print()

# Look at just the first earthquake
print("First Earthquake:")
print(data["features"][0])
print()

# Now just its properties
print("Properties:")
print(data["features"][0]["properties"])
print()

# Print JUST the magnitude of the first earthquake
first_earthquake_magnitude = data["features"][0]["properties"]["mag"]
print(first_earthquake_magnitude)
print()

# loop through all 10 and print the fields you acc care abt
for earthquake in data["features"]:
    mag = earthquake["properties"]["mag"]
    place = earthquake["properties"]["place"]
    time = earthquake["properties"]["time"]
    lat = earthquake["geometry"]["coordinates"][1]
    lon = earthquake["geometry"]["coordinates"][0]
    depth = earthquake["geometry"]["coordinates"][2] # depth
    
    print(mag, place, time, lat, lon)