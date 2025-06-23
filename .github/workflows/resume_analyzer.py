#!/usr/bin/env python3
import argparse
import fitz  # PyMuPDF
from collections import defaultdict
import os
import json
from typing import Dict, List, DefaultDict

# Constants
SKILLS_DB_FILE = "skills_db.json"
DEFAULT_SKILLS = {
    "Programming": ["Python", "Java", "C++", "JavaScript", "SQL", "R", "Go"],
    "Data": ["SQL", "NoSQL", "Spark", "Pandas", "Tableau", "PowerBI", "Excel"],
    "ML/AI": ["Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP"],
    "DevOps": ["Docker", "Kubernetes", "AWS", "Azure", "CI/CD", "Terraform"],
    "Soft Skills": ["Leadership", "Communication", "Teamwork", "Problem Solving"]
}

class ResumeAnalyzer:
    def __init__(self, skills_db: Dict[str, List[str]] = None):
        self.skills_db = skills_db if skills_db else self.load_skills_db()

    @staticmethod
    def load_skills_db() -> Dict[str, List[str]]:
        """Load skills database from JSON file or use defaults"""
        if os.path.exists(SKILLS_DB_FILE):
            with open(SKILLS_DB_FILE, 'r') as f:
                return json.load(f)
        return DEFAULT_SKILLS

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")
        
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text.lower()

    def analyze_skills(self, text: str) -> DefaultDict[str, int]:
        """Count skill mentions in the resume text"""
        skill_counts = defaultdict(int)
        for category, skills in self.skills_db.items():
            for skill in skills:
                if skill.lower() in text:
                    skill_counts[skill] += 1
        return skill_counts

    def suggest_improvements(self, skill_counts: DefaultDict[str, int]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        for category, skills in self.skills_db.items():
            found_skills = [s for s in skills if s in skill_counts]
            if not found_skills:
                suggestions.append(
                    f"⚠️ Missing {category} skills. Consider adding: {', '.join(skills[:3])}..."
                )
            elif len(found_skills) < 2:
                suggestions.append(
                    f"ℹ️ Few {category} skills. Could add: {', '.join([s for s in skills if s not in found_skills][:2])}"
                )
        return suggestions

    def generate_report(self, skill_counts: DefaultDict[str, int], suggestions: List[str]) -> str:
        """Generate formatted analysis report"""
        report = ["\n=== SKILL ANALYSIS ==="]
        
        if not skill_counts:
            report.append("No skills detected from the database")
        else:
            for skill, count in sorted(skill_counts.items(), key=lambda x: (-x[1], x[0])):
                report.append(f"• {skill}: {count} mention{'s' if count > 1 else ''}")

        if suggestions:
            report.append("\n=== SUGGESTIONS ===")
            report.extend(suggestions)
        else:
            report.append("\n✅ Good job! Your resume covers diverse skill categories.")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(
        description="Resume Analyzer CLI - Get skill insights and improvement suggestions",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("resume", help="Path to the PDF resume file")
    parser.add_argument("--skills", help="Custom JSON skills database file", default=None)
    args = parser.parse_args()

    try:
        analyzer = ResumeAnalyzer(
            json.load(open(args.skills)) if args.skills else ResumeAnalyzer()
        
        text = analyzer.extract_text(args.resume)
        skill_counts = analyzer.analyze_skills(text)
        
        print(f"\n📄 Analyzing: {os.path.basename(args.resume)}")
        print(analyzer.generate_report(skill_counts, analyzer.suggest_improvements(skill_counts)))

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
