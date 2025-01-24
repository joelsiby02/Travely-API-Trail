import os
import openai
import re
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from serpapi import GoogleSearch
import geocoder
import requests

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")  # Add your Google Maps API key here

app = Flask(__name__)

def extract_place_names(response):
    """
    Extract place names from GPT response.
    """
    try:
        pattern = r"places_for_images\s*=\s*\[(.*?)\]"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return [place.strip().strip('"') for place in match.group(1).split(",")]
        return []
    except Exception as e:
        print(f"Error extracting place names: {e}")
        return []

def get_image(places_list):
    """
    Retrieve image URLs for a list of places using SerpAPI.
    """
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

def format_markdown(response, image_urls, route_info=None):
    """
    Format the GPT response and image URLs into a structured Markdown file.
    """
    try:
        markdown_output = ""
        
        # Split the response into sections
        sections = response.split("\n\n")
        for section in sections:
            if section.startswith("**"):
                # Format headings
                markdown_output += f"# {section.strip('*')}\n\n"
            elif section.startswith("-"):
                # Format list items
                markdown_output += f"{section}\n"
            else:
                # Add plain text
                markdown_output += f"{section}\n\n"

        # Add images to corresponding places
        markdown_output += "\n## Image Links for Tourist Spots\n"
        places = extract_place_names(response)
        
        for place, url in zip(places, image_urls):
            markdown_output += f"### {place}\n"
            if url != "No image found" and url != "Error fetching image":
                markdown_output += f"![{place}]({url})\n\n"
            else:
                markdown_output += f"No image available\n\n"
        
        if route_info:
            markdown_output += f"\n## Travel Route Information\n{route_info}"

        return markdown_output
    except Exception as e:
        print(f"Error formatting markdown: {e}")
        return "Error formatting the travel guide."

def get_route(origin, destination):
    """
    Get the route information and travel time using Google Maps Directions API.
    """
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin, 
        "destination": destination, 
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(directions_url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        route = data['routes'][0]['legs'][0]
        travel_time = route['duration']['text']
        travel_distance = route['distance']['text']
        steps = route['steps']
        route_info = f"Travel Time: {travel_time}\nDistance: {travel_distance}\n\nStep-by-step Directions:\n"
        for step in steps:
            route_info += f"{step['html_instructions']}\n"
        maps_link = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
        route_info += f"\nGoogle Maps Link: {maps_link}"
        return route_info
    else:
        return "Error: Unable to fetch directions."

def get_travel_info(destination, travel_type, current_location):
    """
    Generate a detailed travel guide using GPT and add image links for tourist spots.
    """
    base_prompt = f"""
    Please create a detailed and structured travel guide for {destination}, ensuring at least 5 tourist spots are included. For each tourist spot, provide the following details separately and comprehensively:

        1. **Overview of {destination}**:
        - Provide a brief introduction to the destination.
        - Highlight its historical significance, cultural importance, or unique features that make it a popular tourist spot.

        2. **Top 5 Tourist Spots**:
        For each spot, create a **separate section** with the following subheadings:

        2.1 **Name and Description**:
            - Name of the attraction.
            - A detailed description explaining why it is worth visiting.
            - Any unique aspects (e.g., historical value, natural beauty, cultural significance).

        2.2 **Tips for Visiting**:
            - Best time to visit (season, time of day).
            - Accessibility tips (e.g., wheelchair access, family-friendly).
            - Recommendations on what to bring or prepare (e.g., sunscreen, cameras).

        2.3 **Ticket Information**:
            - Entry fees, categorized into standard, VIP, and discounted tickets (students, seniors, children, etc.).
            - Reservation requirements (e.g., advance bookings for tours or events).

        2.4 **Nearby Restaurants**:
            - Recommend 3-4 restaurants near the tourist spot.
            - For each restaurant, include:
                - Name and cuisine type (e.g., vegetarian, vegan, non-vegetarian).
                - Ratings (out of 5 stars).
                - Signature dishes to try.
                - Operational status (open/closed) and reservation requirements.

        3. **Local Food and Dining**:
        - Highlight iconic dishes and local delicacies specific to the destination.
        - Include suggestions for popular food markets or street food vendors.

        4. **Must-Do Activities**:
        - Provide a list of exciting activities to experience in {destination}.
        - Include unique or off-the-beaten-path suggestions, such as cultural festivals or adventure sports.

        5. **Packing and Essentials**:
        - Recommend essential items to pack based on {destination}’s climate and culture.
        - Include any cultural etiquette tips (e.g., clothing norms, behavior in religious sites).

        6. **Additional Travel Tips**:
        - Best times of the year to visit and weather considerations.
        - Transport options for navigating the area.
        - Hidden gems or underrated attractions worth exploring.

         At the very end of the response, please provide:
        1. A Python list named places_for_images containing the names of the 5 recommended tourist spots, like this:
           places_for_images = ["Place 1", "Place 2", "Place 3", "Place 4", "Place 5"]
    """

    type_prompts = {
        "family": "Focus on family-friendly attractions, activities for kids, and dining options with child-friendly menus.",
        "business": "Focus on business hotels, meeting-friendly restaurants, and quick-break attractions.",
        "couple": "Focus on romantic spots, scenic locations, and intimate dining experiences.",
        "friends": "Focus on group activities, adventurous attractions, and budget-friendly options.",
        "bachelor": "Focus on nightlife, bars, and exciting activities suitable for solo travelers or small groups."
    }

    if travel_type in type_prompts:
        base_prompt += "\n" + type_prompts[travel_type]

    try:
        # Generate response from OpenAI
        chat_completion = openai.ChatCompletion.create(
            messages=[{"role": "user", "content": base_prompt}],
            model="gpt-3.5-turbo"
        )
        response = chat_completion['choices'][0]['message']['content']

        # Extract places for images
        places_list = extract_place_names(response)
        image_urls = get_image(places_list)

        # Get route information
        route_info = get_route(current_location, destination)

        # Format the response into Markdown
        markdown_response = format_markdown(response, image_urls, route_info)
        return markdown_response
    except Exception as e:
        return f"Error generating travel guide: {str(e)}"

@app.route('/')
def home():
    return """
    <h1>Welcome to the Travel Guide API</h1>
    <p>To get a travel guide, add the destination and travel type as query parameters in the URL, like this:</p>
    <pre>/travel_guide?destination=New York&travel_type=couple</pre>
    """

@app.route('/travel_guide')
def travel_guide():
    """
    Handle travel guide API requests.
    """
    destination = request.args.get('destination')
    travel_type = request.args.get('travel_type', 'general')

    if not destination:
        return "Please provide a destination in the query parameter (e.g., ?destination=New York)."

    # Get current location (IP-based)
    g = geocoder.ip('me')
    current_location = f"{g.latlng[0]},{g.latlng[1]}"  # latitude,longitude format

    # Fetch travel information
    travel_info = get_travel_info(destination, travel_type, current_location)

    # Return the response as Markdown
    return f"<h1>Travel Guide for {destination} ({travel_type.capitalize()} Trip)</h1><pre>{travel_info}</pre>"

if __name__ == "__main__":
    app.run(debug=True)