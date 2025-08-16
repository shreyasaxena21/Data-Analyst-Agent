import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List, Optional
from pathlib import Path
import pandas as pd
import asyncio
import io
import os
import json
import re
import logging

from dotenv import load_dotenv
from .llm_tools import generate_python_code, execute_python_code

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

@app.post("/api/")
async def analyze_data(
    questions: UploadFile = File(..., description="The questions to be answered."),
    files: Optional[List[UploadFile]] = File(None, description="Optional data files.")
):
    try:
        # Read the questions file
        questions_content = (await questions.read()).decode("utf-8")
        
        data_context = {}
        context_string = ""

        # Process uploaded files and build context
        if files:
            for file in files:
                file_ext = Path(file.filename).suffix.lower()
                file_content = await file.read()

                # Safer variable name (no special chars, no starting digit)
                var_name = re.sub(r'\W|^(?=\d)', '_', Path(file.filename).stem)

                if file_ext == ".csv":
                    df = pd.read_csv(io.StringIO(file_content.decode("utf-8")))
                    data_context[var_name] = df
                    context_string += (
                        f"A pandas DataFrame named `{var_name}` has been loaded from "
                        f"'{file.filename}'. It has columns: {', '.join(df.columns)}\n\n"
                    )

                elif file_ext == ".json":
                    json_data = json.loads(file_content.decode("utf-8"))
                    data_context[var_name] = json_data
                    context_string += f"A Python object `{var_name}` was loaded from '{file.filename}'.\n\n"

                elif file_ext in [".png", ".jpg", ".jpeg", ".gif"]:
                    context_string += (
                        f"An image file '{file.filename}' is available. "
                        f"It is not loaded into a variable but can be referenced.\n\n"
                    )

                else:
                    context_string += (
                        f"Unknown file type '{file.filename}' was provided. "
                        "Not automatically loaded.\n\n"
                    )

        # Combine questions and context
        full_llm_context = f"User Questions:\n{questions_content}\n\nAdditional Data Context:\n{context_string}"

        # Use a timeout (3 min total)
        try:
            code = await asyncio.wait_for(
                asyncio.to_thread(generate_python_code, questions_content, full_llm_context),
                timeout=120
            )

            result = await asyncio.wait_for(
                asyncio.to_thread(execute_python_code, code, data_context),
                timeout=60
            )

            return {"status": "success", "result": result}

        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Request timed out. The analysis took too long.")

    except Exception as e:
        logging.error("Error in /api/: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
