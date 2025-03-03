from flask import Flask, request, render_template, jsonify
import requests

app = Flask(__name__)

HERE_API_KEY = "3MHNRtsSj6qMMIoorPIiZWM48lhjVGAbkK7rONYOqMc"  # Replace with your actual HERE API Key

def geocode_address(address):
    """Convert address to latitude and longitude using HERE Geocoder API."""
    url = f"https://geocode.search.hereapi.com/v1/geocode?q={address}&apiKey={HERE_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "items" in data and data["items"]:
            location = data["items"][0]["position"]
            return location["lat"], location["lng"]
    return None, None

def get_bike_route(start_lat, start_lon, end_lat, end_lon):
    """Get bike route using HERE Routing API."""
    url = f"https://router.hereapi.com/v8/routes?transportMode=bicycle&origin={start_lat},{start_lon}&destination={end_lat},{end_lon}&return=summary,polyline,instructions&apiKey={HERE_API_KEY}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "routes" in data and data["routes"]:
            return data
    return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_route", methods=["POST"])
def get_route():
    """Handle route requests from frontend."""
    data = request.get_json()

    start_address = data.get("start_address", "")
    end_address = data.get("end_address", "")

    # Convert addresses to coordinates
    start_lat, start_lon = geocode_address(start_address)
    end_lat, end_lon = geocode_address(end_address)

    if not start_lat or not end_lat:
        return jsonify({"success": False, "message": "Invalid start or end address."})

    route_data = get_bike_route(start_lat, start_lon, end_lat, end_lon)

    if route_data and "routes" in route_data:
        route = route_data["routes"][0]
        polyline_data = route["sections"][0]["polyline"]

        return jsonify({
            "success": True,
            "polyline": polyline_data  # Send polyline string back to frontend
        })
    
    return jsonify({"success": False, "message": "No route found."})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

