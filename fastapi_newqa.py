from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# FastAPI app
app = FastAPI()

# Request schema
class InterviewRequest(BaseModel):
    role: str
    experience: str
    job_description: str
    num_questions: int = 20
    include_answers: bool = False

# Endpoint
@app.post("/generate-questions")
async def generate_questions(request: InterviewRequest):
    try:
        # Define Agents
        question_generator = Agent(
            role="Question Generator",
            backstory="An expert in crafting interview questions by analyzing job descriptions and candidate profiles.",
            goal="Generate high-quality interview questions focusing on technical aspects, with optional answers.",
            tools=[],
            verbose=True
        )

        question_refiner = Agent(
            role="Question Refiner",
            backstory="A skilled HR professional who categorizes interview questions into types for optimal candidate evaluation.",
            goal="Categorize questions into Technical, Behavioral, and Situational, ensuring clarity and structure.",
            tools=[],
            verbose=True
        )

        # Task 1: Generate Questions
        answers_note = "Include detailed answers for each question." if request.include_answers else "Only include questions without answers."
        generate_questions_task = Task(
            description=(
                f"Generate {request.num_questions} interview questions for a {request.role} "
                f"with {request.experience} years of experience. Use the job description below:\n\n"
                f"{request.job_description}\n\n"
                f"Focus primarily on technical questions (around 60-70%), followed by behavioral and situational questions.\n"
                f"{answers_note}"
            ),
            agent=question_generator,
            expected_output="A list of questions (and answers if requested) tailored to the input role and experience."
        )

        # Task 2: Refine and Categorize
        refine_questions_task = Task(
            description=(
                f"Refine and categorize the interview questions generated above into Technical, Behavioral, and Situational. "
                f"Ensure each question is appropriate for a {request.role} with {request.experience} years of experience. "
                f"If answers are provided, format them cleanly."
            ),
            agent=question_refiner,
            depends_on=generate_questions_task,
            expected_output="A structured list of categorized interview questions (and answers if applicable)."
        )

        # Crew setup
        interview_crew = Crew(
            agents=[question_generator, question_refiner],
            tasks=[generate_questions_task, refine_questions_task],
            verbose=True
        )

        # Run Crew
        result = interview_crew.kickoff()
        task_outputs = result.tasks_output

        return {
            "role": request.role,
            "experience": request.experience,
            "job_description": request.job_description,
            "num_questions": request.num_questions,
            "include_answers": request.include_answers,
            "questions_output": task_outputs[-1] if task_outputs else "No questions generated."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
