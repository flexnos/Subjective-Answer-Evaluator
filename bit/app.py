from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main import app as main_app

app = FastAPI(title="Answer Evaluation System", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/", main_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)