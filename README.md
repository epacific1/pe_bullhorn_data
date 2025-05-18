# 🐂 Bullhorn Analyzer

**Bullhorn Analyzer** is a Python script that extracts and analyses contributor data from the [Ansible Bullhorn](https://forum.ansible.com/c/news/bullhorn/17) newsletter hosted on Discourse. It produces structured reports on post views, contributor mentions, and user activity across all issues.

---

## 📦 Features

- Fetches **all pages** of Bullhorn topics using the Discourse API
- Extracts:
  - `post_id`, `title`, `views`, and `like_count` for each issue
- Downloads the **raw Markdown content** of each post
- Searches for contributor mentions using keywords:
  - `shared`, `said`, or `contributed`
- Extracts contributor data in Markdown format:
  ```
  [username](https://matrix.to/#/@username:matrix.org) said
  ```
- Generates 3 output CSV files

---

## 📁 Output Files

| File                          | Description                                                  |
|-------------------------------|--------------------------------------------------------------|
| `views_per_edition.csv`       | Post metadata: `id`, `title`, `views`, `like_count`         |
| `bullhorn_filtered_lines.csv` | Contributor mentions: `post_id`, `title`, `user`, `matrix_link` |
| `user_count_per_post.csv`     | Number of unique users mentioned per post                    |

---

## 🚀 Getting Started

### 1. Clone the Repository or Copy the Script

```bash
git clone https://github.com/yourname/bullhorn-analyzer.git
cd bullhorn-analyzer
```

### 2. Install Requirements

Only the standard library and `requests` are used:

```bash
pip install requests
```

### 3. Run the Script

```bash
python bullhorn_analyzer.py
```

---

## 📊 How It Works

1. **Pagination**:  
   The script pulls all available pages from the Bullhorn category using:
   ```
   https://forum.ansible.com/c/news-bullhorn/17/l/latest.json?page=n
   ```

2. **Metadata Extraction**:  
   It collects the `id`, `title`, `views`, and `like_count` for each topic.

3. **Raw Post Retrieval**:  
   For each topic, it downloads the raw Markdown via:
   ```
   https://forum.ansible.com/raw/{post_id}
   ```

4. **Contributor Matching**:  
   It scans for Markdown-formatted lines like:
   ```
   [Felix Fontein](https://matrix.to/#/@felixfontein:matrix.org) contributed
   ```

   and extracts:
   - `user` from `[username]`
   - `matrix_link` from `(https://matrix.to/#/...)`

5. **Aggregation**:
   - Counts number of **unique contributors per post**
   - Links each mention to its corresponding post `title`

---

## 🧠 Customisation

### Change the Keywords:
To match different terms (e.g., “announced”), modify this line in the code:

```python
keywords=("shared", "said", "contributed")
```

---

## 📂 File Structure

```
.
├── bullhorn_analyzer.py            # Main script
├── views_per_edition.csv           # Post metadata report
├── bullhorn_filtered_lines.csv     # Contributor mentions
├── user_count_per_post.csv         # User summary per post
└── README.md                       # Project documentation
```

---

## 🙋 FAQ

### Why are some posts missing from the contributor CSV?
Only posts that include a Markdown-formatted contributor line with keywords like "shared" or "contributed" are included in `bullhorn_filtered_lines.csv`.

### Why is the same user missing from one post but not another?
The script looks specifically for lines where a Matrix link is present in Markdown `[text](url)` format and contains one of the target keywords.

---

## 🛠️ Roadmap

- Add timestamp and author fields to output
- Export HTML versions of the reports
- Add CLI arguments for filtering and output control

---

## 🤝 Contributing

Contributions are welcome! If you spot a bug or have an idea for a feature, feel free to open an issue or a pull request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

