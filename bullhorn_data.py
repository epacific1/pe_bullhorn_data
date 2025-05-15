import requests

def fetch_all_bullhorn_topic_ids():
    post_id = []
    page = 0

    while True:
        url = f"https://forum.ansible.com/c/news-bullhorn/17/l/latest.json?page={page}"
        print(f"Fetching page {page}: {url}")
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}, status code: {response.status_code}")
            break

        data = response.json()
        topics = data.get("topic_list", {}).get("topics", [])

        if not topics:
            print("No more topics found. Exiting.")
            break

        for topic in topics:
            topic_id = topic.get("id")
            if topic_id is not None:
                post_id.append(topic_id)

        page += 1

    return post_id

# Run the function and print result
post_id = fetch_all_bullhorn_topic_ids()
print(f"Total topics found: {len(post_id)}")
print("Topic IDs:", post_id)