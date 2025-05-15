import requests
import csv
import re
import json

# Step 1: Fetch all topic info
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

# Step 2: Fetch raw Markdown
def fetch_raw_markdown(post_id):
    url = f"https://forum.ansible.com/raw/{post_id}"
    print(f"Fetching raw content for post {post_id}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch post {post_id}")
        return ""

# Step 3: Extract user and matrix link from matched lines
def extract_user_and_link(post_id, markdown_text, keywords=("shared", "said", "contributed")):
    pattern = r"\[(.*?)\]\((https://matrix\.to/#/@[^)]+)\).*(" + "|".join(keywords) + ")"
    matches = []

    for line in markdown_text.splitlines():
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            user, link, _ = match.groups()
            matches.append({
                "post_id": post_id,
                "user": user,
                "matrix_link": link
            })

    return matches

# Run full pipeline
post_id, views_per_edition = fetch_all_bullhorn_topics()

# Save views_per_edition to CSV
with open("views_per_edition.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "title", "views", "like_count"])
    writer.writeheader()
    for entry in views_per_edition:
        writer.writerow(entry)

# Collect and save filtered user + matrix links
filtered_data = []

for pid in post_id:
    raw_md = fetch_raw_markdown(pid)
    user_link_matches = extract_user_and_link(pid, raw_md)
    filtered_data.extend(user_link_matches)

# Save to CSV
# Add title to each row in filtered_data using post_id -> title mapping
id_to_title = {entry["id"]: entry["title"] for entry in views_per_edition}

# Save enriched data to CSV
with open("bullhorn_filtered_lines.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["post_id", "title", "user", "matrix_link"])
    writer.writeheader()
    for row in filtered_data:
        post_id = int(row["post_id"])
        writer.writerow({
            "post_id": post_id,
            "title": id_to_title.get(post_id, ""),
            "user": row["user"],
            "matrix_link": row["matrix_link"]
        })

print(f"\n✅ Extracted {len(filtered_data)} matching lines to bullhorn_filtered_lines.csv")



from collections import defaultdict

# Step 4: Count number of unique users per post_id
user_map = defaultdict(set)

# Group by post_id and collect unique users
for row in filtered_data:
    user_map[row["post_id"]].add(row["user"])

# Merge with title info from views_per_edition
id_to_title = {str(entry["id"]): entry["title"] for entry in views_per_edition}

# Write the summary CSV
with open("user_count_per_post.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "title", "number_of_users"])
    writer.writeheader()
    for pid, users in user_map.items():
        writer.writerow({
            "id": pid,
            "title": id_to_title.get(str(pid), ""),
            "number_of_users": len(users)
        })

print(f"✅ Created user_count_per_post.csv with {len(user_map)} rows")