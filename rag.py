# rag.py

import os
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pypdf import PdfReader
from google import genai


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
POLICY_DIR = BASE_DIR / "policy"


# =========================================================
# GEMINI
# =========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


def get_client():

    if not API_KEY:
        return None

    try:
        return genai.Client(
            api_key=API_KEY
        )

    except Exception:
        return None


# =========================================================
# TEXT HELPERS
# =========================================================

def clean_text(text):

    if pd.isna(text):
        return ""

    return str(text).strip()


def normalize(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# LOAD CSV FILES
# =========================================================

def load_csv(filename):

    path = DATA_DIR / filename

    if not path.exists():
        return None

    try:
        return pd.read_csv(path)

    except Exception as error:

        print(
            f"Error reading {filename}: {error}"
        )

        return None


# =========================================================
# FORMAT DATAFRAME
# =========================================================

def dataframe_to_documents(
    dataframe,
    source
):

    documents = []

    if dataframe is None:
        return documents

    for _, row in dataframe.iterrows():

        parts = []

        for column in dataframe.columns:

            value = clean_text(
                row[column]
            )

            if value:

                parts.append(
                    f"{column}: {value}"
                )

        if parts:

            documents.append({
                "source": source,
                "text": " | ".join(parts)
            })

    return documents


# =========================================================
# LOAD PDF
# =========================================================

def load_policy():

    documents = []

    if not POLICY_DIR.exists():
        return documents

    pdf_files = list(
        POLICY_DIR.glob("*.pdf")
    )

    for pdf_file in pdf_files:

        try:

            reader = PdfReader(
                str(pdf_file)
            )

            for page_number, page in enumerate(
                reader.pages,
                start=1
            ):

                text = page.extract_text()

                if not text:
                    continue

                text = clean_text(text)

                if text:

                    documents.append({
                        "source": (
                            f"{pdf_file.name} "
                            f"- Page {page_number}"
                        ),
                        "text": text
                    })

        except Exception as error:

            print(
                f"PDF error: {error}"
            )

    return documents


# =========================================================
# INTENT DETECTION
# =========================================================

def detect_intent(question):

    q = normalize(question)

    # -----------------------------------------------------
    # ALL DOCTORS
    # -----------------------------------------------------

    if (
        "doctor list" in q
        or "doctors list" in q
        or "list doctors" in q
        or "list of doctors" in q
        or "all doctors" in q
        or "show doctors" in q
        or "show all doctors" in q
        or "doctors available" in q
        or q == "doctors"
        or q == "doctor"
    ):

        return "all_doctors"


    # -----------------------------------------------------
    # ALL DEPARTMENTS
    # -----------------------------------------------------

    if (
        "department list" in q
        or "departments list" in q
        or "list departments" in q
        or "list of departments" in q
        or "all departments" in q
        or "show departments" in q
        or q == "departments"
        or q == "department"
    ):

        return "all_departments"


    # -----------------------------------------------------
    # CONTACTS
    # -----------------------------------------------------

    if (
        "contact list" in q
        or "contacts list" in q
        or "list contacts" in q
        or "all contacts" in q
        or "contact numbers" in q
        or "phone numbers" in q
    ):

        return "all_contacts"


    # -----------------------------------------------------
    # DOCTOR SCHEDULE
    # -----------------------------------------------------

    if (
        "schedule" in q
        or "timing" in q
        or "timings" in q
        or "availability" in q
    ):

        return "doctor_schedule"


    # -----------------------------------------------------
    # POLICY
    # -----------------------------------------------------

    if (
        "policy" in q
        or "policies" in q
        or "rules" in q
        or "visiting hours" in q
        or "appointment rules" in q
    ):

        return "policy"


    # -----------------------------------------------------
    # GENERAL
    # -----------------------------------------------------

    return "general"


# =========================================================
# STRUCTURED RETRIEVAL
# =========================================================

def structured_retrieval(question):

    intent = detect_intent(
        question
    )

    documents = []


    # =====================================================
    # ALL DOCTORS
    # =====================================================

    if intent == "all_doctors":

        df = load_csv(
            "doctors.csv"
        )

        documents = dataframe_to_documents(
            df,
            "doctors.csv"
        )

        return documents


    # =====================================================
    # ALL DEPARTMENTS
    # =====================================================

    if intent == "all_departments":

        df = load_csv(
            "departments.csv"
        )

        documents = dataframe_to_documents(
            df,
            "departments.csv"
        )

        return documents


    # =====================================================
    # ALL CONTACTS
    # =====================================================

    if intent == "all_contacts":

        df = load_csv(
            "contacts.csv"
        )

        documents = dataframe_to_documents(
            df,
            "contacts.csv"
        )

        return documents


    # =====================================================
    # DOCTOR SCHEDULE
    # =====================================================

    if intent == "doctor_schedule":

        schedule_df = load_csv(
            "doctor_schedule.csv"
        )

        doctors_df = load_csv(
            "doctors.csv"
        )

        question_normalized = normalize(
            question
        )

        selected_rows = []

        if schedule_df is not None:

            for _, row in schedule_df.iterrows():

                doctor_name = normalize(
                    row.get(
                        "Doctor_Name",
                        ""
                    )
                )

                department = normalize(
                    row.get(
                        "Department",
                        ""
                    )
                )

                if (
                    doctor_name
                    and doctor_name in question_normalized
                ):

                    selected_rows.append(row)

                elif (
                    department
                    and department in question_normalized
                ):

                    selected_rows.append(row)

        if selected_rows:

            selected_df = pd.DataFrame(
                selected_rows
            )

            return dataframe_to_documents(
                selected_df,
                "doctor_schedule.csv"
            )

        return dataframe_to_documents(
            schedule_df,
            "doctor_schedule.csv"
        )


    # =====================================================
    # POLICY
    # =====================================================

    if intent == "policy":

        return load_policy()


    # =====================================================
    # GENERAL SEARCH
    # =====================================================

    all_documents = []

    csv_files = [
        "hospital_info.csv",
        "departments.csv",
        "doctors.csv",
        "doctor_schedule.csv",
        "contacts.csv"
    ]

    for filename in csv_files:

        df = load_csv(filename)

        all_documents.extend(
            dataframe_to_documents(
                df,
                filename
            )
        )

    all_documents.extend(
        load_policy()
    )

    question_words = set(
        normalize(question).split()
    )

    scored = []

    for document in all_documents:

        document_words = set(
            normalize(
                document["text"]
            ).split()
        )

        score = len(
            question_words
            & document_words
        )

        if score > 0:

            scored.append(
                (
                    score,
                    document
                )
            )

    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        document
        for score, document in scored[:8]
    ]


