# safety.py

MEDICAL_KEYWORDS = [
    "diagnose",
    "diagnosis",
    "disease",
    "symptom",
    "symptoms",
    "medicine",
    "medication",
    "tablet",
    "drug",
    "dose",
    "dosage",
    "prescription",
    "treatment",
    "cure",
    "what should i take",
    "which medicine",
    "should i take",
    "medical advice",
    "blood pressure",
    "blood sugar",
    "blood test result",
    "test result",
    "scan result",
    "x-ray result",
    "mri result",
    "ct scan result"
]


def is_medical_question(question):
    question = question.lower().strip()

    for keyword in MEDICAL_KEYWORDS:
        if keyword in question:
            return True

    return False


def safety_response():
    return (
        "I can help with VinCare Hospital's general information, "
        "including doctors, departments, schedules, contacts, "
        "appointments, and hospital policies.\n\n"
        "However, I cannot provide diagnosis, medication advice, "
        "prescriptions, treatment recommendations, or medical-test "
        "interpretation. Please consult a qualified healthcare "
        "professional for medical advice."
    )