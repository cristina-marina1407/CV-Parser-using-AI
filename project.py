#!/usr/bin/env python3

# CV Analysis and Ranking System with Azure OpenAI integration
import os
import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import PyPDF2
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
from datetime import datetime
import sys
from config_positions import get_requirements_for_position, POSITION_REQUIREMENTS

load_dotenv()

# Load Azure OpenAI configuration from environment variables
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") 
subscription_key = os.getenv("AZURE_OPENAI_KEY")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2025-01-01-preview",
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data structure for company job requirements and scoring weights
@dataclass
class CompanyRequirements:
    keywords: List[str]
    education_levels: Dict[str, int]
    domain_skills: Dict[str, int]
    experience_weight: float = 0.3
    education_weight: float = 0.25
    skills_weight: float = 0.35
    keywords_weight: float = 0.1

# Data structure for candidate information extracted from CV
@dataclass
class CandidateProfile:
    name: str
    email: str
    education_level: str
    skills: List[str]
    experience_years: int
    keywords_found: List[str]
    raw_text: str
    score: float = 0.0
    rank: int = 0

class CVParser:
    
    def __init__(self):
        # Regex patterns for different education levels
        self.education_patterns = {
            'phd': r'(?i)(phd|doctor|doctorate)',
            'master': r'(?i)(master|msc|ma|masters)',
            'bachelor': r'(?i)(bachelor|bsc|ba|undergraduate)',
            'diploma': r'(?i)(diploma|degree)',
            'training': r'(?i)(certificate|certification|course|training)'
        }
        
        # Standard email regex pattern
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Extract raw text from PDF file using PyPDF2
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    # Use Azure OpenAI to analyze CV text and extract structured data
    def analyze_cv_with_ai(self, cv_text):
        # Simple prompt for name, email, score extraction
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an AI assistant that analyzes PDF CVs and extracts name, email and calculates score for ranking. Return a JSON with: name, email, score."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"CV: {cv_text}"
                    }
                ]
            }
        ]
        completion = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_tokens=400,
            temperature=0.3,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False
        )
        return completion.choices[0].message.content if hasattr(completion, 'choices') else completion.to_json()

    def main(self):
        cv_folder = Path("cv")
        if not cv_folder.exists():
            print(f"Folder {cv_folder} does not exist.")
            return
        results = []
        for pdf_file in cv_folder.glob("*.pdf"):
            print(f"Processing {pdf_file.name}...")
            text = self.extract_text_from_pdf(pdf_file)
            ai_result = self.analyze_cv_with_ai(text)
            try:
                data = json.loads(ai_result)
                results.append({
                    "name": data.get("name", ""),
                    "email": data.get("email", ""),
                    "score": data.get("score", 0),
                    "file": pdf_file.name
                })
            except Exception as e:
                print(f"Error parsing AI response for {pdf_file.name}: {e}")
                print(ai_result)
        results.sort(key=lambda x: x["score"], reverse=True)
        print("\nCV ranking by score:")
        for idx, r in enumerate(results, 1):
            print(f"{idx}. {r['name']} ({r['email']}) - score: {r['score']} [{r['file']}]")

    
    # Detailed CV parsing with job requirements matching
    def parse_cv_with_ai(self, text: str, requirements: CompanyRequirements) -> Dict:
        
        skills_list = ", ".join(requirements.domain_skills.keys())
        keywords_list = ", ".join(requirements.keywords)
        
        prompt = f"""
        Please analyze the following CV text and extract the following information in JSON format:
        
        1. candidate_name: The full name of the candidate (not university or company names)
        2. email: Email address
        3. education_level: Highest education level (phd, master, bachelor, diploma, training, or unknown)
        4. skills: List of technical skills found from this list: {skills_list}
        5. experience_years: Number of years of work experience (integer, 0 if not found)
        6. keywords_found: List of keywords found from: {keywords_list}
        
        Important guidelines:
        - For candidate_name: Extract only personal names, not university names, company names, or job titles
        - For education_level: Return the highest level found
        - For experience_years: Look for patterns like "X years experience", "X+ years", etc.
        - Return only the JSON object, no additional text
        
        CV Text:
        {text[:4000]}
        """
        
        try:
            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": "You are a professional CV parser. Extract information accurately and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result = json.loads(result_text[json_start:json_end])
                    return result
                else:
                    raise Exception("Could not parse JSON response")
                    
        except Exception as e:
            logger.error(f"Error with OpenAI API: {e}")
            return self.fallback_extraction(text, requirements)
    
    # Regex-based extraction when AI fails or is unavailable
    def fallback_extraction(self, text: str, requirements: CompanyRequirements) -> Dict:
        return {
            "candidate_name": self.extract_name_basic(text),
            "email": self.extract_email_basic(text),
            "education_level": self.extract_education_level_basic(text),
            "skills": self.extract_skills_basic(text, requirements.domain_skills),
            "experience_years": self.extract_experience_years_basic(text),
            "keywords_found": self.find_keywords_basic(text, requirements.keywords)
        }
        
    # Extract candidate name using pattern matching and exclusion lists
    def extract_name_basic(self, text: str) -> str:
        lines = text.split('\n')
        name_pattern = r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]*\.?){1,3}$'
        exclude_words = {
            'university', 'college', 'institute', 'school', 'department', 
            'engineering', 'science', 'technology', 'boston', 'carnegie',
            'mellon', 'national', 'politehnica', 'bucharest', 'sample',
            'undergraduate', 'graduate', 'resumes', 'current', 'address'
        }
        
        # Check first 15 lines for name patterns
        for line in lines[:15]:
            line = line.strip()
            if not line or len(line) < 3 or len(line) > 60:
                continue
            if re.search(r'[\d@()+-]|www\.|http|email|phone|address', line.lower()):
                continue
                
            if re.match(name_pattern, line):
                line_lower = line.lower()
                if not any(word in line_lower for word in exclude_words):
                    return re.sub(r'\s+', ' ', line)
        
        return "Unknown name"
    
    # Find valid email addresses, filtering out generic examples
    def extract_email_basic(self, text: str) -> str:
        emails = re.findall(self.email_pattern, text)
        if emails:
            # Filter out generic/example emails
            generic_patterns = [r'sample', r'example', r'test', r'xxxx', r'first\.last']
            for email in emails:
                if not any(re.search(pattern, email.lower()) for pattern in generic_patterns):
                    return email
            return emails[0]
        return ""
    
    def extract_education_level_basic(self, text: str) -> str:
        text_lower = text.lower()
        for level, pattern in self.education_patterns.items():
            if re.search(pattern, text_lower):
                return level
        return "unknown"
    
    def extract_skills_basic(self, text: str, domain_skills: Dict[str, int]) -> List[str]:
        found_skills = []
        text_lower = text.lower()
        for skill in domain_skills.keys():
            if skill.lower() in text_lower:
                found_skills.append(skill)
        return found_skills
    
    def extract_experience_years_basic(self, text: str) -> int:
        experience_patterns = [
            r'(\d+)\s*years?\s*(of\s*)?experience',
            r'experience\s*[:\-]?\s*(\d+)\s*years?',
            r'(\d+)\+?\s*years?\s*in',
            r'(\d+)\s*years?\s*working',
            r'over\s*(\d+)\s*years?'
        ]
        
        text_lower = text.lower()
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                years = [int(match[0]) if isinstance(match, tuple) else int(match) 
                        for match in matches]
                return max(years)
        return 0
    
    def find_keywords_basic(self, text: str, keywords: List[str]) -> List[str]:
        found_keywords = []
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        return found_keywords

    def parse_cv(self, pdf_path: str, requirements: CompanyRequirements) -> Optional[CandidateProfile]:
        try:
            text = self.extract_text_from_pdf(pdf_path)
            if not text.strip():
                logger.warning(f"Could not extract text from {pdf_path}")
                return None
            
            if not subscription_key or not endpoint or subscription_key == "your_azure_openai_key_here":
                logger.warning("No valid Azure OpenAI configuration found, using fallback extraction")
                extracted_data = self.fallback_extraction(text, requirements)
            else:
                extracted_data = self.parse_cv_with_ai(text, requirements)
            
            profile = CandidateProfile(
                name=extracted_data.get("candidate_name", "Unknown name"),
                email=extracted_data.get("email", ""),
                education_level=extracted_data.get("education_level", "unknown"),
                skills=extracted_data.get("skills", []),
                experience_years=extracted_data.get("experience_years", 0),
                keywords_found=extracted_data.get("keywords_found", []),
                raw_text=text
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error parsing CV {pdf_path}: {e}")
            return None

# Handles scoring calculations for candidates based on company requirements
class CandidateScorer:
    
    def __init__(self, requirements: CompanyRequirements):
        self.requirements = requirements
    
    def calculate_education_score(self, education_level: str) -> float:
        return self.requirements.education_levels.get(education_level, 0)
    
    def calculate_skills_score(self, skills: List[str]) -> float:
        total_score = 0
        for skill in skills:
            total_score += self.requirements.domain_skills.get(skill, 0)
        return total_score
    
    def calculate_experience_score(self, experience_years: int) -> float:
        return min(experience_years * 10, 100)
    
    def calculate_keywords_score(self, keywords_found: List[str]) -> float:
        return len(keywords_found) * 20
    
    def calculate_total_score(self, profile: CandidateProfile) -> float:
        education_score = self.calculate_education_score(profile.education_level)
        skills_score = self.calculate_skills_score(profile.skills)
        experience_score = self.calculate_experience_score(profile.experience_years)
        keywords_score = self.calculate_keywords_score(profile.keywords_found)
        
        # Weighted combination of all scoring components
        total_score = (
            education_score * self.requirements.education_weight +
            skills_score * self.requirements.skills_weight +
            experience_score * self.requirements.experience_weight +
            keywords_score * self.requirements.keywords_weight
        )
        
        return round(total_score, 2)

class CVAnalysisSystem:
    
    def __init__(self, requirements: CompanyRequirements):
        self.requirements = requirements
        self.parser = CVParser()
        self.scorer = CandidateScorer(requirements)
        self.candidates: List[CandidateProfile] = []
    
    def process_cv_folder(self, folder_path: str) -> List[CandidateProfile]:
        folder = Path(folder_path)
        pdf_files = list(folder.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {folder_path}")
            return []
        
        logger.info(f"Processing {len(pdf_files)} CVs...")
        
        for pdf_file in pdf_files:
            logger.info(f"Processing: {pdf_file.name}")
            profile = self.parser.parse_cv(str(pdf_file), self.requirements)
            
            if profile:
                profile.score = self.scorer.calculate_total_score(profile)
                self.candidates.append(profile)
                logger.info(f"Candidate processed: {profile.name} - Score: {profile.score}")
        
        return self.candidates
    
    def rank_candidates(self) -> List[CandidateProfile]:
        sorted_candidates = sorted(self.candidates, key=lambda x: x.score, reverse=True)
        
        for i, candidate in enumerate(sorted_candidates, 1):
            candidate.rank = i
        
        return sorted_candidates
    
    def get_top_percentage(self, percentage: float = 0.5) -> List[CandidateProfile]:
        ranked = self.rank_candidates()
        top_count = max(1, int(len(ranked) * percentage))
        return ranked[:top_count]

def create_sample_requirements() -> CompanyRequirements:
    return CompanyRequirements(
        keywords=["Python", "Machine Learning", "AI", "Data Science", "Azure", "Cloud"],
        education_levels={
            "phd": 100,
            "master": 80,
            "bachelor": 60,
            "diploma": 40,
            "training": 20,
            "unknown": 0
        },
        domain_skills={
            "Python": 30,
            "Machine Learning": 35,
            "Deep Learning": 35,
            "TensorFlow": 25,
            "PyTorch": 25,
            "Pandas": 20,
            "NumPy": 20,
            "Scikit-learn": 25,
            "Azure": 30,
            "AWS": 25,
            "Docker": 20,
            "Kubernetes": 25,
            "SQL": 20,
            "NoSQL": 15,
            "Git": 15,
            "Linux": 15
        }
    )

def main():
    print("CV Analysis and Ranking System with Azure AI")
    print("=" * 50)
    
    api_key = os.getenv('AZURE_OPENAI_KEY')
    api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
    
    if not api_key or not api_base or api_key == "your_azure_openai_key_here":
        print("WARNING: No Azure OpenAI configuration found!")
        print("   Using fallback extraction methods.")
        print("   For better results, configure Azure OpenAI in .env file:")
        print("   AZURE_OPENAI_KEY=your-azure-key")
        print("   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
        print("   AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name")
        print("-" * 50)
    else:
        print("Azure OpenAI configured - using AI-powered extraction")
        print(f"   Endpoint: {api_base}")
        print("-" * 50)
    
    print("Available positions:")
    for pos in POSITION_REQUIREMENTS.keys():
        print(f"- {pos}")
    position = input("Enter position to filter candidates (e.g. data_scientist): ").strip().lower()
    try:
        requirements = get_requirements_for_position(position)
    except Exception as e:
        print(f"Invalid position: {e}")
        sys.exit(1)
    
    cv_system = CVAnalysisSystem(requirements)
    
    cv_folder = input("Enter path to CV PDF folder: ").strip()
    
    if not os.path.exists(cv_folder):
        logger.error(f"Folder {cv_folder} does not exist!")
        return
    
    print("Starting CV processing...")
    candidates = cv_system.process_cv_folder(cv_folder)
    
    if not candidates:
        logger.error("No valid candidates found!")
        return
    
    ranked_candidates = cv_system.rank_candidates()
    
    print(f"\nCandidate Ranking ({len(ranked_candidates)} total):")
    print("-" * 70)
    for candidate in ranked_candidates:
        print(f"{candidate.rank:2d}. {candidate.name:30s} | Email: {candidate.email:30s} | Score: {candidate.score:6.2f}")
    
    output_filename = f"Candidates Ranking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("CANDIDATE RANKING\n")
        f.write("=" * 50 + "\n")
        f.write(f"Processing date: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Total candidates: {len(ranked_candidates)}\n\n")
        
        for candidate in ranked_candidates:
            f.write(f"{candidate.rank:2d}. {candidate.name}\n")
            f.write(f"    Email: {candidate.email}\n")
            f.write(f"    Score: {candidate.score:6.2f}\n")
            f.write(f"    Education: {candidate.education_level}\n")
            f.write(f"    Experience: {candidate.experience_years} years\n")
            f.write(f"    Skills: {', '.join(candidate.skills) if candidate.skills else 'N/A'}\n")
            f.write(f"    Keywords: {', '.join(candidate.keywords_found) if candidate.keywords_found else 'N/A'}\n")
            f.write("-" * 50 + "\n")
    
    print(f"\nProcessing complete!")
    print(f"Results saved to: {output_filename}")

if __name__ == "__main__":
    main()
