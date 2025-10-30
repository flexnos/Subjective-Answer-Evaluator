from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import fitz
from PIL import Image, ImageEnhance
import pytesseract
import io
import re
import logging
from datetime import datetime
from sentence_transformers import SentenceTransformer, util

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdf", tags=["PDF Evaluation"])

try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("PDF Module: Model loaded successfully")
except Exception as e:
    logger.error(f"PDF Module: Failed to load model: {e}")
    model = None

# =============================================
# SCHEMAS
# =============================================
class QuestionResult(BaseModel):
    question_number: int
    question_text: str
    extracted_answer: str
    max_marks: int
    obtained_marks: float
    similarity_score: float
    coverage_score: float
    feedback: str

class PDFEvalResult(BaseModel):
    student_name: Optional[str]
    exam_name: str
    total_max_marks: int
    total_obtained_marks: float
    percentage: float
    grade: str
    questions_results: List[QuestionResult]
    evaluation_timestamp: str
    processing_time: float

# =============================================
# UTILITY FUNCTIONS
# =============================================
def extract_text_from_pdf(pdf_bytes: bytes) -> Dict[int, str]:
    """Extract text from PDF pages"""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages_text = {}
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            pages_text[page_num + 1] = text
        doc.close()
        return pages_text
    except Exception as e:
        logger.error(f"PDF text extraction error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {str(e)}")

def extract_images_from_pdf(pdf_bytes: bytes) -> Dict[int, List[Image.Image]]:
    """Extract images from PDF for OCR"""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages_images = {}
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            pages_images.setdefault(page_num + 1, []).append(image)
        doc.close()
        return pages_images
    except Exception as e:
        logger.error(f"PDF image extraction error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to extract images: {str(e)}")

def ocr_image(image: Image.Image) -> str:
    """Perform OCR on image"""
    try:
        results = []
        text1 = pytesseract.image_to_string(image, config='--psm 6')
        results.append(text1)
        gray = image.convert('L')
        enhanced = ImageEnhance.Contrast(gray).enhance(2.0)
        text2 = pytesseract.image_to_string(enhanced, config='--psm 6')
        results.append(text2)
        best_text = max(results, key=len)
        return best_text.strip()
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""

def clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted text"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(?i)c\s*o\s*2', 'CO2', text)
    text = re.sub(r'(?i)h\s*2\s*o', 'H2O', text)
    text = re.sub(r'(?i)o\s*2', 'O2', text)
    return text.strip()

def extract_answer_for_question(all_text: str, question_num: int, next_question_num: Optional[int] = None) -> str:
    """Extract student answer for specific question number"""
    if next_question_num:
        pattern_end = fr'(?:q\.?\s*{next_question_num}|question\s*{next_question_num}|{next_question_num}\.)'
    else:
        pattern_end = r'\Z'

    patterns = [
        rf'(?i)q\.?\s*{question_num}[\s:.\)]+(.+?)(?={pattern_end})',
        rf'(?i)question\s*{question_num}[\s:.\)]+(.+?)(?={pattern_end})',
        rf'(?i){question_num}\.?\s+(.+?)(?={pattern_end})',
    ]

    for pattern in patterns:
        match = re.search(pattern, all_text, re.DOTALL)
        if match:
            answer = match.group(1).strip()
            return clean_extracted_text(answer)

    lines = all_text.split('\n')
    in_answer = False
    answer_lines = []
    for line in lines:
        if re.search(rf'(?i)q\.?\s*{question_num}[\s:.\)]', line):
            in_answer = True
            continue
        if next_question_num and re.search(rf'(?i)q\.?\s*{next_question_num}[\s:.\)]', line):
            break
        if in_answer:
            answer_lines.append(line)
    return clean_extracted_text(' '.join(answer_lines))

def calculate_similarity(reference: str, student: str) -> float:
    """Calculate semantic similarity between reference and student answer"""
    if not model:
        return 0.0
    try:
        ref_emb = model.encode(reference, convert_to_tensor=True)
        student_emb = model.encode(student, convert_to_tensor=True)
        similarity = util.cos_sim(ref_emb, student_emb).item()
        return (similarity + 1) / 2
    except Exception as e:
        logger.error(f"Similarity calculation error: {e}")
        return 0.0

