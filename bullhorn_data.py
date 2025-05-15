import requests
import json

def fetch_and_save_pretty_json(url, output_file="output.json"):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        data = response.json()  # Parse JSON
        pretty_json = json.dumps(data, indent=4, ensure_ascii=False)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(pretty_json)

        print(f"JSON data saved to '{output_file}'")

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except json.JSONDecodeError:
        print("The response is not valid JSON.")


import json

def extract_topic_ids(json_file_path):
    topic_id = []

    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Navigate to topic_list → topics
        topics = data.get("topic_list", {}).get("topics", [])

        # Extract all "id" values and store in topic_id
        topic_id = [topic.get("id") for topic in topics if "id" in topic]

    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print("File content is not valid JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return topic_id

# Example usage
file_path = "output.json"
topic_id = extract_topic_ids(file_path)
print("Topic IDs:", topic_id)




# Main call
if __name__ == "__main__":

    url = "https://forum.ansible.com/c/news/bullhorn/17.json"
    fetch_and_save_pretty_json(url)
