# PubMed Article Summarizer

**PubMed Article Summarizer** is an easy-to-use application designed to help users quickly find and summarize scientific literature on topics of interest. Leveraging OpenAI's powerful language models and PubMed's comprehensive database, this tool streamlines the research process, enabling users to gain concise insights from vast amounts of scientific data.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)

## Features

- **Keyword Extraction:** Automatically extracts and refines keywords from user queries using GPT-based models to enhance search relevance.
- **Synonym Expansion:** Expands search terms with synonyms to include related articles that may use different terminology.
- **RAG Pipeline:** Utilizes Retrieval-Augmented Generation (RAG) to build an index of article chunks and retrieve the most relevant information.
- **Summarization:** Generates concise summaries of selected articles, highlighting key findings and methodologies.
- **Streamlit Interface:** Provides an intuitive web-based interface for seamless interaction.

## Installation

Ensure you have [Python 3.12](https://www.python.org/downloads/) installed on your system.

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/pubmed-article-summarizer.git
    cd pubmed-article-summarizer
    ```

2. **Install Dependencies:**

    The project uses `make` for managing installation and testing tasks.

    ```bash
    make install
    ```

    *This command installs all necessary Python packages as specified in `requirements.txt`.*

3. **Set Up Environment Variables:**

    Obtain your API keys for [OpenAI](https://platform.openai.com/account/api-keys).

- Create a `.env` file in the root directory:

        ```bash
        touch .env
        ```

- Add your API keys to the `.env` file:

        ```env
        OPENAI_API_KEY=your_openai_api_key_here
        ```

## Usage

Launch the Streamlit application to start summarizing PubMed articles based on your research query.

```bash
streamlit run app/streamlit_app.py
```

## Testing

```bash
make test
```
