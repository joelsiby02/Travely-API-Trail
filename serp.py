from serpapi import GoogleSearch
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch the SerpAPI key from environment variables
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")  # Ensure your .env file contains SERPAPI_KEY

# Input list of places
places_for_images = ["Empire State Building", "Central Park", "Brooklyn Bridge", "The High Line", "Top of the Rock"]

# List to store image URLs
image_urls = []

for place in places_for_images:
    # Define search parameters
    params = {
        "q": place,
        "engine": "google_images",
        "ijn": "0",  # First page of results
        "api_key": SERPAPI_KEY
    }
    
    try:
        # Perform the search
        search = GoogleSearch(params)
        results_dict = search.get_dict()
        
        # Extract image results
        images_results = results_dict.get("images_results", [])
        
        # Get the first image URL if available
        if images_results:
            first_image_url = images_results[0].get("original")  # Use "original" key for full-size image URL
            if first_image_url:
                image_urls.append(first_image_url)
                print(f"Image URL for {place}: {first_image_url}")
            else:
                print(f"No valid image URL found for {place}")
        else:
            print(f"No image results found for {place}")
    
    except Exception as e:
        print(f"An error occurred while fetching results for {place}: {e}")

# Optional: Print the list of all image URLs at the end
print("\nAll fetched image URLs:")
for i, url in enumerate(image_urls, 1):
    print(f"{i}. {url}")



# def get_image(places_list, SERPAPI_KEY):
#     # List to store image URLs
#     image_urls = []
    
#     for place in places_for_images:
#         # Define search parameters
#         params = {
#             "q": place,
#             "engine": "google_images",
#             "ijn": "0", 
#             "api_key": SERPAPI_KEY
#         }
        
#         try:
#             # Perform the search
#             search = GoogleSearch(params)
#             results_dict = search.get_dict()
            
#             # Extract image results
#             images_results = results_dict.get("images_results", [])
            
#             # Get the first image URL
#             if images_results:
#                 first_image_url = images_results[0].get("original") 
#                 if first_image_url:
#                     image_urls.append(first_image_url)
#                     print(f"Image URL for {place}: {first_image_url}")
#                 else:
#                     print(f"No valid image URL found for {place}")
#             else:
#                 print(f"No image results found for {place}")
        
#         except Exception as e:
#             print(f"An error occurred while fetching results for {place}: {e}")
    
#     # Optional: Print the list of all image URLs at the end
#     print("\nAll fetched image URLs:")
#     for i, url in enumerate(image_urls, 1):
#         print(f"{i}. {url}")



