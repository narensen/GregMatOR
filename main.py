from groq import Groq
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os

# Initialize Groq client with API key from environment
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else Groq()

app = FastAPI()

# Create static directory and mount it
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptInput(BaseModel):
    input: str

@app.post("/generate-test")
async def generate_test(prompt: PromptInput):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a GRE Verbal Question Generator. Make sure you use the right grammar dont be so straightforward. Based on the given input or theme, your task is to create one or more GRE-style Verbal Reasoning questions (e.g., Text Completion, Sentence Equivalence). You must strictly follow this JSON output format:\n\n[\n  {\n \"Question-Type\":\"(TC/SE/RC)\",\n  \"Question\": \"<The full GRE-style question text>\",\n    \"Options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\", \"Option E\", \"Option F\"],\n \"Correct Answer\" : \"The Correct Option For SE it will be two just mark their option\",\n   \"Explanation\": \"<A clear, concise explanation of the correct answer(s), including why the correct choice(s) work and why the others do not>\"\n  }\n]\n\n⚠️ IMPORTANT:\n- You must only return a valid JSON string — no markdown, no backticks, no extra text.\n- The output must be a pure JSON string (not markdown formatted or code block wrapped).\n- Ensure that the JSON is properly escaped and syntactically correct.\n- If multiple questions are generated, return them as elements in a JSON array.\n- All strings must use double quotes (\"\").\n\nFollow GRE difficulty and tone guidelines. Avoid repetition. Include only content relevant to the JSON."
                },
                {
                    "role": "user",
                    "content": prompt.input,
                }
            ],
            model="meta-llama/llama-4-maverick-17b-128e-instruct"
        )

        print(chat_completion.choices[0].message.content)
        return json.loads(chat_completion.choices[0].message.content)

    except Exception as e:
        print("Error:", str(e))
        return {"Error": "Something went wrong. Please try again."}