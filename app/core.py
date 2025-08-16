import duckdb
import pandas as pd
import io

def run_duckdb_query(query: str, s3_access_key: str, s3_secret_key: str):
    """
    Executes a DuckDB query, especially for S3 access.
    """
    con = duckdb.connect(':memory:')
    
    # Configure S3 access
    con.sql(f"SET s3_access_key_id = '{s3_access_key}';")
    con.sql(f"SET s3_secret_access_key = '{s3_secret_key}';")
    
    try:
        result = con.execute(query).fetchdf()
        return result
    finally:
        con.close()