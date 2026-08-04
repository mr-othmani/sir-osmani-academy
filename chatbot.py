"""
chatbot.py
Customer Support Bot for Sir Osmani Academy (Online Tuition).

This chatbot answers Frequently Asked Questions using a JSON knowledge
base (faq.json). It does NOT take orders - its purpose is to give
students/parents information about courses, fees, timings, teachers,
contact details, enrollment and services.

Meaningful queries are classified and logged to query_log.csv.
Simple greetings (Hi, Hello, Thanks, Bye, etc.) are answered but
never logged, as required by the project spec.
"""

from utils import (
    load_json,
    validate_input,
    is_greeting,
    classify_query,
    append_csv_row,
    get_current_date,
    get_current_time,
)

FAQ_FILE = "faq.json"
LOG_FILE = "query_log.csv"
LOG_HEADERS = ["Date", "Time", "Query", "Category"]

FALLBACK_MESSAGE = "Sorry, I couldn't find information related to your question. " \
                    "You can also reach us directly via WhatsApp or email."

GREETING_RESPONSE = "Hello! Welcome to Sir Osmani Academy 👋 How can I help you today? " \
                     "You can ask me about courses, fees, timings, teachers, or enrollment."

THANKS_RESPONSE = "You're most welcome! Feel free to ask if you have any more questions. 😊"

BYE_RESPONSE = "Thank you for visiting Sir Osmani Academy. Have a great day! 👋"


class SirOsmaniChatbot:
    """
    Encapsulates chatbot behaviour: loading knowledge, matching intent,
    generating a response, and logging meaningful queries.
    """

    def __init__(self, faq_file=FAQ_FILE, log_file=LOG_FILE):
        self.faq_file = faq_file
        self.log_file = log_file
        self.knowledge_base = load_json(self.faq_file)

    # -- intent matching ---------------------------------------------------

    def _match_answer(self, text):
        """
        Search the JSON knowledge base for the best matching answer
        based on simple keyword lookups within each topic section.
        Returns the answer string, or None if nothing matches.
        """
        lowered = text.lower()
        kb = self.knowledge_base

        # Course related
        if any(k in lowered for k in ["matric"]):
            return kb.get("courses", {}).get("matric")
        if any(k in lowered for k in ["o level", "o-level", "olevel"]):
            return kb.get("courses", {}).get("o_level")
        if any(k in lowered for k in ["a level", "a-level", "alevel"]):
            return kb.get("courses", {}).get("a_level")
        if "spoken" in lowered or "english course" in lowered:
            return kb.get("courses", {}).get("spoken_english")
        if any(k in lowered for k in ["python", "programming", "coding", "web development"]):
            return kb.get("courses", {}).get("programming")
        if any(k in lowered for k in ["course", "subject", "class do you", "classes do you offer"]):
            return kb.get("courses", {}).get("general")

        # Contact
        if "whatsapp" in lowered:
            return f"You can reach us on WhatsApp at {kb.get('contact', {}).get('whatsapp')}"
        if "email" in lowered:
            return f"You can email us at {kb.get('contact', {}).get('email')}"
        if any(k in lowered for k in ["phone", "number", "contact", "call"]):
            return f"You can contact us at {kb.get('contact', {}).get('phone')} or email {kb.get('contact', {}).get('email')}"

        # Timings
        if "weekend" in lowered:
            return kb.get("class_timings", {}).get("weekend")
        if any(k in lowered for k in ["timing", "time", "schedule", "hours", "when"]):
            return kb.get("class_timings", {}).get("weekday")

        # Teachers
        if "demo" in lowered or "trial" in lowered:
            return kb.get("teachers", {}).get("demo")
        if any(k in lowered for k in ["teacher", "tutor", "instructor", "faculty"]):
            return kb.get("teachers", {}).get("general")

        # Fees / Payment
        if "discount" in lowered:
            return kb.get("fees", {}).get("discount")
        if any(k in lowered for k in ["payment method", "how can i pay", "pay via", "jazzcash", "easypaisa", "bank"]):
            return kb.get("fees", {}).get("payment_methods")
        if any(k in lowered for k in ["fee", "fees", "price", "cost", "charges"]):
            return kb.get("fees", {}).get("general")

        # Location
        if any(k in lowered for k in ["location", "address", "where", "campus"]):
            return kb.get("location", {}).get("general")

        # Enrollment
        if any(k in lowered for k in ["enroll", "admission", "register", "join", "sign up", "apply"]):
            return kb.get("enrollment", {}).get("general")

        # Services
        if any(k in lowered for k in ["service", "recorded", "quiz", "report", "homework"]):
            return kb.get("services", {}).get("general")

        return None

    # -- public API ----------------------------------------------------------

    def get_response(self, user_text):
        """
        Main entry point: takes raw user text, returns (response, category, logged: bool)
        """
        if not validate_input(user_text):
            return "Please type a question so I can help you.", "Other", False

        text = user_text.strip()

        # Handle greetings / courtesy messages without logging
        lowered = text.lower().strip("!.,")
        if is_greeting(text):
            if lowered in {"thank you", "thanks"}:
                return THANKS_RESPONSE, "Greeting", False
            if lowered in {"bye", "goodbye"}:
                return BYE_RESPONSE, "Greeting", False
            return GREETING_RESPONSE, "Greeting", False

        # Look up an answer
        answer = self._match_answer(text)
        category = classify_query(text)

        if answer is None:
            answer = FALLBACK_MESSAGE

        # Log meaningful query
        self._log_query(text, category)

        return answer, category, True

    def _log_query(self, text, category):
        row = [get_current_date(), get_current_time(), text, category]
        append_csv_row(self.log_file, row, headers=LOG_HEADERS)