def calculate_coverage(reference: str, student: str) -> float:
    """Calculate keyword coverage"""
    ref_words = set(word.lower() for word in reference.split() if len(word) > 3)
    student_words = set(word.lower() for word in student.split() if len(word) > 3)
    if not ref_words:
        return 0.0
    common = ref_words.intersection(student_words)
    return len(common) / len(ref_words)

def calculate_marks(similarity: float, coverage: float, max_marks: int) -> float:
    """Calculate marks based on similarity and coverage"""
    score = (0.6 * similarity + 0.4 * coverage)
    marks = score * max_marks
    return round(marks, 2)

def generate_feedback(similarity: float, coverage: float, obtained_marks: float, max_marks: int) -> str:
    """Generate feedback based on performance"""
    percentage = (obtained_marks / max_marks) * 100 if max_marks > 0 else 0
    if percentage >= 90:
        return "Excellent! Very comprehensive answer."
    elif percentage >= 75:
        return "Good answer. Minor improvements possible."
    elif percentage >= 60:
        return "Satisfactory. Some concepts missing."
    elif percentage >= 40:
        return "Needs improvement. Lacks detail."
    else:
        return "Insufficient answer. Review the topic."

def determine_grade(percentage: float) -> str:
    """Determine letter grade from percentage"""
    if percentage >= 90: return "A+"
    elif percentage >= 85: return "A"
    elif percentage >= 80: return "A-"
    elif percentage >= 75: return "B+"
    elif percentage >= 70: return "B"
    elif percentage >= 65: return "B-"
    elif percentage >= 60: return "C+"
    elif percentage >= 55: return "C"
    elif percentage >= 50: return "C-"
    elif percentage >= 40: return "D"
    else: return "F"

def parse_question_paper(text: str) -> List[Dict]:
    """Extract questions and marks from question paper PDF"""
    questions = []
    lines = text.split('\n')
    current_q = None
    
    for line in lines:
        # Match patterns like "Q1.", "Question 1:", "1)", etc.
        q_match = re.match(r'(?i)(?:q(?:uestion)?\.?\s*)?(\d+)[.):\s]+(.+)', line.strip())
        # Match marks like "[5 marks]", "(10)", "Marks: 5"
        marks_match = re.search(r'(?i)(?:\[|\()?(\d+)\s*(?:marks?|m)(?:\]|\))?', line)
        
        if q_match:
            if current_q:
                questions.append(current_q)
            current_q = {
                'number': int(q_match.group(1)),
                'text': q_match.group(2).strip(),
                'marks': 5  # default
            }
        elif marks_match and current_q:
            current_q['marks'] = int(marks_match.group(1))
        elif current_q and line.strip():
            current_q['text'] += ' ' + line.strip()
    
    if current_q:
        questions.append(current_q)
    
    return questions

