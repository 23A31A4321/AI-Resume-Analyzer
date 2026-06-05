from flask import Flask
from flask import render_template
from flask import request

import PyPDF2
import sqlite3

from skills import skills

app = Flask(__name__)
def create_database():

    conn = sqlite3.connect("history.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_score INTEGER,
        ats_score INTEGER,
        match_score REAL,
        skills TEXT,
        missing_skills TEXT
    )
    """)

    conn.commit()

    conn.close()
def save_analysis(
    resume_score,
    ats_score,
    match_score,
    skills,
    missing_skills
):

    conn = sqlite3.connect("history.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO history
        (
            resume_score,
            ats_score,
            match_score,
            skills,
            missing_skills
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            resume_score,
            ats_score,
            match_score,
            skills,
            missing_skills
        )
    )

    conn.commit()

    conn.close()
def get_history():

    conn = sqlite3.connect("history.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM history
        ORDER BY id DESC
        """
    )

    records = cursor.fetchall()

    conn.close()

    return records

# Add the function here
def extract_text(pdf_file):

    text = ""

    reader = PyPDF2.PdfReader(pdf_file)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text

    return text


# Add extract_skills() below this
def extract_skills(text):

    found = []

    text = text.lower()

    for skill in skills:

        if skill in text:
            found.append(skill)

    return found


# Add calculate_score() below this
def calculate_score(found_skills):

    score = len(found_skills) * 10

    if score > 100:
        score = 100

    return score

def calculate_ats_score(text):

    score = 0

    text = text.lower()

    if "@" in text:
        score += 10

    if any(word in text for word in ["python", "java", "sql", "html", "css"]):
        score += 20

    if "project" in text:
        score += 20

    if "education" in text:
        score += 20

    if any(word in text for word in ["internship", "experience"]):
        score += 20

    if any(word in text for word in ["certificate", "certification"]):
        score += 10

    return score
def find_missing_skills(
    resume_skills,
    job_description
):

    missing = []

    job_description = job_description.lower()

    for skill in skills:

        if (
            skill in job_description
            and skill not in resume_skills
        ):
            missing.append(skill)

    return missing
def generate_recommendations(
    resume_skills,
    missing_skills
):

    recommendations = []

    for skill in missing_skills:

        recommendations.append(
            f"Learn {skill.title()}"
        )

    if len(resume_skills) < 5:

        recommendations.append(
            "Add more technical skills"
        )

    if "github" not in resume_skills:

        recommendations.append(
            "Create a GitHub profile"
        )

    if "git" not in resume_skills:

        recommendations.append(
            "Learn Git"
        )

    return recommendations
def calculate_skill_match(
    resume_skills,
    job_description
):

    job_skills = []

    job_description = job_description.lower()

    for skill in skills:

        if skill in job_description:
            job_skills.append(skill)

    if len(job_skills) == 0:
        return 100

    matched = 0

    for skill in job_skills:

        if skill in resume_skills:
            matched += 1

    return round((matched / len(job_skills)) * 100, 2)

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        print("POST request received")

        resume = request.files["resume"]
        job_description = request.form["job_description"]

        text = extract_text(resume)

        found_skills = extract_skills(text)

        score = calculate_score(found_skills)

        ats_score = calculate_ats_score(text)
        match_score = calculate_skill_match(found_skills,job_description)

        missing_skills = find_missing_skills(found_skills,job_description)
        recommendations = generate_recommendations(found_skills,missing_skills)
        save_analysis(
        score,
        ats_score,
        match_score,
        ",".join(found_skills),
        ",".join(missing_skills)
        ) 

        return render_template(
        "result.html",
        skills=found_skills,
        score=score,
        ats_score=ats_score,
        match_score=match_score,
        missing_skills=missing_skills,
        recommendations=recommendations
        )

    return render_template("index.html")


@app.route("/history")
def history():

    records = get_history()

    return render_template(
        "history.html",
        records=records
    )


create_database()

if __name__ == "__main__":
    app.run(debug=True)