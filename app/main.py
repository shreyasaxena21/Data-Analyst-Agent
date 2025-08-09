import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from typing import List, Optional
from pathlib import Path
import pandas as pd
import asyncio
import io
import os # Import os to load .env file

from .llm_tools import generate_python_code, execute_python_code

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

@app.post("/api/")
async def analyze_data(
    questions: UploadFile = File(..., description="The questions to be answered."),
    files: Optional[List[UploadFile]] = File(None, description="Optional data files.")
):
    try:
        # Read the questions file
        questions_content = (await questions.read()).decode('utf-8')
        
        data_context = {}
        context_string = "" # Initialize context string for LLM
        
        # Process uploaded files and build context for the LLM
        if files:
            for file in files:
                file_ext = Path(file.filename).suffix.lower()
                file_content = await file.read()
                
                # Create a safe variable name from the filename
                var_name = Path(file.filename).stem.replace('-', '_').replace('.', '_')
                
                if file_ext == ".csv":
                    df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
                    data_context[var_name] = df
                    context_string += f"A pandas DataFrame named `{var_name}` has been loaded from '{file.filename}'. It has the following columns: {', '.join(df.columns)}\n\n"
                elif file_ext == ".json":
                    # For JSON, load as a Python object
                    json_data = json.loads(file_content.decode('utf-8'))
                    data_context[var_name] = json_data
                    context_string += f"A Python object named `{var_name}` has been loaded from '{file.filename}'.\n\n"
                elif file_ext in [".png", ".jpg", ".jpeg", ".gif"]:
                    # For images, you might just note their presence or offer to load them
                    # For this project, we'll just note them. The LLM might ask to use them for analysis.
                    context_string += f"An image file named '{file.filename}' is available. Its content is not directly loaded into a variable but can be referenced if needed.\n\n"
                # Add more file types as needed (e.g., .parquet, .xlsx)
                else:
                    context_string += f"An unknown file type '{file.filename}' was provided. Its content is not automatically loaded.\n\n"

        # Combine questions and file context for the LLM
        full_llm_context = f"User Questions:\n{questions_content}\n\nAdditional Data Context:\n{context_string}"

        # Use a timeout to ensure the 3-minute limit
        # Allocate 2 minutes for code generation and 1 minute for execution
        try:
            code = await asyncio.wait_for(
                asyncio.to_thread(generate_python_code, questions_content, full_llm_context),
                timeout=120 # 2 minutes for code generation
            )
            
            result = await asyncio.wait_for(
                asyncio.to_thread(execute_python_code, code, data_context),
                timeout=60 # 1 minute for code execution
            )
            return result
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Request timed out. The analysis took too long.")
            
    except Exception as e:
        # Log the full exception for debugging in production
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)