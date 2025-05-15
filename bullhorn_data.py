import requests
import csv
import json

# Step 1: Fetch all topic info including id, title, views, like_count
def fetch_all_bullhorn_topics():
    post_id = []
    views_per_edition = []
    page = 0

    while True:
        url = f"https://forum.ansible.com/c/news-bullhorn/17/l/latest.json?page={page}"
        print(f"Fetching page {page}")
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}")
            break

        data = response.json()
        topics = data.get("topic_list", {}).get("topics", [])

        if not topics:
            break

        for topic in topics:
            topic_id = topic.get("id")
            title = topic.get("title", "").strip()
            views = topic.get("views", 0)
            like_count = topic.get("like_count", 0)

            if topic_id:
                post_id.append(topic_id)
                views_per_edition.append({
                    "id": topic_id,
                    "title": title,
                    "views": views,
                    "like_count": like_count
                })

        page += 1

    return post_id, views_per_edition

# Step 2: For each post_id, get the raw Markdown content
def fetch_raw_markdown(post_id):
    url = f"https://forum.ansible.com/raw/{post_id}"
    print(f"Fetching raw content for post {post_id}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch post {post_id}")
        return ""

# Step 3: Extract lines with keywords
def extract_matching_lines(markdown_text, keywords=("shared", "said", "contributed")):
    lines = markdown_text.splitlines()
    matched_lines = [line for line in lines if any(keyword in line.lower() for keyword in keywords)]
    return matched_lines

# Run the whole pipeline
post_id, views_per_edition = fetch_all_bullhorn_topics()
print(f"Found {len(post_id)} post IDs")

# Save views_per_edition to CSV
with open("views_per_edition.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "title", "views", "like_count"])
    writer.writeheader()
    for entry in views_per_edition:
        writer.writerow(entry)

# Process raw markdown and extract keyword matches
all_matches = []

for pid in post_id:
    raw_md = fetch_raw_markdown(pid)
    matches = extract_matching_lines(raw_md)
    if matches:
        all_matches.append({
            "post_id": pid,
            "matched_lines": matches
        })

# Print and optionally save filtered lines
for match in all_matches:
    print(f"\n📌 Post ID: {match['post_id']}")
    for line in match['matched_lines']:
        print(f"→ {line}")

with open("bullhorn_filtered_lines.json", "w", encoding="utf-8") as f:
    json.dump(all_matches, f, indent=2, ensure_ascii=False)
