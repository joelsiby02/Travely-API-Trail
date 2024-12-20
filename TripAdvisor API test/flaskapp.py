from flask import Flask, jsonify, request
import http.client
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Access the secret key
trip_advisor_secret_key = os.getenv("TRIP_ADVISOR_KEY")
if not trip_advisor_secret_key:
    raise ValueError("TRIP_ADVISOR_KEY environment variable is missing.")

app = Flask(__name__)

def fetch_restaurants(location_id):
    """
    Helper function to fetch restaurants for a given location ID.
    """
    conn = http.client.HTTPSConnection("tripadvisor16.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': trip_advisor_secret_key,
        'x-rapidapi-host': "tripadvisor16.p.rapidapi.com"
    }
    conn.request("GET", f"/api/v1/restaurant/searchRestaurants?locationId={location_id}", headers=headers)
    res = conn.getresponse()
    return res.status, res.read()

@app.route('/restaurants/search', methods=['GET'])
def search_restaurants():
    """
    Search for restaurants based on a location ID.
    """
    location_id = request.args.get('locationId', '60763')  # Default location ID
    try:
        status_code, data = fetch_restaurants(location_id)
        if status_code != 200:
            return jsonify({"error": f"API request failed with status code {status_code}"}), status_code

        json_data = json.loads(data.decode("utf-8"))
        return jsonify(json_data), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON response from the API"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/restaurants/save', methods=['GET'])
def save_restaurants():
    """
    Save restaurant data to a JSON file based on a location ID.
    """
    location_id = request.args.get('locationId', '304554')  # Default location ID
    try:
        status_code, data = fetch_restaurants(location_id)
        if status_code != 200:
            return jsonify({"error": f"API request failed with status code {status_code}"}), status_code

        json_data = json.loads(data.decode("utf-8"))
        with open("restaurants.json", "w") as file:
            json.dump(json_data, file, indent=4)

        return jsonify({"message": "Data saved to restaurants.json"}), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON response from the API"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
