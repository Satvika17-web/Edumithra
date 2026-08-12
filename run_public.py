import uvicorn

if __name__ == "__main__":
    # This points to the 'app' object inside 'main.py' which is now inside the 'backend' folder
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)