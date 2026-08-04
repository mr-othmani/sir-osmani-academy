"""
utils.py
Reusable helper functions for Sir Osmani Academy Chatbot project.
Covers: JSON handling, CSV handling, validation, datetime, and query
classification. Keeping these functions separate avoids repeated code
across chatbot.py, models.py and app.py.
"""

import json
import csv
import os
from datetime import datetime


# ---------------------------------------------------------------------------
# JSON HANDLING
# ---------------------------------------------------------------------------

def load_json(file_path):
    """
    Load and return data from a JSON file.
    Returns an empty dict if the file does not exist or is invalid.
    """
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_json(file_path, data):
    """
    Save a Python dict/list to a JSON file with nice formatting.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False


# ---------------------------------------------------------------------------
# CSV / TXT HANDLING
# ---------------------------------------------------------------------------

def ensure_csv_exists(file_path, headers):
    """
    Create a CSV file with headers if it does not already exist.
    """
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)


def append_csv_row(file_path, row, headers=None):
    """
    Append a single row (list) to a CSV file.
    Creates the file with headers first if it doesn't exist.
    """
    if headers is not None:
        ensure_csv_exists(file_path, headers)
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def read_csv_rows(file_path):
    """
    Read all rows from a CSV file and return them as a list of dicts.
    Returns an empty list if the file does not exist.
    """
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ---------------------------------------------------------------------------
# DATETIME
# ---------------------------------------------------------------------------

def get_current_date():
    return datetime.now().strftime("%d-%b-%Y")


def get_current_time():
    return datetime.now().strftime("%I:%M %p")


# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------

def validate_input(text):
    """
    Basic validation for text input.
    Returns True if the input is a non-empty, meaningful string.
    """
    if text is None:
        return False
    text = text.strip()
    if len(text) == 0:
        return False
    return True


def validate_phone(phone):
    """
    Very simple phone number validation: must contain at least 7 digits.
    """
    digits = [c for c in phone if c.isdigit()]
    return len(digits) >= 7


# ---------------------------------------------------------------------------
# GREETING / QUERY CLASSIFICATION
# ---------------------------------------------------------------------------

GREETINGS = {
    "hi", "hello", "hey", "good morning", "good evening",
    "good afternoon", "thank you", "thanks", "bye", "goodbye",
    "salam", "assalamualaikum", "asalam o alaikum"
}


def is_greeting(text):
    """
    Check whether a user message is only a greeting/courtesy message.
    Greetings are answered but never logged, per project requirements.
    """
    cleaned = text.strip().lower().strip("!.,")
    return cleaned in GREETINGS


CATEGORY_KEYWORDS = {
    "Class Timings": [
        "timing", "class timing", "schedule", "hours", "what time",
        "when do", "when does", "start time", "end time"
    ],
    "Course Information": [
        "course", "subject", "o level", "a level", "matric",
        "syllabus", "curriculum", "grade", "math", "physics", "chemistry",
        "biology", "english", "computer", "programming", "coding"
    ],
    "Contact Information": [
        "contact", "phone", "number", "email", "whatsapp", "call"
    ],
    "Teachers / Services": [
        "teacher", "tutor", "instructor", "faculty", "service", "demo",
        "trial"
    ],
    "Fees / Payment": [
        "fee", "fees", "price", "cost", "payment", "pay", "discount",
        "installment", "charges"
    ],
    "Location": [
        "location", "address", "where", "campus", "branch", "city"
    ],
    "Enrollment Policy": [
        "enroll", "admission", "register", "registration", "join",
        "sign up", "apply"
    ],
}


def classify_query(text):
    """
    Classify a user's query into a category based on keyword matching.
    Returns 'Other' if no keywords match.
    """
    lowered = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in lowered:
                return category
    return "Other"
