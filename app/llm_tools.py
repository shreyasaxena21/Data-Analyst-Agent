import os
import sys
import re
import json
import io
from io import StringIO

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import duckdb
from bs4 import BeautifulSoup
import requests
from openai import OpenAI
from dotenv import load_dotenv

from .utils import image_to_base64_uri

# Load environment variables
load_dotenv()

# Initialize the OpenAI client with the AI Pipe base URL
ai_pipe_base_url = os.getenv("AI_PIPE_BASE_URL")
if not ai_pipe_base_url:
    raise ValueError("AI_PIPE_BASE_URL environment variable is not set. Please set it in your .env file.")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=ai_pipe_base_url
)

# Step 1: Function to scrape and clean the Wikipedia table
def scrape_highest_grossing(url):
    tables = pd.read_html(url)

    # Find the correct table
    df = None
    for table in tables:
        if 'Worldwide gross' in table.columns or 'Gross' in table.columns:
            df = table
            break

    if df is None:
        raise ValueError("No table with 'Worldwide gross' found.")

    # Standardize column names
    df.columns = [col.strip() for col in df.columns]
    if 'Gross' in df.columns:
        df.rename(columns={'Gross': 'Worldwide gross'}, inplace=True)

    # Clean Worldwide gross safely
    df['Worldwide gross'] = (
        df['Worldwide gross']
        .fillna('')
        .astype(str)
        .str.extract(r'([\d,\.]+)')[0]  # only keep numbers and decimal points
        .str.replace(',', '', regex=False)
    )
    df['Worldwide gross'] = pd.to_numeric(df['Worldwide gross'], errors='coerce')
    df = df.dropna(subset=['Worldwide gross'])


    # Clean Year column if present
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

    # Drop rows without valid gross
    df = df.dropna(subset=['Worldwide gross'])
    return df

# Alias for generated scripts
scrape_data = scrape_highest_grossing

# -------------------------------------
# Wrapped analysis code into a function
# -------------------------------------
def run_highest_grossing_analysis():
    """Scrapes Wikipedia's highest-grossing films data, runs analysis, and returns results."""
    url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
    df = scrape_highest_grossing(url)

    # Analysis
    count_2bn_before_2000 = df[(df['Worldwide gross'] >= 2000) & (df['Year'] < 2000)].shape[0]
    earliest_1_5bn_film = df[df['Worldwide gross'] > 1500].nsmallest(1, 'Year')['Title'].values[0]

    # Clean Rank and Peak columns to be numeric before correlation
    df['Rank'] = pd.to_numeric(df['Rank'], errors='coerce')
    df['Peak'] = pd.to_numeric(df['Peak'], errors='coerce')
    df = df.dropna(subset=['Rank', 'Peak'])

    correlation_rank_peak = df['Rank'].corr(df['Peak'])

    # Scatterplot
    plt.figure(figsize=(10, 6))
    sns.regplot(
        x='Rank', y='Peak', data=df,
        scatter_kws={'alpha': 0.5},
        line_kws={'color': 'red', 'linestyle': 'dotted'}
    )
    plt.title('Scatterplot of Rank vs Peak')
    plt.xlabel('Rank')
    plt.ylabel('Peak')
    plt.tight_layout()

    # Encode the plot
    fig = plt.gcf()
    base64_img = image_to_base64_uri(fig)
    plt.close()

    result = [
        f"{count_2bn_before_2000} $2 bn movies were released before 2000.",
        f"The earliest film that grossed over $1.5 bn is '{earliest_1_5bn_film}'.",
        f"The correlation between Rank and Peak is {correlation_rank_peak:.2f}.",
        base64_img
    ]

    return result

# DuckDB query execution
def run_duckdb_query(query: str) -> pd.DataFrame:
    con = duckdb.connect(database=':memory:', read_only=False)
    try:
        return con.execute(query).fetchdf()
    finally:
        con.close()


def run_indian_high_court_analysis():
    """
    Runs analysis on Indian High Court case data stored in S3 parquet files.
    Returns charts and insights as base64-encoded images.
    """
    try:
        # --- Load dataset from S3 ---
        query = """
        SELECT * 
        FROM read_parquet('s3://ada-project-files/indian_high_court/parquet/casetime.parquet')
        """
        df = duckdb.query(query).to_df()

        # Convert judge_date to datetime
        df["judge_date"] = pd.to_datetime(df["judge_date"], errors="coerce")

        # Compute case duration in days
        df["duration_days"] = (df["disp_date"] - df["reg_date"]).dt.days

        # --- Analysis 1: yearly trend ---
        df["year"] = df["judge_date"].dt.year
        yearly_counts = df.groupby("year").size().reset_index(name="case_count")

        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=yearly_counts, x="year", y="case_count", marker="o", ax=ax1)
        ax1.set_title("Yearly Case Counts in Indian High Courts")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Number of Cases")
        fig1.tight_layout()
        img1 = image_to_base64_uri(fig1)
        plt.close(fig1)

        # --- Analysis 2: duration distribution ---
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.histplot(df["duration_days"].dropna(), bins=50, kde=True, ax=ax2)
        ax2.set_title("Distribution of Case Durations")
        ax2.set_xlabel("Duration (days)")
        ax2.set_ylabel("Frequency")
        fig2.tight_layout()
        img2 = image_to_base64_uri(fig2)
        plt.close(fig2)

        # --- Analysis 3: court-wise counts ---
        court_counts = df["court_name"].value_counts().reset_index()
        court_counts.columns = ["court_name", "case_count"]

        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.barplot(data=court_counts.head(10), x="case_count", y="court_name", ax=ax3)
        ax3.set_title("Top 10 High Courts by Case Count")
        ax3.set_xlabel("Case Count")
        ax3.set_ylabel("Court Name")
        fig3.tight_layout()
        img3 = image_to_base64_uri(fig3)
        plt.close(fig3)

        return {
            "status": "success",
            "analysis": [
                {"title": "Yearly Case Counts", "image": img1},
                {"title": "Case Duration Distribution", "image": img2},
                {"title": "Top 10 High Courts by Case Count", "image": img3},
            ]
        }

    except Exception as e:
        logging.error("Error in run_indian_high_court_analysis: %s", str(e), exc_info=True)
        return {"status": "error", "message": str(e)}
   

