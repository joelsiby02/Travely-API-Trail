import re

def extract_place_names(response):
    # Extract `places_for_images` list
    pattern = r"places_for_images\s*=\s*\[(.*?)\]"
    match = re.search(pattern, response, re.DOTALL)
    if match:
        # Split the list items and clean up whitespace and quotes
        return [place.strip().strip('"').strip("'") for place in match.group(1).split(",")]
    return []

response = """Travel Guide for New York (Couple Trip)
# Comprehensive Travel Guide for New York

---

### Python Lists for Reference

```python
places_for_images = ["Central Park", "Empire State Building", "The High Line", "Brooklyn Bridge", "Times Square"]
restaurants_to_search = ["Tavern on the Green", "The Skylark", "Juliana’s Pizza", "The River Café"]
```"""

# Extract the places
places = extract_place_names(response)
print(places)
