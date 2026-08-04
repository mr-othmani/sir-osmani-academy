# Sir Osmani Academy — Online Tuition Chatbot

Final Project for **Python & AI Mastery** (Combine Foundation).
A Streamlit web app with an FAQ chatbot for an online tuition academy.

## Features

- **Home page** — Academy intro, highlights, and a live course table.
- **Chatbot page** — Customer Support Bot that answers questions about
  courses, fees, class timings, teachers, location, and enrollment,
  reading from `faq.json`. Meaningful queries are auto-classified and
  logged to `query_log.csv`; greetings (Hi, Thanks, Bye, etc.) are
  answered but never logged.
- **Course Manager page** — Full CRUD demo (Add / Search / Update /
  Delete / Display) built on the `Course` and `CourseManager` classes,
  persisted to `courses.json`.
- **Query Log page** — Table + bar chart of all logged customer
  queries by category.

## Project Structure

```
Final_Project/
├── app.py            # Streamlit UI (all pages)
├── chatbot.py         # SirOsmaniChatbot class - FAQ matching + logging
├── models.py           # Course / CourseManager classes (OOP blueprint)
├── utils.py             # Reusable helper functions
├── faq.json              # Chatbot knowledge base
├── courses.json           # Course data (created/updated at runtime)
├── query_log.csv            # Logged customer queries (created at runtime)
├── requirements.txt
└── README.md
```

## Setup & Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## Notes for Viva

- `Course` / `CourseManager` in `models.py` implement the required
  Class Properties Blueprint: properties (Name, ID, Category, Status)
  and methods (Add, Search, Update, Delete, Display).
- `utils.py` holds all reusable functions (`load_json`, `save_json`,
  `append_csv_row`, `validate_input`, `classify_query`, etc.) so logic
  isn't duplicated across files.
- The chatbot reads all answers from `faq.json` — no hard-coded
  business data lives inside `chatbot.py` itself.
- Greeting detection uses `is_greeting()` in `utils.py`; these
  messages get a friendly reply but are intentionally excluded from
  `query_log.csv`.
