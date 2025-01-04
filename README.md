# Travel Guide FLASK App

This Flask web application provides users with a comprehensive travel guide for any destination. It uses OpenAI's GPT-4 to generate detailed information on top tourist attractions, food, activities, essential packing items, and more.

## Features

- **History and Origin**: Learn the history of the destination.
- **Top Tourist Attractions**: Get a list of must-visit spots with descriptions and ratings.
- **Ticket Information**: Information on entrance fees, discounts, and ticket types.
- **Food and Dining**: Restaurant recommendations with must-try dishes.
- **Must-Do Activities**: List of unique and off-the-beaten-path activities.
- **Packing Tips**: Essential items to bring based on destination.
- **Nearby Restaurants**: Nearby dining options for each tourist spot.
- **Additional Tips**: Travel tips and hidden gems.

## Installation

1. Clone the repository:

2. Navigate to the project directory:

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file and add your OpenAI API Key:
   ```bash
   OPENAI_API_KEY=your-api-key-here
   ```

5. Run the app:
   ```bash
   python app.py
   ```

6. Open your browser and go to `http://127.0.0.1:5000/`.

## Usage

- Visit `http://127.0.0.1:5000/{destination}` (e.g., `http://127.0.0.1:5000/new-york`) to get a travel guide for any destination.
  
## License

This project is open source and available under the MIT License.

.env file is already created so replace the key with your OPENAI API Key
