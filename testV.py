# import os
# import requests
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# PAPI_HOST = os.environ.get("PAPI_HOST")
# API_KEY = os.environ.get("API_KEY")

# headers = {
#     "exp-api-key": API_KEY,  # ✅ Required API key header
#     "Accept": "application/json;version=2.0",  # ✅ Ensure correct API version
#     "Content-Type": "application/json",
#     "Accept-Language": "en-US"  # ✅ Add a valid language code (e.g., "en-US" or "fr-FR")
# }

# def get_destinations():
#     url = f"{PAPI_HOST}/destinations/"
#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error {response.status_code}: {response.text}")
#         return None

# data = get_destinations()
# print(data)

import os
import requests
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PAPI_HOST = os.getenv("PAPI_HOST")
API_KEY = os.getenv("API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

headers = {
    "exp-api-key": API_KEY,
    "Accept": "application/json;version=2.0",
    "Content-Type": "application/json",
    "Accept-Language": "en-US"
}

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
    """Format attraction details nicely."""
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
        
        formatted_attractions.append(
            f"🎡 **{name}**\n📍 {address}, {city}\n⭐ Rating: {rating}\n🖼 Image: {image_url}\n🔗 More Info: {url}\n"
        )
    
    return formatted_attractions

def get_attractions_from_openai(destination_name):
    """Fetch attractions using OpenAI when API fails."""
    openai.api_key = OPENAI_API_KEY
    prompt = f"List the top 5 tourist attractions in {destination_name}, with a short description for each."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"].split("\n")
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return ["Could not retrieve attractions. Try again later."]

def main():
    destination_name = input("Enter a destination: ")
    destination_id = get_destination_id(destination_name)
    
    if not destination_id:
        print(f"❌ Destination '{destination_name}' not found. Using OpenAI instead...")
        attractions = get_attractions_from_openai(destination_name)
    else:
        print(f"✅ Found destination ID: {destination_id}")
        attractions_data = get_attractions(destination_id)
        attractions = format_attractions(attractions_data) if attractions_data else []
    
    print("\n🎡 **Top Attractions:**")
    for attr in attractions:
        print(attr)

if __name__ == "__main__":
    main()
