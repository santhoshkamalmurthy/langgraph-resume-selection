import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from docx import Document
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from PyPDF2 import PdfReader


load_dotenv()

class State(TypedDict):
  application: str
  experience_level: str
  skill_match : str
  response: str

app = FastAPI()
llm = ChatGroq(model='llama-3.3-70b-versatile')

JOB_DESC_PATH = os.path.join(os.path.dirname(__file__), 'job_description.txt')

class ResumeProcessResult(BaseModel):
    experience_level: str
    skill_match: str
    response: str
    

# Utility: Read job description from file
def read_job_description() -> str:
    with open(JOB_DESC_PATH, 'r') as f:
        return f.read()

# Utility: Extract text from resume file
def extract_resume_text(file: UploadFile) -> str:
    if file.filename.endswith('.pdf'):
        reader = PdfReader(file.file)
        text = " ".join(page.extract_text() or '' for page in reader.pages)
        return text
    elif file.filename.endswith('.docx'):
        doc = Document(file.file)
        text = " ".join([p.text for p in doc.paragraphs])
        return text
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF and DOCX are supported.")

# Prompt: Categorize experience level
def categorize_experience(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        """
        Based on the following job application, categorize the candidate as 'Entry-level', 'Mid-level' or 'Senior-level' in one word.
        Entry-level: 0 years of experience
        Mid-level: 2-6 years of experience
        Senior-level: 7+ years of experience
        Application: {application}
        """
    )
    chain = prompt | llm
    experience_level = chain.invoke({"application": state["application"]}).content
    print(f"Experience Level : {experience_level}")
    return {"experience_level" : experience_level}

# Prompt: Assess skillset match
def assess_skillset(state: State) -> State:
    job_description = read_job_description()
    prompt = ChatPromptTemplate.from_template(
        """
        Given the following job description and candidate application, does the candidate match the required skills? Respond with either 'Match' or 'No Match' in one word.\nJob Description: {job_description}\nApplication: {application}
        """
    )
    chain = prompt | llm
    skill_match = chain.invoke({"application": state["application"], "job_description": job_description}).content
    print(f"Skill Match : {skill_match}")
    return {"skill_match" : skill_match}

def schedule_hr_interview(state: State) -> State:
  print("\nScheduling the interview : ")
  return {"response" : "Candidate has been shortlisted for an HR interview."}

def escalate_to_recruiter(state: State) -> State:
  print("Escalating to recruiter")
  return {"response" : "Candidate has senior-level experience but doesn't match job skills."}

def reject_application(state: State) -> State:
  print("Sending rejecting email")
  return {"response" : "Candidate doesn't meet JD and has been rejected."}

# Decision logic
def make_decision(experience_level: str, skill_match: str) -> str:
    if skill_match == "Match":
        return "Candidate has been shortlisted for an HR interview."
    elif experience_level == "Senior-level":
        return "Candidate has senior-level experience but doesn't match job skills."
    else:
        return "Candidate doesn't meet JD and has been rejected."

def route_app(state: State) -> str:
  if(state["skill_match"] == "Match"):
    return "schedule_hr_interview"
  elif(state["experience_level"] == "Senior-level"):
    return "escalate_to_recruiter"
  else:
    return "reject_application"

workflow = StateGraph(State)
workflow.add_node("categorize_experience", categorize_experience)
workflow.add_node("assess_skillset", assess_skillset)
workflow.add_node("schedule_hr_interview", schedule_hr_interview)
workflow.add_node("escalate_to_recruiter", escalate_to_recruiter)
workflow.add_node("reject_application", reject_application)
workflow.add_edge("categorize_experience", "assess_skillset")
workflow.add_conditional_edges("assess_skillset", route_app)
workflow.add_edge(START, "categorize_experience")
workflow.add_edge("assess_skillset", END)
workflow.add_edge("escalate_to_recruiter", END)
workflow.add_edge("reject_application", END)
workflow.add_edge("schedule_hr_interview", END)
workflow_compiler = workflow.compile()

def run_candidate_screening(application: str):
  results = workflow_compiler.invoke({"application" : application})
  return {
      "experience_level" : results["experience_level"],
      "skill_match" : results["skill_match"],
      "response" : results["response"]
  }

@app.post("/process-resume", response_model=ResumeProcessResult)
async def process_resume(file: UploadFile = File(...)):
    application = extract_resume_text(file)
    print("application", application)
    results = run_candidate_screening(application)
    if not application.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from resume.")
    return ResumeProcessResult(
        experience_level=results["experience_level"],
        skill_match=results["skill_match"],
        response=results["response"]
    )