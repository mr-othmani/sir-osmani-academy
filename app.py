"""
app.py
Streamlit application for Sir Osmani Academy - Online Tuition Chatbot.

Pages:
    - Home              : Introduction to the academy
    - Chatbot            : Customer Support Bot (FAQ chatbot)
    - Course Manager     : Admin panel demonstrating OOP CRUD (Course/CourseManager)
    - Query Log          : View logged customer queries

Course Manager and Query Log are admin-only and hidden behind a password.

Run with:
    streamlit run app.py
"""

import os
import pandas as pd
import streamlit as st

from chatbot import SirOsmaniChatbot
from models import CourseManager
from utils import read_csv_rows, validate_input

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Sir Osmani Academy",
    page_icon="🎓",
    layout="wide",
)

LOGO_PATH = os.path.join("assets", "logo.png")


# ---------------------------------------------------------------------------
# CACHED RESOURCES
# ---------------------------------------------------------------------------

@st.cache_resource
def get_chatbot():
    return SirOsmaniChatbot()


@st.cache_resource
def get_course_manager():
    return CourseManager()


chatbot = get_chatbot()
course_manager = get_course_manager()

# Chat history lives in session state so it persists across reruns
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False


# ---------------------------------------------------------------------------
# ADMIN PASSWORD
# ---------------------------------------------------------------------------
# Change this password before sharing your app publicly!
ADMIN_PASSWORD = "osmani2026"


# ---------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------------------------

with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)
    st.title("🎓 Sir Osmani Academy")
    st.caption("Online Tuition Platform")

    # Pages every visitor can see
    available_pages = ["🏠 Home", "💬 Chatbot"]

    # Admin-only pages are only added to the list once logged in
    if st.session_state.is_admin:
        available_pages += ["📚 Course Manager", "📄 Query Log"]

    page = st.radio("Navigate", available_pages)

    st.divider()

    # Admin login / logout box
    if st.session_state.is_admin:
        st.success("🔓 Admin mode is ON")
        if st.button("Log out of Admin"):
            st.session_state.is_admin = False
            st.rerun()
    else:
        with st.expander("🔒 Admin Login"):
            entered_password = st.text_input("Password", type="password", key="admin_password_input")
            if st.button("Unlock Admin Pages"):
                if entered_password == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("Incorrect password.")

    st.divider()
    st.caption("Python & AI Mastery — Final Project")


# ---------------------------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------------------------

