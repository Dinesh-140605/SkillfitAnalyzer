# SkillFit Analyzer: AI-Powered Career Architect
## 10-Minute Technical Walkthrough Script

**Author:** Dinesh Kumar  
**Date:** December 2025  
**Topic:** End-to-End Explanation of the SkillFit Analyzer Project

---

## 1. Introduction (0:00 - 1:30)

"Hello everyone. Today, I am going to explain my project, **SkillFit Analyzer**.

**The Problem:**
In today's competitive job market, candidates often apply to hundreds of jobs but get rejected because their resumes don't match the specific keywords or requirements of the Job Description (JD). They don't know *why* they are being rejected.

**The Solution:**
I built **SkillFit Analyzer**, an intelligent AI application. It acts as a personal Career Coach. It takes your Resume and the Job Description, analyzes them using Google's advanced Gemini AI, and tells you **exactly** what you are missing. It gives you a match score, identifies skill gaps, and even lets you chat with an AI coach to fix those gaps."

---

## 2. High-Level Architecture (1:30 - 3:00)

"Let's look at how the system works technically. It follows a **Client-Server Architecture**.

1.  **The Frontend (Client):**
    *   Built using **Next.js 14** and **TypeScript**.
    *   It provides a modern, 'Dark Mode' User Interface.
    *   It handles the file upload (your PDF resume) and user inputs.

2.  **The Backend (Server):**
    *   Built using **Python** and **FastAPI**.
    *   This is where the logic lives. It receives the PDF, interacts with the AI, and sends back the results.

3.  **The Intelligence (AI Model):**
    *   I am using **Google Gemini Pro (via API)**.
    *   Instead of writing thousands of `if-else` statements to match keywords, I send the text to Gemini, which 'understands' the context (e.g., that 'React.js' is a frontend library)."

---

## 3. Workflow & Logic (3:00 - 6:00)

"Now, let's trace the journey of a single user request.

**Step 1: Resume Parsing**
*   When a user uploads a PDF, the backend receives it.
*   I use a Python library called `pypdf`. It opens the binary file and extracts raw text string from the PDF pages.

**Step 2: Constructing the Prompt**
*   The core magic happens in `analyzer.py`.
*   The system creates a **Prompt** for the AI. It looks like this:
    > 'Act as a Career Coach. Here is the Resume text: [INSERT TEXT]. Here is the JD: [INSERT TEXT]. Compare them and return a JSON object with score, gaps, and advice.'
*   This technique is called **Prompt Engineering**. We enforce a specific JSON structure so our frontend code doesn't break.

**Step 3: The AI Analysis**
*   We send this prompt to Google's API (`generativeai` library).
*   Gemini reads both texts. It doesn't just look for matching words; it understands *semantic Meaning*.
    *   *Example:* If the JD asks for 'Machine Learning' and the Resume says 'trained Neural Networks', a simple code might miss it, but Gemini knows they are related.

**Step 4: Data Processing**
*   The AI returns a JSON response.
*   The backend validates this response (checks if the score is 0-10, ensures the lists are valid).
*   It sends this clean data back to the frontend.

**Step 5: The Chatbot (Context Awareness)**
*   On the results page, there is a Chat Window.
*   When you ask 'How do I learn these skills?', we don't just send that question.
*   We send: *"User asked X. Context: User has a score of 6/10 and is missing Docker skills."*
*   This ensures the AI gives **personalized** advice, not generic Google search results."

---

## 4. Key Technologies Used (6:00 - 7:30)

"I chose this tech stack for performance and scalability:

*   **Next.js (React):** For Server-Side Rendering (SSR) and SEO. It makes the app load very fast.
*   **Tailwind CSS:** For the styling. I used 'Glassmorphism' (blur effects) to give it a premium, futuristic look.
*   **FastAPI (Python):** It is one of the fastest Python frameworks and creates automatic documentation (`/docs`).
*   **Google Gemini API:** Chosen because it's cost-effective and creates high-quality reasoning compared to local models."

---

## 5. Directory Structure Walkthrough (7:30 - 8:30)

"If you look at my code structure:

*   **`career-backend/app/main.py`**: This is the entry point. It defines the API routes like `/analyze` and `/chat`.
*   **`career-backend/app/analyzer.py`**: This is the most important file. It contains the `Analyzer` class that wraps the Google Gemini API key and handles the prompt logic.
*   **`new-career-frontend/src/app/results/page.tsx`**: This handles the complex dashboard logic, parsing the JSON response and rendering the charts."

---

## 6. Conclusion (8:30 - 10:00)

"In conclusion, **Career Compass** solves a real-world problem using cutting-edge Generative AI. 

*   It automates the job of a human career counselor.
*   It provides instant feedback (under 5 seconds).
*   It is interactive (through the Chatbot).

**Future Scope:**
*   I plan to add a 'Cover Letter Generator' that writes a letter based on the gaps found.
*   Integration with LinkedIn to auto-fetch profiles.

Thank you. Dealing with API integrations and Prompt Engineering taught me a lot about building modern AI applications."
