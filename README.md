# VinCare Hospital Information Assistant

A lightweight RAG-based hospital information assistant.

## Tech Stack

- Python
- Streamlit
- Gemini API
- Pandas
- PyPDF
- CSV
- Simple keyword retrieval

## Features

The assistant can provide information about:

- Hospital details
- Departments
- Doctors
- Doctor specializations
- Doctor rooms
- Doctor schedules
- Hospital contacts
- Appointment information
- Hospital policies

## Safety

The assistant does not provide:

- Medical diagnosis
- Medication recommendations
- Prescriptions
- Treatment recommendations
- Medical test interpretation

## Architecture

User
↓
Streamlit
↓
Safety Check
↓
Simple Retrieval
↓
CSV + PDF
↓
Relevant Context
↓
Gemini
↓
Grounded Answer

## Run

Create `.env`:

GEMINI_API_KEY=your_api_key

Install dependencies:

```bash
pip install -r requirements.txt