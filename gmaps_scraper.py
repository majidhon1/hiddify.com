import argparse
import sys
import requests
import pandas as pd
from geopy.geocoders import Nominatim

def get_coords(province_name):
    """
    Geocodes a province name to latitude and longitude using Nominatim.
    """
    try:
        geolocator = Nominatim(user_agent="gmaps_scraper_app")
        # Adding "Iran" to the query to improve accuracy
        location = geolocator.geocode(f"{province_name}, Iran")
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except Exception as e:
        print(f"An error occurred during geocoding: {e}")
        return None

def main():
    """
    Main function to parse arguments, call the scraping API, and process the results.
    """
    parser = argparse.ArgumentParser(description="Scrape Google Maps for business information using an API.")
    parser.add_argument("business_type", type=str, help="The type of business to search for (e.g., 'کافی نت').")
    parser.add_argument("province_name", type=str, help="The name of the province to search in (e.g., 'استان تهران').")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # Since I cannot prompt for interactive input, I will ask the user to provide the key.
    # For now, I will use a placeholder. The user will be instructed to replace it.
    # In a real scenario, I would use request_user_input here.
    api_key = "YOUR_API_KEY_HERE"
    print("="*50)
    print("IMPORTANT: The script is using a placeholder API key.")
    print("You will need to edit gmaps_scraper.py and replace 'YOUR_API_KEY_HERE' with your actual ScraperAPI key.")
    print("="*50)


    print(f"Geocoding province: {args.province_name}...")
    coords = get_coords(args.province_name)

    if not coords:
        print(f"Could not get coordinates for '{args.province_name}'. Please ensure the province name is correct.")
        sys.exit(1)

    latitude, longitude = coords
    print(f"Coordinates found: Latitude={latitude}, Longitude={longitude}")

    query = args.business_type

    api_url = "http://api.scraperapi.com/structured/google/mapssearch" # Using http as per docs
    params = {
        "api_key": api_key,
        "query": query,
        "latitude": str(latitude),
        "longitude": str(longitude),
    }

    print(f"Making API request for query: '{query}'...")

    try:
        response = requests.get(api_url, params=params, timeout=60) # 60 second timeout
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        print("API request successful.")

        api_data = response.json()
        results = api_data.get('results', [])

        if not results:
            print("The API returned no business results for the query.")
            return

        print(f"Processing {len(results)} results from the API...")

        scraped_data = []
        for item in results:
            scraped_data.append({
                'name': item.get('name'),
                'address': item.get('address_line'),
                'phone': item.get('phone_number', 'N/A'), # Guessing the key might be 'phone_number'
                'latitude': item.get('latitude'),
                'longitude': item.get('longitude')
            })

        df = pd.DataFrame(scraped_data)
        output_filename = "google_maps_data.xlsx"
        df.to_excel(output_filename, index=False, engine='openpyxl')
        print(f"Data successfully saved to {output_filename}")

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
