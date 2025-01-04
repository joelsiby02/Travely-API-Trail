import os
import openai
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")

app = Flask(__name__)

def get_travel_info(destination):
    # Construct a detailed query asking for different aspects of the destination
    prompt = f"""
    Please provide a comprehensive travel guide for {destination}, covering the following aspects:

    1. **History and Origin**:
    - Briefly explain the history and origins of the destination. What makes it a renowned tourist spot? How did it gain popularity?

    2. **Top Tourist Attractions**:
    - List at least five must-visit tourist attractions. For each:
        - A short description
        - Ratings (if available)
        - Key details like operational hours (year-round or seasonal), any seasonal tips, and whether reservations are required.

    3. **Ticket Information**:
    - Provide entrance fee details for each attraction, including:
        - Ticket types (standard, VIP, etc.)
        - Any available discounts (student, senior, etc.)
        - Age-based pricing, if applicable

    4. **Food and Dining**:
    - Suggest the best dining options, including:
        - Local cuisine and must-try dishes
        - Vegetarian, non-vegetarian, and vegan restaurant recommendations with ratings
        - Status of each restaurant (open/closed, reservations required, etc.)
        - Highlight the best dish to try at a specific restaurant.

    5. **Must-Do Activities**:
    - List essential activities to experience at the destination, including:
        - Popular activities
        - Off-the-beaten-path suggestions
        - Unique experiences or local customs that tourists typically miss

    6. **Packing and Essential Items**:
    - Suggest essential items to pack based on the destination’s weather, culture, and activities. For example:
        - Gear for outdoor activities (e.g., hiking boots, trekking poles)
        - Clothing recommendations based on the climate (e.g., sunblock, rain gear)
        - Any cultural etiquette to consider (e.g., clothing norms, tipping practices)

    7. **Nearby Restaurants**:
    - Recommend restaurants near each of the key tourist spots. Include:
        - Ratings and whether the restaurants offer vegetarian, non-vegetarian, or vegan options
        - Operational status (open/closed) and any specific requirements (e.g., reservations needed)

    8. **Additional Tips**:
    - Share helpful tips for navigating the area:
        - Best times of the year to visit, weather considerations
        - Hidden gems or lesser-known attractions that are worth visiting
        - Practical advice like how to get around (e.g., local transport options or apps)

    9. **Local Delicacies and Iconic Dishes**:
    - Highlight the top local dishes and delicacies, explaining what makes them special to the region.
    - Include where to find the best versions of these dishes, and any popular food markets or street food experiences.

    Please organize the information in a clear and concise manner, making it easy for travelers to navigate. Include all necessary details to help plan their visit efficiently.
    """

    # Requesting the information from GPT-4
    chat_completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-4"
    )

    # Extracting the response
    response = chat_completion['choices'][0]['message']['content']
    return response

@app.route('/')
def home():
    return """
    <h1>Welcome to the Travel Guide API</h1>
    <p>To get a travel guide, add the destination as a query parameter in the URL, like this:</p>
    <pre>/travel_guide?destination=New York</pre>
    """

@app.route('/travel_guide')
def travel_guide():
    # Get the 'destination' parameter from the URL
    destination = request.args.get('destination')

    if not destination:
        return "Please provide a destination in the query parameter (e.g., ?destination=New York)."

    # Fetch the travel information for the destination
    travel_info = get_travel_info(destination)

    # Return the travel guide info as a response on the web page
    return f"<h1>Travel Guide for {destination}</h1><pre>{travel_info}</pre>"

if __name__ == '__main__':
    app.run(debug=True)
