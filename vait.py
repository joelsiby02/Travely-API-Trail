from flask import Flask, request, jsonify, render_template
import os
import openai
import re
from dotenv import load_dotenv
from serpapi import GoogleSearch
import requests

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
PAPI_HOST = os.getenv("PAPI_HOST")
API_KEY = os.getenv("API_KEY")

headers = {
    "exp-api-key": API_KEY,
    "Accept": "application/json;version=2.0",
    "Content-Type": "application/json",
    "Accept-Language": "en-US"
}

app = Flask(__name__)

def get_destination_id(destination_name):
    """Fetch destinations and use a dictionary for faster lookup."""
    url = f"{PAPI_HOST}/destinations/"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        destinations = data.get("destinations", [])
        destination_dict = {dest["name"].lower(): dest["destinationId"] for dest in destinations}
        return destination_dict.get(destination_name.lower())
    
    print(f"❌ API Error {response.status_code}: {response.text}")
    return None

def get_attractions(destination_id):
    """Fetch attractions for a given destination ID."""
    url = f"{PAPI_HOST}/attractions/search"
    body = {
        "destinationId": destination_id,
        "pagination": {"start": 1, "count": 10},
        "sorting": {"sort": "DEFAULT"}
    }
    
    response = requests.post(url, json=body, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    
    print(f"❌ API Error {response.status_code}: {response.text}")
    return None

def format_attractions(attractions_data):
    """Format attraction details into structured data."""
    attractions = attractions_data.get("attractions", [])
    
    if not attractions:
        print("❌ No attractions found.")
        return []
    
    formatted_attractions = []
    for attr in attractions:
        name = attr.get("name", "Unknown Attraction")
        url = attr.get("attractionUrl", "N/A")
        address = attr.get("address", {}).get("street", "Unknown Address")
        city = attr.get("address", {}).get("city", "")
        rating = attr.get("reviews", {}).get("combinedAverageRating", "N/A")
        image_url = attr.get("images", [{}])[0].get("url", "No Image")
        
        formatted_attractions.append({
            "name": name,
            "url": url,
            "address": f"{address}, {city}",
            "rating": rating,
            "image_url": image_url
        })
    
    return formatted_attractions

def extract_place_names(response):
    try:
        pattern = r"places_for_images\s*=\s*\[(.*?)\]"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return [place.strip().strip('"') for place in match.group(1).split(",")]
        return []
    except Exception as e:
        print(f"Error extracting place names: {e}")
        return []

def get_lat_lng(place):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={place}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url).json()
    
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        return {"name": place, "lat": location["lat"], "lng": location["lng"]}
    else:
        return None

def get_image(places_list):
    image_urls = []
    for place in places_list:
        params = {"q": place, "engine": "google_images", "ijn": "0", "api_key": SERPAPI_KEY}
        try:
            search = GoogleSearch(params)
            results_dict = search.get_dict()
            images_results = results_dict.get("images_results", [])
            if images_results:
                image_urls.append(images_results[0].get("original"))
            else:
                image_urls.append("No image found")
        except Exception as e:
            print(f"Error fetching image for {place}: {e}")
            image_urls.append("Error fetching image")
    return image_urls

def format_markdown_api(response, attractions, locations):
    """Format markdown for API-found destinations."""
    markdown_output = response
    markdown_output += "\n## Image Links for Tourist Spots\n"
    
    for attr in attractions:
        markdown_output += f"### {attr['name']}\n"
        if attr['image_url'] != "No Image":
            markdown_output += f"![{attr['name']}]({attr['image_url']})\n\n"
        else:
            markdown_output += "No image available\n\n"
    
    if locations:
        markdown_output += "\n## Travel Route Information\n"
        for loc in locations:
            if loc:
                markdown_output += f"- {loc['name']}: Latitude {loc['lat']}, Longitude {loc['lng']}\n"
    
    return markdown_output

def format_markdown_generated(response, image_urls, locations):
    """Format markdown for API-not-found destinations."""
    markdown_output = response
    markdown_output += "\n## Image Links for Tourist Spots\n"
    places = extract_place_names(response)
    
    for place, url in zip(places, image_urls):
        markdown_output += f"### {place}\n"
        if url not in ["No image found", "Error fetching image"]:
            markdown_output += f"![{place}]({url})\n\n"
        else:
            markdown_output += f"No image available\n\n"
    
    if locations:
        markdown_output += "\n## Travel Route Information\n"
        for loc in locations:
            if loc:
                markdown_output += f"- {loc['name']}: Latitude {loc['lat']}, Longitude {loc['lng']}\n"
    
    return markdown_output

