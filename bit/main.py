from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Optional
import numpy as np
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import pickle
from PIL import Image
import pytesseract
import io
import re
from fuzzywuzzy import fuzz

# -------------------------
# FastAPI Init
# -------------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# -------------------------
# Models
# -------------------------
models = {
    "MiniLM": SentenceTransformer("all-MiniLM-L6-v2"),
}
default_model = "MiniLM"

# Load CNN model + tokenizer
cnn_model = load_model("cnn_answer_evaluator.h5")
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)
cnn_max_len = 100  # same as during training

# -------------------------
# Schemas
# -------------------------
class AnswerRequest(BaseModel):
    question: str
    reference_answer: str
    student_answer: str
    model_name: Optional[str] = default_model

    class Config:
        protected_namespaces = ()

class AdvancedResult(BaseModel):
    question: str
    student_answer: str
    similarity: float
    coverage: float
    grammar: float
    final_score: float
    feedback: str

# -------------------------
# Utilities
# -------------------------
def clean_ocr_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"[^a-zA-Z0-9\s.,]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def keyword_coverage(ref: str, ans: str) -> float:
    vectorizer = TfidfVectorizer(stop_words="english")
    vectorizer.fit([ref])
    keywords = vectorizer.get_feature_names_out()
    matched = sum(1 for kw in keywords if kw in ans.lower())
    return matched / len(keywords) if len(keywords) else 0

def fuzzy_keyword_coverage(ref: str, ans: str) -> float:
    ref_words = ref.lower().split()
    ans_words = ans.lower().split()
    matched = 0
    for word in ref_words:
        if any(fuzz.ratio(word, a) > 80 for a in ans_words):
            matched += 1
    return matched / len(ref_words) if ref_words else 0

def grammar_score(text: str) -> float:
    try:
        from gingerit.gingerit import GingerIt
        parser = GingerIt()
        result = parser.parse(text)
        corrections = result.get("corrections", [])
        return max(0, 1 - len(corrections)/max(1, len(text.split())))
    except Exception:
        sentences = re.split(r'[.!?]', text)
        sentence_count = len([s for s in sentences if s.strip()])
        capitalized = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
        ratio = capitalized / sentence_count if sentence_count else 1
        return round(ratio, 2)

def compute_similarity(model, ref, ans) -> float:
    emb1 = model.encode(ref, convert_to_tensor=True)
    emb2 = model.encode(ans, convert_to_tensor=True)
    return util.cos_sim(emb1, emb2).item()

def full_feedback(score: float) -> str:
    if score > 8:
        return "Excellent! Relevant, well-structured, and accurate."
    elif score > 5:
        return "Good. Covers key points but needs improvement in detail/grammar."
    else:
        return "Weak answer. Improve relevance, grammar, and completeness."

# -------------------------
# Endpoints
# -------------------------

@app.post("/evaluate_image")
def evaluate_image(file: UploadFile = File(...), model_answer: str = "", question: str = ""):
    try:
        # Read image
        image = Image.open(io.BytesIO(file.file.read()))

        # OCR with better config
        student_answer = pytesseract.image_to_string(image, config="--psm 6")
        student_answer = clean_ocr_text(student_answer)

        # Use embeddings + fuzzy coverage for scoring
        model = models[default_model]
        similarity = compute_similarity(model, model_answer, student_answer)
        coverage = fuzzy_keyword_coverage(model_answer, student_answer)
        grammar = grammar_score(student_answer)

        # Different weights for image answers (less grammar weight)
        final_score = round((0.6 * similarity + 0.35 * coverage + 0.05 * grammar) * 10, 2)

        return {
            "question": question,
            "student_answer": student_answer,
            "similarity": round(similarity, 2),
            "coverage": round(coverage, 2),
            "grammar": round(grammar, 2),
            "final_score": final_score,
            "feedback": full_feedback(final_score),
            "extracted_text": student_answer
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"OCR/Eval error: {ex}")

@app.post("/evaluate_advanced", response_model=AdvancedResult)
def evaluate_advanced(data: AnswerRequest):
    model = models.get(data.model_name, models[default_model])
    try:
        similarity = compute_similarity(model, data.reference_answer, data.student_answer)
        coverage = keyword_coverage(data.reference_answer, data.student_answer)
        grammar = grammar_score(data.student_answer)
        final_score = round((0.5 * similarity + 0.3 * coverage + 0.2 * grammar) * 10, 2)
        return AdvancedResult(
            question=data.question,
            student_answer=data.student_answer,
            similarity=round(similarity, 2),
            coverage=round(coverage, 2),
            grammar=round(grammar, 2),
            final_score=final_score,
            feedback=full_feedback(final_score),
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Evaluation error: {ex}")

@app.post("/evaluate")
def evaluate_basic(data: AnswerRequest):
    try:
        model_emb = models[default_model].encode(data.reference_answer, convert_to_tensor=True)
        student_emb = models[default_model].encode(data.student_answer, convert_to_tensor=True)
        similarity = util.cos_sim(model_emb, student_emb).item()
        score = round(similarity * 10, 2)
        if score > 8:
            feedback = "Excellent! Your answer is very close to the reference answer."
        elif score > 5:
            feedback = "Good attempt. You covered some important points but missed a few."
        else:
            feedback = "Needs improvement. Try to include more relevant details."
        return {
            "question": data.question,
            "student_answer": data.student_answer,
            "score": score,
            "feedback": feedback,
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Evaluation error: {ex}")

def preprocess_cnn_inputs(reference, student):
    ref_seq = tokenizer.texts_to_sequences([reference])
    stu_seq = tokenizer.texts_to_sequences([student])
    ref_pad = pad_sequences(ref_seq, maxlen=cnn_max_len)
    stu_pad = pad_sequences(stu_seq, maxlen=cnn_max_len)
    combined = np.concatenate([ref_pad, stu_pad], axis=1)
    return combined

@app.post("/evaluate_cnn")
def evaluate_cnn(data: AnswerRequest):
    try:
        x = preprocess_cnn_inputs(data.reference_answer, data.student_answer)
        similarity = cnn_model.predict(x)[0][0]
        similarity = float(np.clip(similarity, 0, 1))
        final_score = round(similarity * 10, 2)

        if final_score > 8:
            feedback = "Excellent! Your answer closely matches the reference."
        elif final_score > 5:
            feedback = "Good effort but room for improvement."
        else:
            feedback = "Needs improvement. Consider including relevant points."

        return {
            "question": data.question,
            "student_answer": data.student_answer,
            "cnn_similarity": round(similarity, 3),
            "final_score": final_score,
            "feedback": feedback,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Advanced API running! See /docs"}