if page == "🏠 Home":
    st.title("Welcome to Sir Osmani Academy 🎓")
    st.subheader("Quality Online Tuition, Anywhere, Anytime")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            **Sir Osmani Academy** offers online tuition for:
            - Matric (Science & Arts)
            - O Level & A Level
            - Spoken English
            - Python Programming & Web Development

            Ask our chatbot anything about courses, fees, timings,
            teachers, or how to enroll!
            """
        )
        if st.button("💬 Start chatting with our Support Bot"):
            st.session_state["_redirect_hint"] = True
            st.info("Select '💬 Chatbot' from the sidebar to begin.")

    with col2:
        st.markdown("#### Why choose us?")
        st.success("✅ Qualified & experienced teachers")
        st.success("✅ Free demo class before enrollment")
        st.success("✅ Flexible weekday & weekend batches")
        st.success("✅ Recorded lectures & progress reports")

    st.divider()
    st.markdown("#### Our Courses")
    courses = course_manager.display()
    if courses:
        df = pd.DataFrame(courses)
        st.table(df)
    else:
        st.warning("No courses have been added yet. Add some in the Course Manager page.")


# ---------------------------------------------------------------------------
# CHATBOT PAGE
# ---------------------------------------------------------------------------

elif page == "💬 Chatbot":
    st.title("💬 Sir Osmani Academy — Support Chatbot")
    st.caption("Ask about courses, fees, timings, teachers, location, or enrollment.")

    example_cols = st.columns(4)
    examples = [
        "What courses do you offer?",
        "What are your fees?",
        "What are the class timings?",
        "How can I enroll?",
    ]
    clicked_example = None
    for col, ex in zip(example_cols, examples):
        with col:
            if st.button(ex):
                clicked_example = ex

    # Display existing chat history
    for sender, message in st.session_state.chat_history:
        with st.chat_message(sender):
            st.write(message)

    user_input = st.chat_input("Type your question here...")
    final_input = clicked_example or user_input

    if final_input:
        if not validate_input(final_input):
            st.error("Please enter a valid question.")
        else:
            st.session_state.chat_history.append(("user", final_input))
            with st.chat_message("user"):
                st.write(final_input)

            response, category, logged = chatbot.get_response(final_input)

            st.session_state.chat_history.append(("assistant", response))
            with st.chat_message("assistant"):
                st.write(response)
                if logged:
                    st.caption(f"📁 Logged under category: **{category}**")

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


# ---------------------------------------------------------------------------
# COURSE MANAGER PAGE (OOP CRUD DEMO) — ADMIN ONLY
# ---------------------------------------------------------------------------

elif page == "📚 Course Manager":
    st.title("📚 Course Manager")
    st.caption("Admin panel demonstrating the Course / CourseManager class (OOP Blueprint).")

    tab_add, tab_search, tab_update, tab_delete, tab_display = st.tabs(
        ["➕ Add", "🔍 Search", "✏️ Update", "🗑️ Delete", "📋 Display All"]
    )

    with tab_add:
        with st.form("add_course_form"):
            name = st.text_input("Course Name")
            course_id = st.text_input("Course ID")
            category = st.selectbox(
                "Category",
                ["Matric", "O Level", "A Level", "Spoken English", "Programming", "Other"],
            )
            status = st.selectbox("Status", ["Active", "Inactive"])
            submitted = st.form_submit_button("Add Course")

        if submitted:
            if not validate_input(name) or not validate_input(course_id):
                st.error("Course Name and Course ID are required.")
            else:
                success, msg = course_manager.add(name, course_id, category, status)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

    with tab_search:
        search_id = st.text_input("Enter Course ID to search", key="search_id")
        if st.button("Search"):
            result = course_manager.search(search_id)
            if result:
                st.success("Course found:")
                st.json(result.to_dict())
            else:
                st.error(f"No course found with ID '{search_id}'.")

    with tab_update:
        update_id = st.text_input("Course ID to update", key="update_id")
        new_name = st.text_input("New Name (optional)", key="update_name")
        new_category = st.selectbox(
            "New Category (optional)",
            ["", "Matric", "O Level", "A Level", "Spoken English", "Programming", "Other"],
            key="update_category",
        )
        new_status = st.selectbox("New Status (optional)", ["", "Active", "Inactive"], key="update_status")
        if st.button("Update Course"):
            success, msg = course_manager.update(
                update_id,
                name=new_name or None,
                category=new_category or None,
                status=new_status or None,
            )
            if success:
                st.success(msg)
            else:
                st.error(msg)

    with tab_delete:
        delete_id = st.text_input("Course ID to delete", key="delete_id")
        if st.button("Delete Course"):
            success, msg = course_manager.delete(delete_id)
            if success:
                st.success(msg)
            else:
                st.error(msg)

    with tab_display:
        courses = course_manager.display()
        if courses:
            st.dataframe(pd.DataFrame(courses), use_container_width=True)
        else:
            st.info("No courses added yet.")


# ---------------------------------------------------------------------------
# QUERY LOG PAGE — ADMIN ONLY
# ---------------------------------------------------------------------------

elif page == "📄 Query Log":
    st.title("📄 Customer Query Log")
    st.caption("Meaningful customer queries logged by the chatbot (greetings are excluded).")

    rows = read_csv_rows("query_log.csv")
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        st.divider()
        st.markdown("#### Queries by Category")
        if "Category" in df.columns:
            st.bar_chart(df["Category"].value_counts())
    else:
        st.info("No queries have been logged yet. Try the chatbot!")
