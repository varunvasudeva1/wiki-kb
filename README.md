# Wiki KB: Customizable, embedding-ready knowledge base

This repository contains a set of scripts designed to convert desired articles from a Wikipedia XML dump into plain text formatted files, making them suitable for building embedded model knowledge bases. Knowledge bases like this can enable retrieval-augmented generation (RAG), making it possible to increase recall accuracy and prevent hallucinations in language models. Combined with reasoning models, it is a potent combination that opens the door to assistants that have the ability to perform competent reasoning with real-world information.

## Description

The project consists of scripts that:

1. Extract lists of desired Wikipedia article titles.
2. Convert those articles from their original Wikipedia XML format into clean TXT files.

The extracted text can be used as training data for language models, semantic search engines, or other natural language processing applications.

Wikipedia dumps, even those containing only revision for each article, are large and generally unwieldy documents (expectedly so). Embedding an entire Wikipedia dump on a consumer GPU without running multiple instances of the embedding model being used would take an unbelievably long amount of time. Thus, we filter out articles based on the level of specificity required.

### Levels

Wikipedia moderators compile and maintain a [5 level "vital article" list](https://en.wikipedia.org/wiki/Wikipedia:Vital_articles) that categorizes articles by how fundamental their inclusion is in a wiki. This list allows for users to have control over the size of their knowledge base. Below is a table describing the distribution of data by level:

| Level | Number of Articles |
| ----- | ------------------ |
| 1     | 10                 |
| 2     | 100                |
| 3     | 1000               |
| 4     | 10000              |
| 5     | 50000              |

Inspired by Einstein's approach to organizing knowledge, we break down Wikipedia articles into two distinct categories: general and special. The general level encompasses the foundational articles that form the broad base of your knowledge base (KB), ensuring it contains essential information across various domains. Meanwhile, the special level focuses on in-depth coverage of specific topics you choose, allowing for highly customized and comprehensive knowledge without sacrificing the core utility of your KB.

## Installation

Run the following script to clone the repository and install dependencies:

```bash
git clone https://github.com/varunvasudeva1/wiki-kb.git
cd wiki-kb
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

1) Download your Wikipedia dump of choice from [here](https://meta.wikimedia.org/wiki/Data_dump_torrents). A torrent download is recommended.
2) Uncompress the `.bz2` result to obtain an `.xml` file (warning: depending on the device you run this action on, it may take some time). Place this at the root of the `wiki-kb` directory.
3) Configure options in `config.json`.
4) Run the script:
    ```bash
    python main.py
    ```

### `config.json`

- `data_filename`: Filename of the XML containing articles.
- `general_level`: The desired level for your KB's general knowledge. Set value between 1 and 5.
- `special_level`: The desired level for your KB's specialized knowledge in select few topics. Set value between 1 and 5 or `null` if no specialized knowledge topics are needed. Value must be greater than `general_level`.
- `special_level_topics`: The topics that the special level applies to. Set to `[]` if no specialized knowledge topics are needed.

### Embedding

To utilize your KB with language models, the resulting text outputs will need to be embedded by an embedding model so that language models can use them before providing answers. If you're using a custom RAG pipeline, you probably don't need to read this section anyway. 

If you don't know what embedding is and just want a way to ground your LLM responses, follow these steps to build your embedded KB:

1) Install [Open WebUI](https://github.com/open-webui/open-webui).
2) Navigate to `Admin Settings` > `Documents`. 
   - Select between `Ollama` and `OpenAI`. If `Ollama`, set the appropriate embedding model. For a good model that balances runtime and performance, run `ollama pull nomic-embed-text` from a terminal and then select it as the `Embedding Model`.
   - Crank `Embedding Batch Size` to the maximum of `8192`.
   - Save your configuration.
3) Make your way to `Workspace` > `Knowledge` > `+`. Choose a title and description.
4) Upload your `output` directory.
5) Wait. Embedding thousands of documents may take quite some time.

To see my detailed guide on setting up Open WebUI with other components for a complete LLM server, click [here](https://github.com/varunvasudeva1/llm-server-docs).

> [!TIP]
> To strike a balance between efficiency of embedding and size of knowledge base, (GL = 3, SL = 4) or (GL = 4, SL = 5) is recommended. This will let your KB be complete enough to be very useful and not so large that embedding and uploading takes forever.

## Contributing

Contributions are welcome! If you'd like to contribute, please fork this repository and submit a pull request. Please discuss any major changes with the maintainers first via issues.

## License

This project is licensed under the [MIT License](LICENSE).