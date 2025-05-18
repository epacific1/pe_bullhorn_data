#!/usr/bin/env python3
"""
Ansible Bullhorn Forum Data Extractor

This script extracts and analyzes data from the Ansible Bullhorn forum, focusing on:
1. Fetching topic information from the forum
2. Extracting raw Markdown content from posts
3. Identifying user contributions and matrix links
4. Generating statistics on user participation and post popularity

The script produces three CSV files:
- views_per_edition.csv: Contains view and like counts for each Bullhorn edition
- bullhorn_filtered_lines.csv: Contains user contributions with matrix links
- user_count_per_post.csv: Summarizes the number of unique contributors per post
- total_contributions_per_user.csv: Lists total contributions per user across all posts

Author: Improved by Manus
"""

import csv
import json
import logging
import re
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple, Any

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def fetch_all_bullhorn_topics() -> Tuple[List[int], List[Dict[str, Any]]]:
    """
    Fetch all Bullhorn topics from the Ansible forum.
    
    Iteratively retrieves all topic pages from the Ansible forum's Bullhorn category,
    extracting topic IDs, titles, view counts, and like counts.
    
    Returns:
        Tuple containing:
            - List of topic IDs
            - List of dictionaries with topic metadata (id, title, views, like_count)
    """
    post_ids: List[int] = []
    views_per_edition: List[Dict[str, Any]] = []
    page = 0

    while True:
        url = f"https://forum.ansible.com/c/news-bullhorn/17/l/latest.json?page={page}"
        logger.info(f"Fetching page {page}")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch page {page}: {e}")
            break

        data = response.json()
        topics = data.get("topic_list", {}).get("topics", [])

        if not topics:
            logger.info(f"No more topics found after page {page}")
            break

        for topic in topics:
            topic_id = topic.get("id")
            title = topic.get("title", "").strip()
            views = topic.get("views", 0)
            like_count = topic.get("like_count", 0)

            if topic_id:
                post_ids.append(topic_id)
                views_per_edition.append({
                    "id": topic_id,
                    "title": title,
                    "views": views,
                    "like_count": like_count
                })

        page += 1

    logger.info(f"Retrieved {len(post_ids)} topics in total")
    return post_ids, views_per_edition


def fetch_raw_markdown(post_id: int) -> str:
    """
    Fetch raw Markdown content for a specific post.
    
    Args:
        post_id: The ID of the post to fetch
        
    Returns:
        The raw Markdown content of the post as a string, or an empty string if the fetch fails
    """
    url = f"https://forum.ansible.com/raw/{post_id}"
    logger.info(f"Fetching raw content for post {post_id}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch post {post_id}: {e}")
        return ""


def extract_user_and_link(
    post_id: int, 
    markdown_text: str, 
    keywords: Tuple[str, ...] = ("shared", "said", "contributed")
) -> List[Dict[str, str]]:
    """
    Extract user names and matrix links from Markdown text.
    
    Searches for lines containing user mentions with matrix links followed by specified keywords,
    which indicate user contributions.
    
    Args:
        post_id: The ID of the post being processed
        markdown_text: The raw Markdown content to search
        keywords: Tuple of keywords that indicate user contributions
        
    Returns:
        List of dictionaries containing post_id, user name, and matrix link
    """
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


def save_to_csv(filename: str, data: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    """
    Save data to a CSV file.
    
    Args:
        filename: The name of the CSV file to create
        data: List of dictionaries containing the data to save
        fieldnames: List of column names for the CSV
    """
    try:
        with open(filename, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for entry in data:
                writer.writerow(entry)
        logger.info(f"Successfully saved {len(data)} rows to {filename}")
    except IOError as e:
        logger.error(f"Failed to write to {filename}: {e}")


def count_users_per_post(filtered_data: List[Dict[str, Any]]) -> Dict[int, Set[str]]:
    """
    Count unique users per post.
    
    Args:
        filtered_data: List of dictionaries containing post_id and user information
        
    Returns:
        Dictionary mapping post_id to sets of unique users
    """
    user_map: Dict[int, Set[str]] = defaultdict(set)
    
    for row in filtered_data:
        post_id = row["post_id"]
        user = row["user"]
        user_map[post_id].add(user)
        
    return user_map


def count_contributions_per_user(filtered_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Count total contributions per user across all posts.
    
    Args:
        filtered_data: List of dictionaries containing user contribution data
        
    Returns:
        Dictionary mapping usernames to their contribution counts
    """
    user_contributions: Dict[str, int] = defaultdict(int)
    
    for row in filtered_data:
        user = row["user"].strip()
        user_contributions[user] += 1
        
    return user_contributions


def main() -> None:
    """
    Main function to run the complete Bullhorn data extraction pipeline.
    
    Executes the following steps:
    1. Fetch all Bullhorn topics
    2. Save view and like counts per edition
    3. Extract user contributions with matrix links
    4. Generate statistics on users per post
    5. Generate statistics on contributions per user
    """
    # Step 1: Fetch all topic info
    post_ids, views_per_edition = fetch_all_bullhorn_topics()
    
    # Step 2: Save views_per_edition to CSV
    save_to_csv(
        "views_per_edition.csv", 
        views_per_edition, 
        ["id", "title", "views", "like_count"]
    )
    
    # Step 3: Collect and save filtered user + matrix links
    filtered_data = []
    for pid in post_ids:
        raw_md = fetch_raw_markdown(pid)
        user_link_matches = extract_user_and_link(pid, raw_md)
        filtered_data.extend(user_link_matches)
    
    # Create mapping from post_id to title
    id_to_title = {entry["id"]: entry["title"] for entry in views_per_edition}
    
    # Prepare enriched data with titles
    enriched_data = []
    for row in filtered_data:
        post_id = int(row["post_id"])
        enriched_data.append({
            "post_id": post_id,
            "title": id_to_title.get(post_id, ""),
            "user": row["user"],
            "matrix_link": row["matrix_link"]
        })
    
    # Save enriched data to CSV
    save_to_csv(
        "bullhorn_filtered_lines.csv", 
        enriched_data, 
        ["post_id", "title", "user", "matrix_link"]
    )
    
    logger.info(f"Extracted {len(filtered_data)} matching lines to bullhorn_filtered_lines.csv")
    
    # Step 4: Count number of unique users per post_id
    user_map = count_users_per_post(filtered_data)
    
    # Prepare user count data with titles
    user_count_data = []
    for pid, users in user_map.items():
        user_count_data.append({
            "id": pid,
            "title": id_to_title.get(pid, ""),
            "number_of_users": len(users)
        })
    
    # Save user count data to CSV
    save_to_csv(
        "user_count_per_post.csv", 
        user_count_data, 
        ["id", "title", "number_of_users"]
    )
    
    logger.info(f"Created user_count_per_post.csv with {len(user_map)} rows")
    
    # Step 5: Count contributions per user
    user_contributions = count_contributions_per_user(filtered_data)
    
    # Prepare user contributions data
    contributions_data = [
        {"user": user, "contributions": count}
        for user, count in sorted(user_contributions.items(), key=lambda x: x[1], reverse=True)
    ]
    
    # Save user contributions to CSV
    save_to_csv(
        "total_contributions_per_user.csv", 
        contributions_data, 
        ["user", "contributions"]
    )
    
    logger.info(f"Saved total contributions per user to total_contributions_per_user.csv")


if __name__ == "__main__":
    main()
