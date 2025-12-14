# SkillFit Analyzer - Complete Project Guide

**Author:** AI Assistant  
**Date:** December 2025  
**Version:** 2.0 (Gemini Edition)

---

## 1. Project Overview

**SkillFit Analyzer** is an intelligent web application helping job seekers optimize their resumes. It uses **Artificial Intelligence (Google Gemini)** to compare a user's resume against a specific job description (JD).

### **What it does:**
1.  **Scans Resume:** Reads your uploaded PDF resume.
2.  **Analyzes Match:** Compares your skills/experience with the Job Description.
3.  **Identifies Gaps:** Tells you exactly what skills you are missing.
4.  ** AI Chat Coach:** Lets you chat with an AI bot that "knows" your resume and gives personalized career advice.

---

## 2. Technologies Used (The "Ingredients")

### **Frontend (The Website)**
*   **Next.js 14:** The framework used to build the website (User Interface).
*   **TypeScript:** A stricter version of JavaScript for better coding safety.
*   **Tailwind CSS:** Used for styling (Colors, Spacing, Dark Mode).
*   **Axios:** A library to send data (Resume/JD) to the backend server.

### **Backend (The Brain)**
*   **Python:** The programming language handling logic.
*   **FastAPI:** A super-fast web framework for Python to create the API.
*   **Google Gemini API:** The "Brain" that reads and understands the text.
*   **PyPDF:** A tool to extract text from PDF files.

---

## 3. Important Setup Details

### **Software Required**
1.  **VS Code:** The code editor.
2.  **Node.js (v18+):** Required to run the Frontend website.
3.  **Python (v3.10+):** Required to run the Backend server.

### **API Keys Required**
You strictly need **ONE** API key for this project:
*   **Key Name:** `GOOGLE_API_KEY`
*   **Provider:** Google (Gemini)
*   **Cost:** Free (for standard tier usage)
*   **Where to get it:** [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
*   **Setup:** You paste this key inside the `.env` file in the backend folder.

---

## 4. How It Works (Step-by-Step Flow)

### **Phase 1: The Input**
1.  User opens the website (`localhost:3005`).
2.  User uploads `Resume.pdf` and pastes a "Job Description".
3.  Frontend sends this data to the Backend API endpoint: `http://127.0.0.1:8000/analysis/full-analyze`

### **Phase 2: The Logic (Backend)**
1.  **PDF Parsing:** The server uses `pypdf` to convert the PDF file into plain text.
2.  **Prompt Engineering:** The server creates a special instruction for the AI:
    > "You are a Career Coach. Compare this RESUME [text] with this JD [text] and give me a JSON score."
3.  **AI Analysis:** It sends this huge text prompt to **Google Gemini (gemini-pro)**.
4.  **Structured Response:** Gemini replies with specific data:
    *   Score: 7.5/10
    *   Missing Skills: ["Docker", "Kubernetes"]
    *   Advice: "Add a project about Cloud Deployment."

### **Phase 3: The Result**
1.  The Frontend receives this JSON data.
2.  It displays a **Dashboard**:
    *   A circular gauge shows the score.
    *   Red tags show "Missing Skills".
    *   Green tags show "Matched Skills".
3.  **Chat:** If you ask the Chatbot "How do I learn Docker?", it sends your question + your resume context back to Gemini to get a personalized answer.

---

## 5. Folder Structure Explained

```text
Delta/
├── career-backend/                 # (The Server)
│   ├── .env                        # [SECRET] Stores GOOGLE_API_KEY
│   ├── requirements.txt            # List of Python libraries needed
│   ├── app/
│   │   ├── main.py                 # The entry point (API Routes)
│   │   └── analyzer.py             # The logic that talks to Gemini
│
└── new-career-frontend/            # (The Website)
    ├── src/app/
    │   ├── page.tsx                # Landing Page (Upload form)
    │   ├── results/page.tsx        # Dashboard Page (Charts & Graphs)
    │   └── globals.css             # Styling (Dark Theme)
    ├── package.json                # List of JavaScript libraries
    └── next.config.ts              # Settings
```

---

## 6. How to Run This Project (Cheatsheet)

### **Step 1: Start Backend**
1.  Open Terminal.
2.  Go to folder: `cd career-backend`
3.  Activate Virtual Env (Optional but recommended).
4.  Run Server: `python -m uvicorn app.main:app --reload --port 8000`

### **Step 2: Start Frontend**
1.  Open a **New** Terminal.
2.  Go to folder: `cd new-career-frontend`
3.  Run Website: `npm run dev` (or `npx next dev -p 3005`)

### **Step 3: Use it**
Open your browser to `http://localhost:3005`

---

## 7. How to Print this as PDF
1.  In VS Code, press `Ctrl + Shift + V` to verify the preview.
2.  Right Click anywhere on the preview -> Select **Print**.
3.  Select Destination: **"Save as PDF"**.
