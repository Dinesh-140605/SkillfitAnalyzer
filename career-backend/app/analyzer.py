"""
analyzer.py

Improved Analyzer class for Career Compass.
Place this file alongside your existing backend Python package (same folder as main.py).

Dependencies:
  pip install sentence-transformers torch numpy

This file is executable as a small CLI for quick testing:
  python analyzer.py

It expects two JSON files in the same directory:
  - skills.json  (array of skill strings)
  - roles.json   (array of objects: { "role": "role-key", "desc": "description" })

The class provides:
  - extract_skills(text)
  - extract_projects(text)
  - project_relevance(jd_text, projects)
  - recommend_roles(resume_text, jd_text)
  - resume_suggestions(resume_text, jd_text)
  - analyze(resume_text, jd_text)

Author: assistant (refactor for readability, types, error handling)
"""

from __future__ import annotations

import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple

# Lazy import of sentence_transformers to provide helpful error if missing
try:
    from sentence_transformers import SentenceTransformer, util
except Exception as e:
    SentenceTransformer = None  # type: ignore
    util = None  # type: ignore


class Analyzer:
    """Analyzer wraps an embedding model + heuristics to compare resume vs JD.

    - Uses sentence-transformers (all-MiniLM-L6-v2 by default)
    - Loads skills.json (list[str]) and roles.json (list[{'role', 'desc'}]) from the same folder
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", assets_dir: Optional[str] = None):
        if SentenceTransformer is None or util is None:
            raise ImportError(
                "Missing dependency: install sentence-transformers and its backend (torch).\n"
                "pip install sentence-transformers torch numpy"
            )

        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)

        # Determine assets directory (defaults to this file's directory)
        base_dir = assets_dir or os.path.dirname(__file__)
        self.skills_path = os.path.join(base_dir, "skills.json")
        self.roles_path = os.path.join(base_dir, "roles.json")

        self.skills = self._load_skills(self.skills_path)
        self.roles = self._load_roles(self.roles_path)

        # Precompute role embeddings (use description text)
        self.role_embeddings = {}
        for r in self.roles:
            desc = r.get("desc") or r.get("description") or r.get("role", "")
            try:
                emb = self.model.encode(desc, convert_to_tensor=True)
            except Exception:
                # fallback: encode empty or raw role name
                emb = self.model.encode(r.get("role", ""), convert_to_tensor=True)
            self.role_embeddings[r.get("role")] = emb

    # ------------------------ Utilities ------------------------
    def _load_skills(self, path: str) -> List[str]:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return [s.lower().strip() for s in data if isinstance(s, str)]
            except Exception:
                return []

    def _load_roles(self, path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # normalize each role to contain 'role' and 'desc'
                out = []
                for r in data:
                    if isinstance(r, dict):
                        key = r.get("role") or r.get("key") or r.get("title")
                        desc = r.get("desc") or r.get("description") or r.get("desc_text") or ""
                        out.append({"role": key, "desc": desc})
                return out
            except Exception:
                return []

    # ------------------------ Skill extraction ------------------------
    def extract_skills(self, text: str) -> List[str]:
        if not text:
            return []
        txt = text.lower()
        found = []
        # simple substring match for now (fast and explainable)
        for s in self.skills:
            if not s:
                continue
            # match whole words for multi-word skills as well
            pattern = r"\\b" + re.escape(s) + r"\\b"
            if re.search(pattern, txt):
                found.append(s)
        # dedupe while keeping order
        seen = set()
        out = []
        for s in found:
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out

    # ------------------------ Project extraction ------------------------
    def extract_projects(self, text: str) -> List[Dict[str, str]]:
        """Attempt to extract project-like blocks from a resume text.

        Strategy:
        1. Look for a block starting with a header containing 'project' (case-insensitive)
        2. Collect following non-empty lines until another header like EXPERIENCE or EDUCATION
        3. If none found, fallback to scanning lines that contain project-like keywords
        """
        if not text:
            return []

        lines = [ln.rstrip() for ln in text.splitlines()]
        projects: List[Dict[str, str]] = []

        # Normalize headers
        header_regex = re.compile(r"^(?P<h>[A-Z\s]{3,})$")
        project_section_indexes: List[int] = []

        # locate project section lines (rough heuristic)
        for i, ln in enumerate(lines):
            up = ln.strip().upper()
            if "PROJECT" in up and len(up) <= 40:
                project_section_indexes.append(i)

        if project_section_indexes:
            for start in project_section_indexes:
                # capture until next all-caps header or blank line cluster
                j = start + 1
                buffer: List[str] = []
                while j < len(lines):
                    L = lines[j].strip()
                    if not L:
                        # allow a single blank, but stop on >1 blank or a clear section header
                        if len(buffer) and (j + 1 < len(lines) and not lines[j + 1].strip()):
                            break
                        buffer.append("")
                        j += 1
                        continue

                    # stop if uppercase header that looks like new section (EXPERIENCE, EDUCATION, SKILLS)
                    if re.match(r"^[A-Z][A-Z\s0-9]{2,}$", L) and any(h in L for h in ["EXPERIENCE", "EDUCATION", "SKILLS", "CERTIFICATION"]):
                        break

                    buffer.append(L)
                    j += 1

                joined = "\n".join([b for b in buffer if b.strip()])
                if len(joined) > 20:
                    # split by bullet markers if multiple projects
                    chunks = re.split(r"\n(?=[\-\u2022\*])", joined)
                    for c in chunks:
                        txt = c.strip(" \n\r-\u2022*\t")
                        if len(txt) > 10:
                            projects.append({"text": txt})

        # Fallback heuristic: lines with verbs like 'developed', 'built', 'implemented'
        if not projects:
            project_keywords = ["developed", "built", "implemented", "designed", "created", "worked on"]
            buffer: List[str] = []
            for ln in lines:
                lower = ln.lower()
                if any(k in lower for k in project_keywords):
                    # if buffer had content, push it as a project and reset
                    if buffer:
                        combined = " ".join(buffer).strip()
                        if len(combined) > 12:
                            projects.append({"text": combined})
                        buffer = []
                    buffer.append(ln.strip())
                elif buffer:
                    # keep accumulating until a short line or blank
                    if ln.strip() == "":
                        combined = " ".join(buffer).strip()
                        if len(combined) > 12:
                            projects.append({"text": combined})
                        buffer = []
                    else:
                        buffer.append(ln.strip())

            if buffer:
                combined = " ".join(buffer).strip()
                if len(combined) > 12:
                    projects.append({"text": combined})

        # final cleanup & dedupe
        seen = set()
        out: List[Dict[str, str]] = []
        for p in projects:
            t = re.sub(r"\s+", " ", p.get("text", "")).strip()
            if not t:
                continue
            if t in seen:
                continue
            seen.add(t)
            out.append({"text": t})

        return out

    # ------------------------ Project relevance scoring ------------------------
    def project_relevance(self, jd_text: str, projects: List[Dict[str, str]], top_k: int = 3) -> List[Dict[str, Any]]:
        if not projects:
            return []

        jd_emb = self.model.encode(jd_text, convert_to_tensor=True)
        out = []
        for p in projects:
            txt = p.get("text", "")
            p_emb = self.model.encode(txt, convert_to_tensor=True)
            sim = util.cos_sim(jd_emb, p_emb).item()
            # convert cosine (-1..1) to 0..10 scale
            score10 = round(((sim + 1) / 2) * 10, 2)

            # extract a short snippet/title
            title = txt.split("\n")[0].strip()
            title = re.sub(r"^[\-\u2022\*\s]+", "", title)

            out.append({"snippet": f"{title} matched score : {round(score10, 2)}/10", "score": score10})

        out.sort(key=lambda x: x["score"], reverse=True)
        # present clean snippet with integer-like formatting when possible
        for e in out:
            sc = e["score"]
            if float(sc).is_integer():
                e["snippet"] = e["snippet"].replace(f": {round(sc,2)}/10", f": {int(sc)}/10")
            else:
                e["snippet"] = e["snippet"].replace(f": {round(sc,2)}/10", f": {round(sc,1)}/10")

        return out[:top_k]

    # ------------------------ Role recommendation ------------------------
    def recommend_roles(self, resume_text: str, jd_text: str, top_k: int = 8) -> List[Dict[str, Any]]:
        combined = (resume_text or "") + "\n" + (jd_text or "")
        combined_emb = self.model.encode(combined, convert_to_tensor=True)

        scores: List[Dict[str, Any]] = []
        for role in self.roles:
            key = role.get("role")
            emb = self.role_embeddings.get(key)
            if emb is None:
                continue
            sim = util.cos_sim(combined_emb, emb).item()
            score_pct = round(((sim + 1) / 2) * 100, 2)
            scores.append({"role": key, "score": score_pct})

        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_k]

    # ------------------------ Resume suggestions ------------------------
    def resume_suggestions(self, resume_text: str, jd_text: str) -> List[str]:
        suggestions: List[str] = []
        resume_sk = set(self.extract_skills(resume_text))
        jd_sk = set(self.extract_skills(jd_text))

        missing = list(jd_sk - resume_sk)
        if missing:
            suggestions.append("Add these missing skills to improve your match: " + ", ".join(missing[:12]))

        if "summary" not in (resume_text or "").lower():
            suggestions.append("Add a short 2–3 line Summary section at the top of your resume.")

        # check numeric achievements (simple heuristic)
        if not re.search(r"\b\d{1,3}%|\b\d{1,5}\b", resume_text or ""):
            suggestions.append("Add measurable achievements (e.g., 'Improved accuracy by 20%' or 'Reduced cost by 15%').")

        # keep suggestions unique and reasonable
        seen = set()
        out: List[str] = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out

    # ------------------------ Main analyze ------------------------
    def analyze(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        resume_text = resume_text or ""
        jd_text = jd_text or ""

        resume_skills = self.extract_skills(resume_text)
        jd_skills = self.extract_skills(jd_text)

        matched = [s for s in jd_skills if s in resume_skills]
        gaps = [s for s in jd_skills if s not in resume_skills]

        # similarity
        jd_emb = self.model.encode(jd_text, convert_to_tensor=True)
        resume_emb = self.model.encode(resume_text, convert_to_tensor=True)
        sim = util.cos_sim(jd_emb, resume_emb).item()
        score10 = round(((sim + 1) / 2) * 10, 2)

        projects = self.extract_projects(resume_text)
        relevant_projects = self.project_relevance(jd_text, projects)

        recommended_jobs = self.recommend_roles(resume_text, jd_text)
        suggestions = self.resume_suggestions(resume_text, jd_text)

        return {
            "overall_score": score10,
            "skills_found": resume_skills,
            "required_skills": jd_skills,
            "matched": matched,
            "gaps": gaps,
            "relevant_projects": relevant_projects,
            "suggested_projects": [],
            "recommended_jobs": recommended_jobs,
            "resume_suggestions": suggestions,
        }


# ------------------------ Quick CLI for local testing ------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Analyzer quick test")
    parser.add_argument("--resume", help="Path to a resume text file (txt or pdf parsed externally)")
    parser.add_argument("--jd", help="Path to a job description text file")
    args = parser.parse_args()

    def _read_file(path: Optional[str]) -> str:
        if not path:
            return ""
        if not os.path.exists(path):
            print(f"Warning: file not found: {path}")
            return ""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    resume_text = _read_file(args.resume)
    jd_text = _read_file(args.jd)

    a = Analyzer()
    out = a.analyze(resume_text, jd_text)
    print(json.dumps(out, indent=2, ensure_ascii=False))
