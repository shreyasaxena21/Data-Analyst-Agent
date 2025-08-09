# Data Analyst Agent

This project deploys a data analyst agent as an API endpoint. It uses a Large Language Model (LLM) to source, prepare, analyze, and visualize data based on natural language task descriptions and optional file attachments.

## Features

* **API Endpoint:** Accepts POST requests with a task description (`questions.txt`) and optional data files.
* **LLM-Powered Analysis:** Leverages an LLM (via an OpenAI-compatible API) to interpret tasks and generate Python code for data processing.
* **Data Sourcing:** Can scrape data from specified URLs.
* **Data Handling:** Processes CSV and JSON files.
* **Visualization:** Generates plots (e.g., scatterplots) as base64-encoded images.
* **Flexible Output:** Returns answers in JSON array or object format.

## Setup and Local Development

Follow these steps to set up and run the project locally.

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/data-analyst-agent.git](https://github.com/your-username/data-analyst-agent.git)
cd data-analyst-agent