from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from langgraph.checkpoint.postgres import PostgresSaver
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import create_weather_agent
from swagger_theme_toggle import add_dark_mode_toggle

load_dotenv()

DB_URI = os.getenv("SUPABASE_DB_URI")

checkpointer = None
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global checkpointer, agent
    
    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        checkpointer.setup()
        agent = create_weather_agent(checkpointer)
        yield

app = FastAPI(
    title="Weather Agent API",
    lifespan=lifespan,
    swagger_ui_parameters={
        "syntaxHighlight.theme": "obsidian"
    }        
    )

add_dark_mode_toggle(app, default_theme="dark")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str
    
class ChatResponse(BaseModel):
    reply: str
    
@app.get('/')
def root():
    return {"status": "ok", "message": "Weather Agent API is running"}

@app.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": body.message}]},
        {"configurable": {"thread_id": body.thread_id}},
    )
    return ChatResponse(reply=response["messages"][-1].content)

    