# =========================================================
# GEMINI
# =========================================================

def generate_answer(
    question,
    documents
):

    if not documents:

        return (
            "I couldn't find this information "
            "in the available VinCare Hospital data."
        )

    context_parts = []

    for document in documents:

        context_parts.append(
            f"SOURCE: {document['source']}\n"
            f"{document['text']}"
        )

    context = "\n\n".join(
        context_parts
    )


    client = get_client()

    if client is None:

        return (
            "I found the relevant hospital information, "
            "but the Gemini API is not configured correctly. "
            "Please check your GEMINI_API_KEY."
        )


    prompt = f"""
You are VinCare Hospital Information Assistant.

Answer the user's question using ONLY the hospital
information provided below.

IMPORTANT RULES:

1. Never invent information.
2. Never remove important information from a list.
3. If the user asks for a list, provide the complete
   list available in the provided context.
4. If the user asks for doctors, use the doctors data.
5. If the user asks for departments, use the departments data.
6. If the user asks for schedules, use the schedule data.
7. If the user asks for contacts, use the contacts data.
8. If information is not available, say so.
9. Do not diagnose medical conditions.
10. Do not prescribe medicines.
11. Do not recommend treatments.
12. Do not interpret medical tests.
13. Keep the answer clear and concise.

USER QUESTION:

{question}

HOSPITAL INFORMATION:

{context}

ANSWER:
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if response.text:

            return response.text.strip()

        return (
            "I could not generate the answer."
        )

    except Exception as error:

        return (
            "I found the relevant hospital information, "
            "but there was a problem generating the response.\n\n"
            f"Error: {error}"
        )


# =========================================================
# MAIN FUNCTION
# =========================================================

def answer_question(question):

    documents = structured_retrieval(
        question
    )

    answer = generate_answer(
        question,
        documents
    )

    sources = list(
        dict.fromkeys(
            document["source"]
            for document in documents
        )
    )

    return answer, sources