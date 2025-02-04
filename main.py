import os
import re
import json
import mwxml
import logging
from articles import get_articles

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

PROCESS_DIR = "process"
OUTPUT_DIR = "output"


def load_config():
    with open("config.json", "r+") as file:
        config = json.load(file)
    return config


def load_desired_articles(mode="general"):
    """Loads the list of desired articles from a file. Returns a set of article titles to be processed."""
    desired_file = os.path.join(PROCESS_DIR, f"{mode}_articles.txt")
    if not os.path.exists(desired_file):
        logging.info("Desired articles file does not exist. Creating...")
        get_articles()

    with open(desired_file, "r") as f:
        return set(f.read().splitlines())


def sanitize_title(title):
    """Sanitizes the title by replacing any '/' with '-'."""
    return title.replace("/", "-")


def remove_ref_tags(text):
    """Remove <ref> tags and their contents, even if they span multiple lines or contain nested content."""
    # Pattern to match multi-line ref tags, including nested ones
    ref_pattern = r"<\/?ref[^>]*>|<ref\s*.*?>[\s\S]*?<\/ref>"
    text = re.sub(ref_pattern, "", text, flags=re.IGNORECASE | re.DOTALL)
    return text


def remove_braces(text):
    """Remove {{}} tags and their contents if they exceed 100 characters or contain 'cite'."""
    # Handle multi-line and nested braces without recursion
    brace_pattern = r"\{\{((?:[^{}]|(?=.*?))*)\}\}"

    def should_remove(match):
        content = match.group(1)
        # Check for 'cite' in the content (case-insensitive)
        if (
            "cite" in content.lower()
            or "sfn" in content.lower()
            or "citation needed" in content.lower()
            or "redirect" in content.lower()
        ):
            return ""
        else:
            return match.group(0)

    text = re.sub(brace_pattern, should_remove, text, flags=re.IGNORECASE | re.DOTALL)
    return text


def sanitize_text(text):
    """Sanitize the text by removing various patterns."""
    text = remove_ref_tags(text)
    text = remove_braces(text)

    # Remove other unwanted patterns
    text = (
        text.replace("'''", "").replace("''", "").replace(r"[[", "").replace(r"]]", "")
    )

    return text


def process_page(mode, page, processed_pages):
    """Processes a single Wikipedia page. Writes the page content to a file if it hasn't been processed before and is in desired articles."""
    title = page.title
    sanitized_title = sanitize_title(title)

    # Check if the sanitized title is in the set of desired articles
    if sanitized_title not in processed_pages:
        logging.info(f"Skipping non-desired page: {sanitized_title}")
        return

    output_file_path = os.path.join(OUTPUT_DIR, mode, f"{sanitized_title}.txt")
    with open(output_file_path, "w") as file_out:
        for revision in page:
            text = revision.text
            text = sanitize_text(text)
            file_out.write(text)

    logging.info(f"Processed and saved page: {sanitized_title}")


def main():
    """Main function that coordinates the processing of Wikipedia XML dump. Processes only the pages listed in the respective desired article files."""
    logging.info("Starting processing of Wikipedia XML dump.")
    config = load_config()
    data_filename = config["data_filename"]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PROCESS_DIR, exist_ok=True)

    try:
        with open(data_filename, "rb") as xml_file:
            dump = mwxml.Dump.from_file(xml_file)

            for mode in ["general", "special"]:
                os.makedirs(os.path.join(OUTPUT_DIR, mode), exist_ok=True)
                desired_articles = load_desired_articles(mode)

                if not desired_articles:
                    logging.error("No desired articles to process. Exiting.")
                    return

                for idx, page in enumerate(dump.pages):
                    title = page.title
                    sanitized_title = sanitize_title(title)

                    # Check if the sanitized title is in the set of desired articles
                    if sanitized_title not in desired_articles:
                        continue

                    if idx % 100 == 0:  # Log progress every 100 pages
                        logging.info(f"Processed {idx + 1} pages so far...")

                    process_page(mode, page, desired_articles)

    except KeyboardInterrupt:
        logging.warning("Operation cancelled by user.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        logging.info("Script execution complete.")


if __name__ == "__main__":
    main()
