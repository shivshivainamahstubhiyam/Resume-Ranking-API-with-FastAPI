import io
import os
import tempfile
from typing import List

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from utils.document_processor import extract_text_from_file
from utils.llm_processor import extract_criteria_with_llm, score_resume_with_llm

# Initialize FastAPI app
app = FastAPI(
    title="Resume Ranking API",
    description="API for extracting job criteria and ranking resumes based on job descriptions",
    version="1.0.0",
)


class CriteriaResponse(BaseModel):
    criteria: List[str]


@app.post(
    "/extract-criteria",
    response_model=CriteriaResponse,
    summary="Extract ranking criteria from job description",
    description="Upload a job description file (PDF or DOCX) and extract key ranking criteria",
    tags=["Criteria Extraction"],
)
async def extract_criteria(file: UploadFile = File(...)):
    """
    Extract ranking criteria from a job description file.

    Parameters:
    - file: Job description document (PDF or DOCX)

    Returns:
    - JSON object containing a list of extracted criteria
    """
    # Validate file type
    allowed_extensions = [".pdf", ".docx"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}",
        )

    try:
        # Extract text from the uploaded file
        text = await extract_text_from_file(file)
        
        # Process the text with an LLM to extract criteria
        criteria = await extract_criteria_with_llm(text)
        
        return {"criteria": criteria}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post(
    "/score-resumes",
    summary="Score resumes against given criteria",
    description="Upload multiple resumes and score them against provided criteria",
    tags=["Resume Scoring"],
)
async def score_resumes(
    criteria: List[str] = Form(...),
    files: List[UploadFile] = File(...),
):
    """
    Score multiple resumes against provided criteria.

    Parameters:
    - criteria: List of criteria to score resumes against
    - files: List of resume files (PDF or DOCX)

    Returns:
    - Excel/CSV file with scores for each candidate and criterion
    """
    if not criteria:
        raise HTTPException(status_code=400, detail="No criteria provided")
    
    if not files:
        raise HTTPException(status_code=400, detail="No resume files provided")

    # Validate file types
    allowed_extensions = [".pdf", ".docx"]
    for file in files:
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type for {file.filename}. Allowed types: {', '.join(allowed_extensions)}",
            )

    try:
        # Process each resume
        results = []
        for file in files:
            # Extract candidate name from filename
            candidate_name = os.path.splitext(file.filename)[0]
            
            # Extract text from resume
            resume_text = await extract_text_from_file(file)
            
            # Score resume against criteria
            scores = await score_resume_with_llm(resume_text, criteria)
            
            # Calculate total score
            total_score = sum(scores)
            
            # Add to results
            candidate_result = {"Candidate Name": candidate_name}
            for i, criterion in enumerate(criteria):
                # Create a shorter criterion key for the Excel/CSV
                short_criterion = ' '.join(criterion.split()[:3]) + "..."
                candidate_result[short_criterion] = scores[i]
            candidate_result["Total Score"] = total_score
            results.append(candidate_result)
        
        # Sort results by total score (descending)
        results = sorted(results, key=lambda x: x["Total Score"], reverse=True)
        
        # Create DataFrame from results
        df = pd.DataFrame(results)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Resume Scores", index=False)
        
        output.seek(0)
        
        # Return Excel file
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=resume_scores.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resumes: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