# =============================================
# ENDPOINTS
# =============================================
@router.post("/evaluate_pdf_direct", response_model=PDFEvalResult)
async def evaluate_pdf_direct(
    answer_sheet: UploadFile = File(..., description="Student's answer sheet PDF"),
    question_paper: UploadFile = File(..., description="Question paper PDF"),
    reference_answers: UploadFile = File(..., description="Reference answers PDF or text file"),
    student_name: str = Form(""),
    exam_name: str = Form("Exam Evaluation")
):
    """
    Direct PDF evaluation - upload answer sheet, question paper, and reference answers
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Starting PDF evaluation for student: {student_name}, exam: {exam_name}")
        
        # Extract answer sheet text
        answer_pdf = await answer_sheet.read()
        answer_pages = extract_text_from_pdf(answer_pdf)
        total_answer_text = ' '.join(answer_pages.values())
        
        logger.info(f"Extracted {len(total_answer_text)} characters from answer sheet")
        
        # If sparse, try OCR
        if len(total_answer_text.strip()) < 100:
            logger.info("Running OCR on answer sheet...")
            answer_images = extract_images_from_pdf(answer_pdf)
            for page_num, images in answer_images.items():
                ocr_text = ""
                for img in images:
                    ocr_text += ocr_image(img) + "\n"
                answer_pages[page_num] = ocr_text
            total_answer_text = ' '.join(answer_pages.values())
            logger.info(f"After OCR: {len(total_answer_text)} characters")
        
        # Extract question paper
        qp_pdf = await question_paper.read()
        qp_pages = extract_text_from_pdf(qp_pdf)
        qp_text = ' '.join(qp_pages.values())
        questions_data = parse_question_paper(qp_text)
        
        logger.info(f"Extracted {len(questions_data)} questions from question paper")
        
        if not questions_data:
            raise HTTPException(status_code=400, detail="Could not extract questions from question paper")
        
        # Extract reference answers
        ref_pdf = await reference_answers.read()
        if reference_answers.filename.endswith('.txt'):
            ref_text = ref_pdf.decode('utf-8')
        else:
            ref_pages = extract_text_from_pdf(ref_pdf)
            ref_text = ' '.join(ref_pages.values())
        
        logger.info(f"Extracted {len(ref_text)} characters from reference answers")
        
        # Parse reference answers
        ref_answers_dict = {}
        for q_data in questions_data:
            q_num = q_data['number']
            patterns = [
                rf'(?i)q\.?\s*{q_num}[\s:.\)]+(.+?)(?=q\.?\s*{q_num+1}|\Z)',
                rf'(?i)question\s*{q_num}[\s:.\)]+(.+?)(?=question\s*{q_num+1}|\Z)',
            ]
            ref_ans = ""
            for pattern in patterns:
                match = re.search(pattern, ref_text, re.DOTALL)
                if match:
                    ref_ans = clean_extracted_text(match.group(1))
                    break
            ref_answers_dict[q_num] = ref_ans if ref_ans else "Reference answer not found"
        
        # Evaluate each question
        results = []
        total_obtained = 0.0
        total_marks = sum(q['marks'] for q in questions_data)
        
        for idx, q_data in enumerate(questions_data):
            q_num = q_data['number']
            next_q_num = questions_data[idx + 1]['number'] if idx + 1 < len(questions_data) else None
            
            extracted_ans = extract_answer_for_question(total_answer_text, q_num, next_q_num)
            ref_ans = ref_answers_dict.get(q_num, "")
            
            if not extracted_ans or len(extracted_ans) < 10:
                similarity = 0.0
                coverage = 0.0
                obtained = 0.0
                feedback = "No answer detected"
            elif not ref_ans or ref_ans == "Reference answer not found":
                similarity = 0.5
                coverage = 0.5
                obtained = q_data['marks'] * 0.5
                feedback = "Reference answer not available, estimated score"
            else:
                similarity = calculate_similarity(ref_ans, extracted_ans)
                coverage = calculate_coverage(ref_ans, extracted_ans)
                obtained = calculate_marks(similarity, coverage, q_data['marks'])
                feedback = generate_feedback(similarity, coverage, obtained, q_data['marks'])
            
            results.append(QuestionResult(
                question_number=q_num,
                question_text=q_data['text'][:200],
                extracted_answer=extracted_ans[:300] if extracted_ans else "No answer found",
                max_marks=q_data['marks'],
                obtained_marks=obtained,
                similarity_score=round(similarity, 3),
                coverage_score=round(coverage, 3),
                feedback=feedback
            ))
            total_obtained += obtained
        
        percentage = (total_obtained / total_marks) * 100 if total_marks > 0 else 0
        grade = determine_grade(percentage)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Evaluation complete: {total_obtained}/{total_marks} ({percentage:.1f}%) - Grade: {grade}")
        
        return PDFEvalResult(
            student_name=student_name or "Anonymous",
            exam_name=exam_name,
            total_max_marks=total_marks,
            total_obtained_marks=round(total_obtained, 2),
            percentage=round(percentage, 2),
            grade=grade,
            questions_results=results,
            evaluation_timestamp=datetime.now().isoformat(),
            processing_time=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF evaluation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")

@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    }