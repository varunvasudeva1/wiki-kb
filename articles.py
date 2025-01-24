import os
import requests
from bs4 import BeautifulSoup, Tag
import time
import logging
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

PROCESS_DIR = "process"
BASE_URL = "https://en.wikipedia.org"
LEVEL = 4


def get_subpages():
    """
    Fetches the vital articles page and extracts all subpage links for a given level.
    Returns a set of URLs pointing to each subpage.
    """
    sub_url = f"/wiki/Wikipedia:Vital_articles/Level/{LEVEL}/"
    main_url = urljoin(BASE_URL, sub_url)

    try:
        response = requests.get(main_url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch {main_url}: {e}")
        return set()

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all subpages under the specified level
    subpages = set()
    for link in soup.find_all("a", href=True):
        if sub_url in link["href"]:
            full_url = urljoin(BASE_URL, link["href"])
            # Only get those pages where something follows /, i.e., Level/4/People or Level/4/Arts
            if full_url.split("/")[-1] != "" and "Current_total" not in full_url:
                subpages.add(full_url)

    return subpages


def extract_article_names(url):
    """
    Visits a given URL and extracts only the article names from <a> tags.
    Specifically designed to handle nested links like your example.
    Returns a set of unique article names.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return set()

    soup = BeautifulSoup(response.text, "html.parser")

    content = soup.find("div", {"class": "mw-content-ltr mw-parser-output"})
    if not content:
        logging.warning(f"Main content div not found in {url}.")
        return set()

    all_articles = set()  # Use a set to avoid duplicates

    if isinstance(content, Tag):
        for ol in content.find_all("ol"):
            for li in ol.find_all("li"):
                # Look for direct child anchor tags
                links = li.find_all("a", href=True)

                if len(links) == 1:
                    article_text = links[0].get_text(strip=True)
                    all_articles.add(article_text)
                else:
                    # If there are multiple links, extract the innermost one
                    for link in reversed(links):
                        # Check if this is an innermost link (no child <a> tags)
                        if not any(l.name == "a" for l in link.children):
                            article_text = link.get_text(strip=True)
                            all_articles.add(article_text)

    logging.info(f"Found {len(list(all_articles))} articles for given URL.")
    return all_articles


def get_articles():
    """
    Main function that coordinates the extraction process.
    """
    logging.info("Starting extraction process.")
    os.makedirs(PROCESS_DIR, exist_ok=True)

    subpages = get_subpages()
    logging.info(f"Found {len(subpages)} subpages: {subpages}")

    all_articles = set()

    for url in subpages:
        logging.info(f"Processing: {url}")
        try:
            articles = extract_article_names(url)
            all_articles.update(articles)
            time.sleep(0.5)  # Be polite and don't overload the server
        except Exception as e:
            logging.error(f"Error processing {url}: {e}")

    # Save results to file
    with open(os.path.join(PROCESS_DIR, "desired_articles.txt"), "w") as f:
        for article in sorted(all_articles):
            f.write(article + "\n")

    logging.info(f"Saved {len(all_articles)} unique articles.")


if __name__ == "__main__":
    get_articles()
