import requests
import json


def retrieve_and_process_json(url, output_file):
    # Retrieve JSON from the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()

        # Access the ['response']['docs'] list
        docs_list = data.get('response', {}).get('docs', [])

        # Extract 'id' values and write to the output file
        with open(output_file, 'w') as f:
            for doc in docs_list:
                id_value = doc.get('id', '')
                f.write(id_value + '\n')

        print(f"Values from 'id' field written to {output_file}")

    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")


# Example usage
url = "http://localhost:8984/solr/news_articles_v2/select?indent=true&q.op=OR&q=title%3A%20vs%20AND%20title%3A%5C-3%20%5C-4%20%5C-5%20%5C-6%20%5C-7%20%5C-8%20%5C-9%20%5C-10&rows=30&useParams="  # Replace with your actual URL
output_file = "output_ids.txt"  # Replace with your desired output file name

retrieve_and_process_json(url, output_file)
