import requests
import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("NEW_RELIC_API_KEY")

if not API_KEY:
    print("Error: NEW_RELIC_API_KEY is not set.")
    exit(1)

ACCOUNT_ID = "3785575"
URL = "https://api.newrelic.com/graphql"

def fetch_new_relic_data():
    now = datetime.utcnow()
    since_time = (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    until_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    file_date = (now - timedelta(days=1)).strftime('%d_%m_%Y')
    output_file = f"rfid_{file_date}.xlsx"

    query = {
        "query": f"""
        {{
            actor {{
                account(id: {ACCOUNT_ID}) {{
                    nrql(query: "SELECT * FROM Log SINCE '{since_time}' UNTIL '{until_time}' LIMIT 1000") {{
                        results
                    }}
                }}
            }}
        }}
        """
    }

    headers = {
        "Content-Type": "application/json",
        "API-Key": API_KEY
    }

    response = requests.post(URL, json=query, headers=headers)

    if response.status_code == 200:
        data = response.json()
        results = data.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
        
        if not results:
            print("No data returned from New Relic.")
            return

        df = pd.DataFrame(results)
        df.to_excel(output_file, index=False)
        print(f"Report saved as {output_file}")
    else:
        print(f"Request error: {response.status_code} - {response.text}")

def main():
    """Main function to execute the script."""
    fetch_new_relic_data()

if __name__ == "__main__":
    main()
