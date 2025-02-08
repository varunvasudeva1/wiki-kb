import os
import re
import json
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


def load_config():
    with open("config.json", "r+") as file:
        config = json.load(file)
    return config


def is_config_valid():
    config = load_config()
    if config["special_level"] <= config["general_level"]:
        return False
    if config["special_level"] != None:
        if config["special_level_topics"] == []:
            return False

    return True


def get_subpages(mode, level, main_url):
    """
    Fetches the vital articles page and extracts all subpage links for a given level.
    Returns a set of URLs pointing to each subpage.
    """
    config = load_config()

    try:
        response = requests.get(main_url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch {main_url}: {e}")
        return set()

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all subpages under the specified level
    subpages = set()
    special_level_topics: list[str] = config["special_level_topics"]
    if special_level_topics == None or len(special_level_topics) == 0:
        logging.error(
            "Special level found but no associated special level topics found. Please specify some topics and re-run the script."
        )
        return set()

    special_level_topics: list[str] = [
        topic.replace(" ", "_") for topic in special_level_topics
    ]
    for link in soup.find_all("a", href=True):
        full_url = urljoin(BASE_URL, link["href"])

        # Only get those pages where something follows /, i.e., Level/4/People or Level/4/Arts
        def extract_topic(text):
            """
            Extracts everything after "Level/{some number}/" from a string using regex.

            Args:
                text: The input string to search within.

            Returns:
                The string found after "Level/{some number}/", or None if the pattern is not found.
            """
            pattern = r"Level/\d+/(.*)"  # Regex pattern: Level/digits/(capture everything after)
            match = re.search(pattern, text)
            if match:
                return match.group(1)  # Return the content of the first capturing group
            else:
                return None  # Return None if no match is found

        level_string = f"Level/{level}"
        topic = extract_topic(full_url)
        if (
            topic != None
            and topic != ""
            and "Current_total" not in full_url
            and level_string in full_url
        ):
            if mode == "special":
                if topic in special_level_topics:
                    subpages.add(full_url)
            else:
                subpages.add(full_url)

    return subpages


def extract_article_names(url, level):
    """
    Visits a given URL and extracts only the article names from <a> tags.
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

    if not isinstance(content, Tag):
        logging.error(
            "Content was not traversable. The link being parsed is not of the correct schema, please report it to the author."
        )
        return set()

    if level <= 3:
        # For levels 3 and below, extract <a> links from within tables
        tables = content.find_all("table")
        for table in tables:
            for link in table.find_all("a", href=True):
                article_text = link.get_text(strip=True)
                all_articles.add(article_text)
    else:
        # For levels 4 and 5, extract innermost <a> links nested within <ol> tags
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
    if not is_config_valid():
        logging.error(
            "Invalid configuration file found. Please ensure `general_level` < `special_level` and, if `special_level` is not null, there is a valid list for `special_level_topics`."
        )
        return

    config = load_config()
    all_articles = set()

    for mode in ["general", "special"]:
        # for mode in ["general"]:
        logging.info(f"Getting {mode} articles.")
        level = config[f"{mode}_level"]
        sub_url = f"/wiki/Wikipedia:Vital_articles/Level/{level}"
        main_url = urljoin(BASE_URL, sub_url)
        if level <= 3:
            logging.info(f"Processing: {main_url}")
            try:
                articles = extract_article_names(main_url, level)
                all_articles.update(articles)
                time.sleep(0.5)
            except Exception as e:
                logging.error(f"Error processing {main_url}: {e}")
        else:
            subpages = get_subpages(mode, level, main_url)
            logging.info(f"Found {len(subpages)} subpages: {subpages}")

            for url in subpages:
                logging.info(f"Processing: {url}")
                try:
                    articles = extract_article_names(url, level)
                    all_articles.update(articles)
                    time.sleep(0.5)
                except Exception as e:
                    logging.error(f"Error processing {url}: {e}")

        # Save results to file
        with open(os.path.join(PROCESS_DIR, f"{mode}_articles.txt"), "w") as f:
            for article in sorted(all_articles):
                f.write(article + "\n")

        logging.info(f"Saved {len(all_articles)} unique articles.")


if __name__ == "__main__":
    get_articles()