# LLM code generation
def generate_python_code(task: str, context: str) -> str:
    prompt = f"""
You are a data analyst agent. Your task is to write a Python script to perform a data analysis task.
You have the following tools and libraries available:
- pandas as pd
- matplotlib.pyplot as plt
- seaborn as sns
- The `scrape_data(url)` function: `df = scrape_data(url)` to scrape a table from a Wikipedia page. The dataframe returned by this function is already cleaned and ready for analysis. **Do not add any additional data cleaning steps, especially for 'Worldwide gross'.**
- The `image_to_base64_uri(fig)` function: `base64_img = image_to_base64_uri(fig)` to encode a matplotlib figure to a base64 data URI.
- The `run_duckdb_query(query)` function: `df = run_duckdb_query("SELECT * FROM my_table")` to execute SQL queries using DuckDB.

The analysis task is described below. Your script should:
1. Load the data using `scrape_data(url)`.
2. Generate any requested visualizations.
3. Store the final answers in a variable called `result`.
4. The final output of your script **must** be `print(json.dumps(result))`.

---
Context (available data and schema):
{context}
---
Task:
{task}

Only return the Python code, do not add any explanations or extra text.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates Python code."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    code = response.choices[0].message.content

    # --- SANITIZATION STEP ---
    # Remove any Worldwide gross cleaning that uses .str
    import re
    code = re.sub(
        r"df\[['\"]Worldwide gross['\"]\]\s*=\s*df\[['\"]Worldwide gross['\"]\]\.str[^\n]*\n?",
        "",
        code
    )
    code = re.sub(
        r"df\[['\"]Worldwide gross['\"]\]\s*=\s*df\[['\"]Worldwide gross['\"]\][^\n]*\n?",
        "",
        code
    )

    return code



# Execute generated Python code
def execute_python_code(code: str, data_context: dict) -> any:
    cleaned_code = code.strip().strip('```python').strip('```')

    exec_globals = {
        'pd': pd,
        'plt': plt,
        'sns': sns,
        'scrape_data': scrape_data,
        'image_to_base64_uri': image_to_base64_uri,
        'run_duckdb_query': run_duckdb_query,
        '__builtins__': {
            'print': print,
            '__import__': __import__,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'len': len,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
            'json': json,
            're': re
        },
        **data_context,
    }

    # --- UNIVERSAL CLEANING GUARD ---
    def clean_numeric_columns(df, cols):
        for col in cols:
            if col in df.columns:
                # Extract only numeric/decimal parts
                df[col] = (
                    df[col]
                    .fillna('')
                    .astype(str)
                    .str.extract(r'([\d\.]+)')[0]
                )
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df

    exec_globals['clean_numeric_columns'] = clean_numeric_columns

    # Redirect stdout
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()

    try:
        # Inject cleaning before any analysis runs
        injected_cleaning = """
# --- Auto-clean key numeric columns ---
if 'Worldwide gross' in df.columns or 'Rank' in df.columns or 'Peak' in df.columns:
    df = clean_numeric_columns(df, ['Worldwide gross', 'Rank', 'Peak'])
    df = df.dropna(subset=['Worldwide gross', 'Rank', 'Peak'])
"""
        # Combine injected cleaning with original code
        safe_code = re.sub(
            r"(df\s*=\s*scrape_data\(.*\))",
            r"\1\n" + injected_cleaning,
            cleaned_code,
            count=1
        )

        exec(safe_code, exec_globals)
        output = redirected_output.getvalue().strip()

        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return {"error": "Generated code did not output valid JSON.", "raw_output": output, "code": safe_code}
        else:
            return {"error": "Generated code produced no output.", "code": safe_code}

    except Exception as e:
        return {"error": f"Code execution failed: {str(e)}", "code": cleaned_code}
    finally:
        sys.stdout = old_stdout



# Run analysis only if executed directly
if __name__ == "__main__":
    print(json.dumps(run_highest_grossing_analysis()))
    print(json.dumps(run_indian_high_court_analysis()))
