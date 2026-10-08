# EDUMITHRA – Intelligent Learning Platform

## Overview
EDUMITHRA is an AI-powered learning platform backend built with FastAPI, SQLAlchemy, and Groq Cloud. It features an automated curriculum generator and an interactive AI tutor powered by Llama 3.3 70B via the Groq API.

## Technology Stack
* **Backend Framework:** FastAPI, SQLAlchemy
* **AI Model & Inference:** Llama 3.3 70B via Groq Cloud API
* **Database:** SQLite / SQLAlchemy ORM
* **Frontend:** HTML, CSS, JavaScript

## System Architecture & Workflow
1. **User Request:** The user interacts with the web interface to request a curriculum or ask the AI tutor a question.
2. **Backend Processing:** FastAPI routes the request, handling authentication and database interactions.
3. **AI Generation:** The backend uses the Groq Python SDK to query the Llama 3.3 70B model with ultra-low latency.
4. **Response Delivery:** The generated study plan or tutor response is sent back and displayed on the interface.

## How to Run
1. Activate your virtual environment.
2. Run `pip install -r requirements.txt` to install dependencies.
3. Run `python run_public.py` to start the server.