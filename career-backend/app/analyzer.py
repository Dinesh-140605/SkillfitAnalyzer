"""
analyzer.py

Gemini-powered Analyzer for Career Compass.
Replaces local sentence-transformers with Google's Generative AI.

Dependencies:
  pip install google-generativeai python-dotenv
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from a .env file if present
load_dotenv()

class Analyzer:
    def __init__(self):
        # API Key management
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("WARNING: GOOGLE_API_KEY not found in environment variables.")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        else:
            self.model = None

    def analyze(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Analyzes the resume against the JD using Gemini API.
        Returns a structured JSON response matching the frontend expectations.
        """
        if not self.model:
             return {
                "overall_score": 0,
                "skills_found": [],
                "required_skills": ["GOOGLE_API_KEY_MISSING"],
                "matched": [],
                "gaps": ["Please set GOOGLE_API_KEY in backend .env file"],
                "relevant_projects": [],
                "recommended_jobs": [],
                "resume_suggestions": ["Backend configuration error: API Key missing."]
            }

        prompt = f"""
        You are an expert AI Career Coach and Resume Analyzer.
        Your task is to analyze a Candidate's Resume against a Job Description (JD).

        RESUME TEXT:
        {resume_text[:20000]} 

        JOB DESCRIPTION:
        {jd_text[:10000]}

        ---------------------------------------------------
        OUTPUT INSTRUCTIONS:
        Analyze the match and return a strictly valid JSON object with the following fields.
        
        CRITICAL SCORING RULES:
        - "overall_score": Must be a number between 0 and 10. (e.g., 7.5, 8.2). DO NOT return a score out of 100.
        
        Fields:
        1. "overall_score": (number 0-10) 
        2. "skills_found": (list of strings) extracted from resume.
        3. "required_skills": (list of strings) extracted from JD.
        4. "matched": (list of strings) skills present in both.
        5. "gaps": (list of strings) important skills in JD but missing in Resume.
        6. "relevant_projects": (list of objects) relevant projects from resume. format: {{"snippet": "Project Name/Desc", "score": 0-10}}. limit to top 3.
        7. "recommended_jobs": (list of objects) suggested roles based on resume skills. format: {{"role": "Role Title", "score": 0-100}}. limit to top 5.
        8. "resume_suggestions": (list of strings) actionable advice to improve the resume for this specific JD. limit to 5.

        Do not generate markdown formatting (like ```json), just the raw JSON string.
        """

        try:
            response = self.model.generate_content(prompt)
            text_response = response.text.replace("```json", "").replace("```", "").strip()
            
            # Attempt to parse JSON
            data = json.loads(text_response)
            
            # Ensure critical keys exist to prevent frontend crash
            defaults = {
                "overall_score": 50,
                "skills_found": [],
                "required_skills": [],
                "matched": [],
                "gaps": [],
                "relevant_projects": [],
                "recommended_jobs": [],
                "resume_suggestions": ["Could not parse specific insights."]
            }
            
            for k, v in defaults.items():
                if k not in data:
                    data[k] = v
            
            return data

        except Exception as e:
            print(f"Gemini Analysis Failed: {e}")
            return {
                "overall_score": 0,
                "skills_found": [],
                "required_skills": [],
                "matched": [],
                "gaps": ["Analysis Error"],
                "relevant_projects": [],
                "recommended_jobs": [],
                "resume_suggestions": [f"Error during AI analysis: {str(e)}"]
            }

    def chat_coach(self, user_message: str, context:  Dict[str, Any]) -> str:
        """
        Chat with the AI Career Coach using resume context.
        """
        if not self.model:
            return "AI Coach is currently unavailable (API Key missing)."

        # Context summary
        summary = f"""
        Candidate Context:
        - Overall Score: {context.get('overall_score', 'N/A')}/10
        - Top Skills: {', '.join(context.get('skills_found', [])[:10])}
        - Missing Skills (Gaps): {', '.join(context.get('gaps', [])[:10])}
        - Recommended Roles: {', '.join([r.get('role', '') for r in context.get('recommended_jobs', [])[:3]])}
        """

        prompt = f"""
        You are a friendly and encouraging AI Career Coach. 
        You are chatting with a candidate who has just analyzed their resume.
        
        {summary}

        User Question: "{user_message}"

        Instructions:
        - Answer the user's question directly and concisely (max 3 sentences).
        - Use the provided context to give specific advice (e.g., mention specific gaps or skills).
        - If asked about "Data Science", "Marketing", etc., use your general knowledge to suggest skills, but link it back to their profile gaps if possible.
        - Be motivational.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"I'm having trouble connecting right now. ({str(e)})"

if __name__ == "__main__":
    # Test script
    an = Analyzer()
    print("Analyzer Initialized. Key present:", bool(an.api_key))