def get_travel_info(destination, travel_type):
    destination_id = get_destination_id(destination)
    
    if destination_id:
        # API Found - Use API data driven prompt
        attractions_data = get_attractions(destination_id)
        if not attractions_data:
            return f"Error: Could not fetch attractions for {destination}"
        
        attractions = format_attractions(attractions_data)[:5]
        attractions_text = "\n".join([f"- {attr['name']}" for attr in attractions])

        base_prompt = f"""
        Create a detailed travel guide for {destination} focusing on these attractions:
        {attractions_text}

        1. **Overview of {destination}**:
        - Brief introduction highlighting historical/cultural significance

        2. **Top 5 Tourist Spots**:
        For each attraction:
        2.1 **Name and Description**: Detailed description and unique aspects
        2.2 **Tips for Visiting**: Best times, accessibility, preparation
        2.3 **Ticket Information**: Pricing tiers and reservations
        2.4 **Nearby Restaurants**: 3-4 recommendations with cuisine, ratings, and dishes

        3. **Local Food and Dining**: Iconic dishes and food markets
        4. **Must-Do Activities**: Unique experiences and hidden gems
        5. **Packing and Essentials**: Climate/culture specific items
        """
    else:
        # API Not Found - Use generic prompt
        base_prompt = f"""
        Create a detailed travel guide for {destination} including:
        1. **Overview**: Introduction and significance
        2. **Top 5 Tourist Spots**: With descriptions, tips, tickets, and nearby restaurants
        3. **Local Food**: Iconic dishes and dining spots
        4. **Activities**: Unique experiences
        5. **Packing**: Climate/culture essentials
        6. **Additional Tips**: Best times, transport, hidden gems

        End with:
        places_for_images = ["Place1", "Place2", "Place3", "Place4", "Place5"]
        places_for_restaurants = ["Restaurant1", "Restaurant2"]
        """

    type_prompts = {
        "family": "Focus on family-friendly amenities and activities.",
        "business": "Highlight business-friendly facilities.",
        "couple": "Emphasize romantic experiences.",
        "friends": "Suggest group activities.",
        "bachelor": "Focus on nightlife and adventure."
    }
    
    if travel_type in type_prompts:
        base_prompt += "\n" + type_prompts[travel_type]

    try:
        chat_completion = openai.ChatCompletion.create(
            messages=[{"role": "user", "content": base_prompt}],
            model="gpt-3.5-turbo"
        )
        response = chat_completion['choices'][0]['message']['content']

        if destination_id:
            # API Found: Use API data for images and locations
            locations = [get_lat_lng(attr['address']) for attr in attractions]
            return format_markdown_api(response, attractions, locations)
        else:
            # API Not Found: Extract places and fetch external data
            places_list = extract_place_names(response)
            locations = [get_lat_lng(place) for place in places_list]
            image_urls = get_image(places_list)
            return format_markdown_generated(response, image_urls, locations)

    except Exception as e:
        return f"Error generating travel guide: {str(e)}"

@app.route('/')
def home():
    return """
    <h1>Welcome to the Travel Guide API</h1>
    <p>To get a travel guide, add the destination and travel type as query parameters in the URL, like this:</p>
    <pre>/travel_guide?destination=New York&travel_type=couple</pre>
    <pre>/map_view?destination=Alappuzha&travel_type=friends<pre>
    """

@app.route("/map_view")
def map_view():
    destination = request.args.get('destination', 'New York')
    travel_type = request.args.get('travel_type', 'general')
    travel_info = get_travel_info(destination, travel_type)
    places_list = extract_place_names(travel_info) if not get_destination_id(destination) else []
    locations = [get_lat_lng(place) for place in places_list if get_lat_lng(place)]
    return render_template("map.html", locations=locations, api_key=GOOGLE_MAPS_API_KEY)

@app.route('/travel_guide')
def travel_guide():
    destination = request.args.get('destination')
    travel_type = request.args.get('travel_type', 'general')

    if not destination:
        return "Please provide a destination in the query parameter (e.g., ?destination=New York)."

    travel_info = get_travel_info(destination, travel_type)
    return f"<h1>Travel Guide for {destination} ({travel_type.capitalize()} Trip)</h1><pre>{travel_info}</pre>"

if __name__ == "__main__":
    app.run(debug=True)