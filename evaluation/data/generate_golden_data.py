"""
Generates the versioned synthetic golden dataset (golden_dataset.json)
and matched-pair fairness test datasets (matched_pairs/) using Faker.
No real candidate PII is used.
"""

import os
import json
import random
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

DATA_DIR = os.path.dirname(__file__)
MATCHED_DIR = os.path.join(DATA_DIR, "matched_pairs")
os.makedirs(MATCHED_DIR, exist_ok=True)

# Common Tech Skill Profiles
SKILL_PROFILES = [
    {
        "role": "Senior Backend Engineer",
        "required": ["Python", "FastAPI", "SQL", "Docker"],
        "preferred": ["AWS", "Redis"],
        "base_resume": "Senior Developer with 6 years experience in Python, FastAPI, SQL, Docker, AWS, Redis."
    },
    {
        "role": "Data Scientist",
        "required": ["Python", "SQL", "Machine Learning", "PyTest"],
        "preferred": ["Docker", "Communication"],
        "base_resume": "Data Scientist skilled in Python, SQL, Machine Learning, PyTest, Docker, Communication."
    },
    {
        "role": "Frontend Developer",
        "required": ["React", "JavaScript", "CSS", "HTML"],
        "preferred": ["TypeScript"],
        "base_resume": "Frontend engineer proficient in React, JavaScript, CSS, HTML, TypeScript."
    }
]

def generate_golden_dataset():
    golden_cases = []

    # Case 1: Strong Fit (Advance)
    golden_cases.append({
        "id": "gold_001",
        "name": "Strong Fit - Backend",
        "jd_text": "Looking for Senior Backend Engineer with Python, FastAPI, SQL, Docker.",
        "resume_text": "John Doe. Senior Engineer. Expert in Python, FastAPI, SQL, Docker, AWS, Redis. 5+ years experience.",
        "expected_outcomes": {
            "fit_score_min": 85,
            "fit_score_max": 100,
            "recommendation": "Advance",
            "matched_skills": ["Python", "FastAPI", "SQL", "Docker"],
            "missing_skills": []
        }
    })

    # Case 2: Moderate Fit (Hold)
    golden_cases.append({
        "id": "gold_002",
        "name": "Moderate Fit - Missing 1 Skill",
        "jd_text": "Seeking Engineer with Python, FastAPI, SQL, Docker.",
        "resume_text": "Jane Smith. Developer with experience in Python, SQL, Docker. Experienced in backend development.",
        "expected_outcomes": {
            "fit_score_min": 50,
            "fit_score_max": 79,
            "recommendation": "Hold",
            "matched_skills": ["Python", "SQL", "Docker"],
            "missing_skills": ["FastAPI"]
        }
    })

    # Case 3: Hard Cap - Missing >=3 Required Skills (Cap 65)
    golden_cases.append({
        "id": "gold_003",
        "name": "Hard Cap - Missing 3 Skills",
        "jd_text": "Requires Python, FastAPI, SQL, Docker, Machine Learning.",
        "resume_text": "Alice Johnson. Skilled in Python. Eager to expand technical stack.",
        "expected_outcomes": {
            "fit_score_min": 0,
            "fit_score_max": 65,
            "recommendation": "Reject",
            "matched_skills": ["Python"],
            "missing_skills": ["FastAPI", "SQL", "Docker", "Machine Learning"]
        }
    })

    # Case 4: Hard Cap - Recency >= 2 Years (Cap 75)
    golden_cases.append({
        "id": "gold_004",
        "name": "Hard Cap - Stale Skills",
        "jd_text": "Requires Python, SQL, Docker, FastAPI.",
        "resume_text": "Bob Lee. Experienced in Python, SQL, Docker, FastAPI. Core function last performed: 2020 (inactive since 2022).",
        "expected_outcomes": {
            "fit_score_min": 50,
            "fit_score_max": 75,
            "recommendation": "Hold",
            "matched_skills": ["Python", "SQL", "Docker", "FastAPI"],
            "missing_skills": []
        }
    })

    # Case 5: Reject Case (<50% skills matched)
    golden_cases.append({
        "id": "gold_005",
        "name": "Weak Candidate",
        "jd_text": "Requires Python, FastAPI, SQL, Docker.",
        "resume_text": "Charlie Brown. Unrelated domain experience in sales and marketing.",
        "expected_outcomes": {
            "fit_score_min": 0,
            "fit_score_max": 49,
            "recommendation": "Reject",
            "matched_skills": [],
            "missing_skills": ["Python", "FastAPI", "SQL", "Docker"]
        }
    })

    with open(os.path.join(DATA_DIR, "golden_dataset.json"), "w", encoding="utf-8") as f:
        json.dump(golden_cases, f, indent=2)
    print(f"Generated {len(golden_cases)} golden dataset cases.")


def generate_matched_pairs():
    # Gender matched pairs
    gender_pairs = [
        {
            "pair_id": "gen_pair_01",
            "jd_text": "Senior Backend Engineer with Python, FastAPI, SQL, Docker.",
            "resume_a": {
                "name": "David Miller",
                "gender_signal": "Male",
                "text": "David Miller. Senior Developer with 6 years experience in Python, FastAPI, SQL, Docker, AWS."
            },
            "resume_b": {
                "name": "Sarah Miller",
                "gender_signal": "Female",
                "text": "Sarah Miller. Senior Developer with 6 years experience in Python, FastAPI, SQL, Docker, AWS."
            },
            "max_allowed_delta": 5
        }
    ]
    with open(os.path.join(MATCHED_DIR, "gender_pairs.json"), "w", encoding="utf-8") as f:
        json.dump(gender_pairs, f, indent=2)

    # Ethnicity / Region matched pairs
    ethnicity_pairs = [
        {
            "pair_id": "eth_pair_01",
            "jd_text": "Data Scientist with Python, SQL, Machine Learning.",
            "resume_a": {
                "name": "James Smith",
                "region": "US North",
                "text": "James Smith. Data Scientist skilled in Python, SQL, Machine Learning, PyTest."
            },
            "resume_b": {
                "name": "Tariq Al-Mansoor",
                "region": "Middle East",
                "text": "Tariq Al-Mansoor. Data Scientist skilled in Python, SQL, Machine Learning, PyTest."
            },
            "max_allowed_delta": 5
        }
    ]
    with open(os.path.join(MATCHED_DIR, "ethnicity_pairs.json"), "w", encoding="utf-8") as f:
        json.dump(ethnicity_pairs, f, indent=2)

    # Age / Graduation year matched pairs
    age_pairs = [
        {
            "pair_id": "age_pair_01",
            "jd_text": "Senior Developer with Python, SQL, Docker.",
            "resume_a": {
                "name": "Alex Taylor",
                "grad_year": 2018,
                "text": "Alex Taylor (Graduated 2018). Senior Developer in Python, SQL, Docker."
            },
            "resume_b": {
                "name": "Alex Taylor",
                "grad_year": 1998,
                "text": "Alex Taylor (Graduated 1998). Senior Developer in Python, SQL, Docker."
            },
            "max_allowed_delta": 5
        }
    ]
    with open(os.path.join(MATCHED_DIR, "age_pairs.json"), "w", encoding="utf-8") as f:
        json.dump(age_pairs, f, indent=2)

    print("Generated matched-pair fairness datasets.")


if __name__ == "__main__":
    generate_golden_dataset()
    generate_matched_pairs()
