import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check for required environment variables
if not os.environ.get("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY not set. Please set it in .env file or environment variables.")

# Run the FastAPI application
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
