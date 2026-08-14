import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from backend.database import engine, Base
from backend import auth, curriculum, quiz, chatbot, progress

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application with metadata
app = FastAPI(
    title="AI Learning Platform API",
    description="Intelligent learning platform powered by Groq LLM",
    version="1.0.0"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers with prefixes and tags
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(curriculum.router, prefix="/api/curriculum", tags=["Curriculum"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])
app.include_router(chatbot.router, prefix="/api/chat", tags=["Chatbot"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])

# Root endpoint serving frontend if available, else returning JSON status
@app.get("/")
def root():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(os.path.dirname(backend_dir), "frontend", "index.html")

    if os.path.exists(index_path):
        return FileResponse(index_path)

    return {"message": "AI Learning Platform API", "status": "running"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Server execution block
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)