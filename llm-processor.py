import os
from typing import List, Dict, Any

# Import OpenAI API
from openai import AsyncOpenAI

# Configure OpenAI client
client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "your-api-key")
)


async def extract_criteria_with_llm(job_description: str) -> List[str]:
    """
    Use an LLM to extract key criteria from a job description.
    
    Args:
        job_description: Text of the job description
        
    Returns:
        List[str]: List of extracted criteria
    """
    # Prepare the prompt
    system_prompt = """
    You are an expert HR system that analyzes job descriptions and extracts key ranking criteria.
    Extract specific criteria related to:
    1. Required skills
    2. Experience (years, specific domains)
    3. Education requirements
    4. Certifications
    5. Technical knowledge
    6. Soft skills
    
    Format each criterion as a clear, standalone requirement. Do not include vague statements.
    Return only the list of criteria, with each item being a specific, measurable requirement.
    """
    
    user_prompt = f"""
    Extract the key ranking criteria from the following job description:
    
    {job_description}
    
    Return ONLY a list of specific criteria, with each item as a clear, standalone requirement.
    """
    
    # Call the LLM
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,  # Low temperature for consistent, focused output
    )
    
    # Process the response
    criteria_text = response.choices[0].message.content.strip()
    
    # Convert to list (handling different possible formats)
    criteria_list = []
    for line in criteria_text.split('\n'):
        # Remove bullet points and numbering
        cleaned_line = line.strip()
        if cleaned_line.startswith(('- ', '• ', '* ', '· ')):
            cleaned_line = cleaned_line[2:].strip()
        elif cleaned_line.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ', '10. ')):
            cleaned_line = cleaned_line[3:].strip()
            
        if cleaned_line and not cleaned_line.startswith(('#', '##', '###')):
            criteria_list.append(cleaned_line)
    
    return criteria_list


async def score_resume_with_llm(resume_text: str, criteria: List[str]) -> List[int]:
    """
    Use an LLM to score a resume against provided criteria.
    
    Args:
        resume_text: Text extracted from the resume
        criteria: List of criteria to score against
        
    Returns:
        List[int]: List of scores (0-5) for each criterion
    """
    # Prepare the prompt
    system_prompt = """
    You are an expert HR system that evaluates resumes against job criteria.
    For each criterion, provide a score from 0 to 5, where:
    
    0: No evidence of meeting the criterion
    1: Minimal evidence, significantly below expectations
    2: Some evidence, but below expectations
    3: Meets expectations
    4: Exceeds expectations
    5: Far exceeds expectations
    
    Be objective and consistent in your scoring. Focus on concrete evidence in the resume.
    """
    
    criteria_str = "\n".join([f"{i+1}. {criterion}" for i, criterion in enumerate(criteria)])
    
    user_prompt = f"""
    Score the following resume against each criterion on a scale of 0-5:
    
    CRITERIA:
    {criteria_str}
    
    RESUME:
    {resume_text}
    
    For each criterion, provide ONLY a numeric score (0-5). Return your answers as a list of numbers in the same order as the criteria, with nothing else.
    """
    
    # Call the LLM
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,  # Low temperature for consistent scoring
    )
    
    # Process the response
    score_text = response.choices[0].message.content.strip()
    
    # Extract scores
    scores = []
    for line in score_text.split('\n'):
        # Try to extract just the numeric score
        line = line.strip()
        try:
            # First, try to extract just the number
            if line.isdigit() and 0 <= int(line) <= 5:
                scores.append(int(line))
            # If that fails, look for patterns like "1. 4" or "Criterion 1: 4"
            elif ': ' in line and line.split(': ')[1].strip().isdigit():
                score = int(line.split(': ')[1].strip())
                if 0 <= score <= 5:
                    scores.append(score)
            # Look for patterns like "1. 4" or "1) 4"
            elif ('. ' in line or ') ' in line) and line.split('. ' if '. ' in line else ') ')[1].strip().isdigit():
                score = int(line.split('. ' if '. ' in line else ') ')[1].strip())
                if 0 <= score <= 5:
                    scores.append(score)
        except (ValueError, IndexError):
            continue
    
    # If parsing failed, try a more flexible approach
    if not scores or len(scores) != len(criteria):
        scores = []
        # Just extract any digit between 0-5
        import re
        digits = re.findall(r'\b[0-5]\b', score_text)
        for digit in digits:
            if len(scores) < len(criteria):
                scores.append(int(digit))
    
    # If we still don't have enough scores, fill with zeros
    while len(scores) < len(criteria):
        scores.append(0)
    
    # If we have too many scores, truncate
    scores = scores[:len(criteria)]
    
    return scores
