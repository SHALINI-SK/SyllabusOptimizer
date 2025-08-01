from flask import Flask, render_template, request
import requests
import json
from flask import send_file
from io import BytesIO
from xhtml2pdf import pisa

from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("IBM_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")



app = Flask(__name__)



def get_access_token(api_key):
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]

def generate_syllabus(user_input):
    access_token = get_access_token(API_KEY)

    prompt = f"""
You are an AI assistant helping faculty refine academic syllabi.

Given the raw syllabus content below, generate a professional syllabus that includes:
- Course Title
- Course Description
- Weekly Topics
- Learning Outcomes
- Assessment Methods

Raw Syllabus:
{user_input}
"""

    payload = {
        "model_id": "ibm/granite-13b-instruct-v2",
        "input": prompt,
        "project_id": PROJECT_ID,
        "parameters": {
            "max_new_tokens": 400,
            "temperature": 0.7
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"https://{REGION}.ml.cloud.ibm.com/ml/v1/text/generation?version=2024-05-20",
        headers=headers,
        data=json.dumps(payload)
    )

    try:
        return response.json()["results"][0]["generated_text"]
    except:
        return "❌ Error: Could not generate syllabus."

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        user_input = request.form.get("syllabus", "").strip()
        if user_input:
            result = generate_syllabus(user_input)
        else:
            result = "⚠️ Please enter syllabus content."
    return render_template("index.html", result=result)

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    syllabus_content = request.form.get("result")
    pdf_buffer = BytesIO()
    rendered = render_template("pdf_template.html", result=syllabus_content)
    pisa_status = pisa.CreatePDF(rendered, dest=pdf_buffer)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, as_attachment=True, download_name="syllabus.pdf", mimetype='application/pdf')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        comments = request.form['comments']
        with open("feedback.txt", "a") as f:
            f.write(f"Name: {name}\nComments: {comments}\n{'-'*40}\n")
        return render_template("feedback.html", submitted=True)
    return render_template("feedback.html", submitted=False)


if __name__ == "__main__":
    app.run(debug=True)
