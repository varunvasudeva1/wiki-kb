# WikiKB: Embedding-ready offline knowledge base

This repository contains a set of scripts designed to convert desired articles from a Wikipedia XML dump into plain text formatted files, making them suitable for building embedded model knowledge bases. Knowledge bases like this can enable retrieval-augmented generation (RAG), making it possible to increase recall accuracy and prevent hallucinations in language models. Combined with reasoning models, it is a potent combination that opens the door to assistants that have the ability to perform competent reasoning with real-world information.

## Description

The project consists of scripts that:

1. Extract lists of desired Wikipedia article titles.
2. Convert those articles from their original Wikipedia XML format into clean TXT files.

The extracted text can be used as training data for language models, semantic search engines, or other natural language processing applications.

Wikipedia dumps, even those containing only revision for each article, are large and generally unwieldy documents (expectedly so). Embedding an entire Wikipedia dump on a consumer GPU without running multiple instances of the embedding model being used would take an unbelievably long amount of time. Thus, we filter out articles based on the level of specificity required.

### Levels

Wikipedia moderators compile and maintain a 5 level list containing article names that rank articles, subjectively, by how fundamental their inclusion is in a wiki. This allows for users to have control over the size of their knowledge base. Below is a table describing the distribution of data by level:

| Level | Number of Articles |
| ----- | ------------------ |
| 1     | 10                 |
| 2     | 100                |
| 3     | 1000               |
| 4     | 10000              |
| 5     | 50000              |

Select a level that will capture the kind of querying you want to do with your wiki. If you/your users ask language models a lot random questions that needed to be factually accurate, a level 4 or 5 would be a better option for you. In contrast, if you have a need to query information from mostly one domain (e.g. mathematics, physics, economics, etc.), a level 3 with a separate injection of domain-specific data might be a better idea. This would effectively translate to the generality of level 3 with the specificity of a level 5 for a given topic.

> [!TIP]
> To strike a balance between efficiency of embedding and size of knowledge base, level 4 is recommended.

## Installation

Run the following script to clone the repository and install dependencies:

```bash
git clone https://github.com/varunvasudeva1/wiki-kb
cd wiki-kb
python -m venv -n .venv
source .venv/bin/activate
pip install requirements.txt
```

## Usage

1) Download your Wikipedia dump of choice from [here](https://meta.wikimedia.org/wiki/Data_dump_torrents). A torrent download is recommended.
2) Uncompress the `.bz2` result to obtain an `.xml` file (warning: depending on the device you run this action on, it may take some time). Place this at the root of the `wiki-kb` directory.
3) Configure options in `config.json`: level.
4) Run the script:
    ```bash
    python main.py
    ```

### Example Output

The converted articles will be saved as individual `.txt` files in the `output/` directory. Each file will contain the full text of a single Wikipedia article, cleaned of markup and formatting.

## Contributing

Contributions are welcome! If you'd like to contribute, please fork this repository and submit a pull request. Please discuss any major changes with the maintainers first via issues.

## License

This project is licensed under the [MIT License](LICENSE).