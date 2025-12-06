import requests
import pymongo
import datetime

# MongoDB URI (Replace with your credentials)
mongo_uri = "your_mongodb_connection_string"
client = pymongo.MongoClient(mongo_uri)

# Test MongoDB connection
try:
    client.admin.command('ping')
    print("Connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Select your database and collection
db = client["StockDataDB"]
collection = db["stocks"]

# Function to fetch stock data using Finnhub API
def fetch_stock_data(stock_symbol):
    API_TOKEN = "your_finnhub_api_token"  # Replace with your Finnhub API token
    url = f'https://finnhub.io/api/v1/quote?symbol={stock_symbol}&token={API_TOKEN}'
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        print("API Response:", data)  # Debugging print

        if "c" in data:
            stock_data = {
                "company_name": stock_symbol,
                "stock_symbol": stock_symbol,
                "date": datetime.datetime.now(),
                "closing_price": float(data.get("c", 0)),
                "volume": data.get("v", 0)
            }
            return stock_data
        else:
            print("Error: API response does not contain expected stock data keys.")
            return None
    else:
        print("Error fetching data from API. Status code:", response.status_code)
        return None

# Function to insert data into MongoDB
def insert_data_into_mongo(stock_data):
    if stock_data:
        try:
            print(f"Inserting data for {stock_data['company_name']} into MongoDB...")
            result = collection.insert_one(stock_data)
            print(f"Data inserted successfully. ID: {result.inserted_id}")
        except Exception as e:
            print(f"Error inserting data into MongoDB: {e}")

# Main function to execute the program
def main():
    stock_symbol = input("Enter stock symbol (e.g., AAPL for Apple, TSLA for Tesla): ").upper()
    stock_data = fetch_stock_data(stock_symbol)

    if stock_data:
        insert_data_into_mongo(stock_data)
    else:
        print("No data to insert. Check the API response.")

if __name__ == "__main__":
    main()