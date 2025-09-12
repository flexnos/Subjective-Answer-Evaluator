import streamlit as st
import requests
from streamlit_lottie import st_lottie
import json
import time

# ----------------- CSS -----------------
def local_css():
    st.markdown(
        """
        <style>
        button[kind="primary"]:hover {
            background: linear-gradient(90deg, #a565f8, #7b4cff) !important;
            box-shadow: 0 8px 20px rgba(165, 101, 248, 0.9);
            transform: scale(1.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        textarea:hover, input[type="text"]:hover, input[type="email"]:hover {
            border-color: #b087ff !important;
            box-shadow: 0 0 8px 2px rgba(123, 76, 255, 0.6);
            transition: box-shadow 0.3s ease, border-color 0.3s ease;
        }
        .stApp {
            background: linear-gradient(135deg, #121212, #2c003e);
            color: #d3c0ff;
            min-height: 100vh;
            padding: 1rem 2rem;
        }
        textarea, .stTextArea>div>textarea {
            background-color: #1e1e1e !important;
            border: 2px solid #7b4cff !important;
            border-radius: 8px !important;
            color: #d3c0ff !important;
            font-weight: 600;
        }
        input[type="text"], input[type="email"], .stTextInput>div>input {
            background-color: #1e1e1e !important;
            border: 2px solid #7b4cff !important;
            border-radius: 8px !important;
            color: #d3c0ff !important;
            font-weight: 600;
        }
        button[kind="primary"] {
            background: linear-gradient(90deg, #7b4cff, #a565f8) !important;
            color: white !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            padding: 10px 18px !important;
            box-shadow: 0 4px 10px rgba(123, 76, 255, 0.8);
            transition: background 0.3s ease;
        }
        button[kind="primary"]:hover {
            background: linear-gradient(90deg, #a565f8, #7b4cff) !important;
            box-shadow: 0 6px 12px rgba(165, 101, 248, 1);
        }
        [data-testid="stSidebar"] {
            background: #2c003e;
            color: #d3c0ff;
        }
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #121212;
        }
        ::-webkit-scrollbar-thumb {
            background: #7b4cff;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

local_css()

# ----------------- Lottie -----------------
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_eval = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_w51pcehl.json")

st.set_page_config(page_title="📘 Advanced Answer Evaluator", page_icon="📘", layout="centered",
                   initial_sidebar_state="expanded")

# ----------------- Sidebar -----------------
st.sidebar.title("⚙️ Evaluation Settings")

eval_mode = st.sidebar.radio("Choose Evaluation Mode", ("Basic", "Advanced (Embedding + Grammar + Keywords)", "CNN-Based Deep Eval"))

backend_url_default = "http://127.0.0.1:8000"
backend_url = st.sidebar.text_input("Backend API URL", backend_url_default)

show_examples = st.sidebar.checkbox("Show Example Inputs", value=True)

with st.sidebar.expander("Score Weight Adjustments (Advanced Mode)"):
    sim_weight = st.slider("Embedding Similarity Weight", 0.0, 1.0, 0.5, 0.05)
    cov_weight = st.slider("Keyword Coverage Weight", 0.0, 1.0, 0.3, 0.05)
    gram_weight = st.slider("Grammar Score Weight", 0.0, 1.0, 0.2, 0.05)
    total_weight = sim_weight + cov_weight + gram_weight
    if total_weight != 1:
        st.warning(f"Total weights sum to {total_weight:.2f}, ideally should be 1. Adjust accordingly.")

# ----------------- Title -----------------
st.title("📘 Advanced & Interactive Subjective Answer Evaluator")
if lottie_eval:
    st_lottie(lottie_eval, height=150, key="eval_anim")

# ----------------- Example -----------------
if show_examples:
    st.markdown("##### Example:")
    st.markdown("> Question: What is photosynthesis?")
    st.markdown("> Reference Answer: Photosynthesis is the process by which green plants produce food using sunlight.")
    st.markdown("> Student Answer: It is how plants make their own food using the energy from sunlight.")

# ----------------- Form -----------------
with st.form("eval_form", clear_on_submit=False):
    question = st.text_area("Enter Question", height=80)
    ref_answer = st.text_area("Enter Model Answer (Reference)", height=120)
    student_answer = st.text_area("Enter Student's Answer", height=120)

    with st.expander("Advanced Options"):
        model_choice = st.selectbox("Select Embedding Model (if applicable)", ["MiniLM", "all-MPNet-base-v2", "BERT-base"])
        batch_mode = st.checkbox("Batch mode: Upload CSV with multiple student answers")

    submit = st.form_submit_button("Evaluate Answer")

if submit:
    if not question or not ref_answer or not student_answer:
        st.error("Please fill in all mandatory fields.")
    else:
        with st.spinner("Evaluating answer ..."):
            payload = {
                "question": question,
                "model_answer": ref_answer,
                "student_answer": student_answer,
            }

            if eval_mode == "Basic":
                url = backend_url + "/evaluate"
            elif eval_mode == "Advanced (Embedding + Grammar + Keywords)":
                url = backend_url + "/evaluate_advanced"
            else:
                url = backend_url + "/evaluate_cnn"

            try:
                response = requests.post(url, json=payload, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    progress_bar = st.progress(0)
                    score_val = result.get("final_score") or result.get("score") or 0
                    for percent in range(0, int(score_val * 10) + 1, 5):
                        progress_bar.progress(min(percent, 100))
                        time.sleep(0.05)

                    st.success(f"Final Score: {score_val} / 10")
                    st.markdown("### Detailed Evaluation Breakdown")
                    for key, val in result.items():
                        if key not in ["question", "student_answer", "final_score", "score", "feedback"]:
                            st.write(f"**{key.replace('_', ' ').title()}** : {val}")
                    feedback = result.get("feedback", "No feedback provided.")
                    st.info(f"**Feedback:** {feedback}")
                else:
                    st.error(f"Error from API: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Failed to evaluate answer: {e}")

# ----------------- Image Upload Section -----------------
st.markdown("---")
st.markdown("### 📷 Evaluate Answer from Image")

uploaded_file = st.file_uploader("Upload Student Answer Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Answer", use_column_width=True)

    if st.button("Evaluate Image Answer"):
        with st.spinner("Extracting text and evaluating..."):
            try:
                data = {"question": question, "model_answer": ref_answer}
                response = requests.post(
                    backend_url + "/evaluate_image",
                    files={"file": uploaded_file.getvalue()},
                    data=data
                )

                if response.status_code == 200:
                    result = response.json()

                    extracted = result.get("extracted_answer", "")
                    if extracted:
                        st.markdown("#### 📝 Extracted Text from Image")
                        st.info(extracted)

                    score_val = result.get("score", 0)
                    score_progress = st.progress(0)
                    for percent in range(0, int(score_val * 10) + 1, 5):
                        score_progress.progress(min(percent, 100))
                        time.sleep(0.05)

                    st.success(f"Image Answer Score: {score_val} / 10")
                    feedback = result.get("feedback", "No feedback provided.")
                    st.info(f"**Feedback:** {feedback}")

                else:
                    st.error(f"Error from API: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Failed to evaluate image answer: {e}")

# ----------------- Extra Widgets -----------------
st.markdown("---")
st.markdown("### Interactive Learning Hub")
col1, col2 = st.columns(2)
with col1:
    if st.button("Show Tips for Writing Better Answers"):
        st.write("""
            - Understand the question carefully.
            - Use relevant keywords from the model answer.
            - Write clear and concise sentences.
            - Check spelling and grammar.
            - Provide examples or explanations where relevant.
        """)
with col2:
    excitement = st.slider("Your Confidence Level in Your Answer", 0, 10, 5)
    st.write(f"Confidence Level: {excitement}/10")

st.markdown("#### Real-Time Answer Progress")
progress = st.progress(0)
for i in range(100):
    time.sleep(0.01)
    progress.progress(i + 1)
