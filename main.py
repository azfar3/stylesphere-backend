from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from utils.styling_engine import suggest_outfit

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/style")
async def generate_style(
    file: UploadFile = File(...),
    category: str = Form("casual"),
    gender: str = Form("unisex"),
):
    try:
        result = suggest_outfit(file.file, category, gender)
        return result
    except Exception as e:
        return {"error": str(e)}
