import os
import openai
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")

app = Flask(__name__)

def get_travel_info(destination, travel_type):
    # Construct a detailed query asking for different aspects of the destination
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
        1. A Python list named `places_for_images` containing the names of the 5 recommended tourist spots, like this:
           places_for_images = ["Place 1", "Place 2", "Place 3", "Place 4", "Place 5"]
        2. A Python list named `restaurents_to_search` containing the names of 4 recommended restaurants, like this:
           restaurents_to_search = ["Restaurant 1", "Restaurant 2", "Restaurant 3", "Restaurant 4"]
        

        Ensure the guide is organized with clear headings and subheadings for each tourist spot and restaurant, making it easy for travelers to follow.
    """
    
    # Travel-type-specific details
    type_prompts = {
        "family": "Focus on family-friendly attractions, activities for kids , and dining options with child-friendly menus.",
        "business": "Focus on business hotels, meeting-friendly restaurants, and quick-break attractions.",
        "couple": "Focus on romantic spots, scenic locations, and intimate dining experiences.",
        "friends": "Focus on group activities, adventurous attractions, and budget-friendly options.",
        "bachelor": "Focus on nightlife, bars, and exciting activities suitable for solo travelers or small groups."
    }

    # Append specific details based on travel type
    travel_type_prompt = type_prompts.get(travel_type.lower(), "Focus on general attractions and experiences.")
    full_prompt = base_prompt + "\n" + travel_type_prompt

    # Generate the response using OpenAI API
    try:
        chat_completion = openai.ChatCompletion.create(
            messages=[{"role": "user", "content": full_prompt}],
            model="chatgpt-4o-latest"
        )

        response = chat_completion['choices'][0]['message']['content']
        print(type(response))
        return response
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return """
    <h1>Welcome to the Travel Guide API</h1>
    <p>To get a travel guide, add the destination and travel type as query parameters in the URL, like this:</p>
    <pre>/travel_guide?destination=New York&travel_type=couple</pre>
    """

@app.route('/travel_guide')
def travel_guide():
    # Get the 'destination' and 'travel_type' parameters from the URL
    destination = request.args.get('destination')
    travel_type = request.args.get('travel_type', 'general')  # Default to 'general' if not provided

    if not destination:
        return "Please provide a destination in the query parameter (e.g., ?destination=New York)."

    # Fetch the travel information for the destination and travel type
    travel_info = get_travel_info(destination, travel_type)

    # Return the travel guide info as a response on the web page
    return f"<h1>Travel Guide for {destination} ({travel_type.capitalize()} Trip)</h1><pre>{travel_info}</pre>"

if __name__ == '__main__':
    app.run(debug=True)
