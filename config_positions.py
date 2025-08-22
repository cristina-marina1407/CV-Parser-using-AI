#!/usr/bin/env python3

from project import CompanyRequirements

def data_scientist_requirements() -> CompanyRequirements:
    return CompanyRequirements(
        keywords=[
            "Python", "R", "Machine Learning", "Deep Learning", "AI", 
            "Data Science", "Statistics", "Analytics", "Big Data"
        ],
        education_levels={
            "phd": 100,
            "master": 85,
            "bachelor": 65,
            "diploma": 40,
            "training": 25,
            "unknown": 0
        },
        domain_skills={
            "Python": 35,
            "R": 30,
            "Machine Learning": 40,
            "Deep Learning": 35,
            "TensorFlow": 30,
            "PyTorch": 30,
            "Keras": 25,
            "Pandas": 25,
            "NumPy": 25,
            "Scikit-learn": 30,
            "Matplotlib": 20,
            "Seaborn": 20,
            "Jupyter": 15,
            "SQL": 25,
            "NoSQL": 20,
            "Hadoop": 25,
            "Spark": 30,
            "Tableau": 20,
            "Power BI": 20,
            "Statistics": 30,
            "Mathematics": 25
        },
        experience_weight=0.35,
        education_weight=0.30,
        skills_weight=0.25,
        keywords_weight=0.10
    )

def software_developer_requirements() -> CompanyRequirements:
    return CompanyRequirements(
        keywords=[
            "Programming", "Software Development", "Coding", "Algorithm",
            "Full Stack", "Backend", "Frontend", "API", "Database"
        ],
        education_levels={
            "phd": 90,
            "master": 80,
            "bachelor": 70,
            "diploma": 50,
            "training": 30,
            "unknown": 0
        },
        domain_skills={
            "Python": 30,
            "Java": 30,
            "JavaScript": 25,
            "C++": 25,
            "C#": 25,
            "React": 25,
            "Angular": 25,
            "Vue.js": 20,
            "Node.js": 25,
            "Django": 20,
            "Flask": 20,
            "Spring": 25,
            "SQL": 25,
            "PostgreSQL": 20,
            "MySQL": 20,
            "MongoDB": 20,
            "Git": 20,
            "Docker": 25,
            "Kubernetes": 20,
            "AWS": 25,
            "Azure": 25,
            "Linux": 20,
            "Agile": 15,
            "Scrum": 15
        },
        experience_weight=0.40,
        education_weight=0.20,
        skills_weight=0.30,
        keywords_weight=0.10
    )

def cloud_engineer_requirements() -> CompanyRequirements:
    return CompanyRequirements(
        keywords=[
            "Cloud", "AWS", "Azure", "GCP", "DevOps", "Infrastructure",
            "Containerization", "Microservices", "CI/CD", "Automation"
        ],
        education_levels={
            "phd": 85,
            "master": 75,
            "bachelor": 65,
            "diploma": 45,
            "training": 35,
            "unknown": 0
        },
        domain_skills={
            "AWS": 40,
            "Azure": 40,
            "GCP": 35,
            "Docker": 30,
            "Kubernetes": 35,
            "Terraform": 30,
            "Ansible": 25,
            "Jenkins": 25,
            "GitLab CI": 20,
            "Python": 25,
            "Bash": 20,
            "Linux": 30,
            "Networking": 25,
            "Security": 25,
            "Monitoring": 20,
            "Prometheus": 20,
            "Grafana": 15,
            "ELK Stack": 20,
            "Serverless": 20,
            "Lambda": 15,
            "CloudFormation": 20,
            "ARM Templates": 15
        },
        experience_weight=0.35,
        education_weight=0.15,
        skills_weight=0.40,
        keywords_weight=0.10
    )

def cybersecurity_analyst_requirements() -> CompanyRequirements:
    return CompanyRequirements(
        keywords=[
            "Cybersecurity", "Security", "Penetration Testing", "Vulnerability",
            "SIEM", "Incident Response", "Risk Assessment", "Compliance"
        ],
        education_levels={
            "phd": 95,
            "master": 85,
            "bachelor": 70,
            "diploma": 50,
            "training": 40,
            "unknown": 0
        },
        domain_skills={
            "CISSP": 40,
            "CEH": 35,
            "CISM": 35,
            "CompTIA Security+": 30,
            "Penetration Testing": 35,
            "Vulnerability Assessment": 30,
            "SIEM": 30,
            "Splunk": 25,
            "Wireshark": 25,
            "Nmap": 20,
            "Metasploit": 25,
            "Burp Suite": 20,
            "Kali Linux": 25,
            "Python": 25,
            "PowerShell": 20,
            "Incident Response": 30,
            "Forensics": 25,
            "Risk Management": 25,
            "Compliance": 20,
            "ISO 27001": 20,
            "NIST": 20,
            "Firewall": 20,
            "IDS/IPS": 20
        },
        experience_weight=0.40,
        education_weight=0.25,
        skills_weight=0.25,
        keywords_weight=0.10
    )

def marketing_specialist_requirements() -> CompanyRequirements:
    return CompanyRequirements(
        keywords=[
            "Digital Marketing", "SEO", "SEM", "Social Media", "Analytics",
            "Content Marketing", "Email Marketing", "PPC", "Brand Management"
        ],
        education_levels={
            "phd": 80,
            "master": 75,
            "bachelor": 70,
            "diploma": 50,
            "training": 35,
            "unknown": 0
        },
        domain_skills={
            "Google Analytics": 30,
            "Google Ads": 30,
            "Facebook Ads": 25,
            "SEO": 30,
            "SEM": 25,
            "Content Marketing": 25,
            "Email Marketing": 20,
            "Social Media": 25,
            "Photoshop": 20,
            "Canva": 15,
            "HubSpot": 25,
            "Mailchimp": 20,
            "WordPress": 20,
            "HTML": 15,
            "CSS": 15,
            "Copywriting": 25,
            "Brand Management": 20,
            "Market Research": 20,
            "A/B Testing": 20,
            "CRM": 20
        },
        experience_weight=0.35,
        education_weight=0.25,
        skills_weight=0.30,
        keywords_weight=0.10
    )

POSITION_REQUIREMENTS = {
    "data_scientist": data_scientist_requirements,
    "software_developer": software_developer_requirements,
    "cloud_engineer": cloud_engineer_requirements,
    "cybersecurity_analyst": cybersecurity_analyst_requirements,
    "marketing_specialist": marketing_specialist_requirements
}

def get_requirements_for_position(position: str) -> CompanyRequirements:
    if position.lower() in POSITION_REQUIREMENTS:
        return POSITION_REQUIREMENTS[position.lower()]()
    else:
        raise ValueError(f"Position '{position}' is not defined. Available positions: {list(POSITION_REQUIREMENTS.keys())}")

if __name__ == "__main__":
    print("Available position configurations:")
    for position in POSITION_REQUIREMENTS.keys():
        print(f"- {position}")
    
    print("\nUsage example:")
    print("from config_positions import get_requirements_for_position")
    print("requirements = get_requirements_for_position('data_scientist')")
