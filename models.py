"""
models.py
Object-Oriented Programming component for Sir Osmani Academy.

Implements the required "Class Properties Blueprint":
    Properties : Name, ID, Category, Status
    Methods    : Add, Search, Update, Delete, Display

Here the blueprint is applied to Courses offered by the academy
(e.g. "O Level Physics", "Spoken English"), which are stored
persistently in courses.json. If GitHub secrets are configured, data
is saved directly to the GitHub repo so it survives app restarts.
"""

from utils import load_json, save_json
from github_store import is_github_storage_enabled, load_json_from_github, save_json_to_github


class Course:
    """
    Represents a single course/tuition offering.

    Properties:
        name     -> Name of the course
        course_id -> Unique ID
        category -> e.g. "O Level", "Matric", "Spoken English"
        status   -> "Active" or "Inactive"
    """

    def __init__(self, name, course_id, category, status="Active"):
        self.name = name
        self.course_id = course_id
        self.category = category
        self.status = status

    def to_dict(self):
        return {
            "name": self.name,
            "course_id": self.course_id,
            "category": self.category,
            "status": self.status,
        }

    @staticmethod
    def from_dict(data):
        return Course(
            name=data.get("name"),
            course_id=data.get("course_id"),
            category=data.get("category"),
            status=data.get("status", "Active"),
        )

    def __repr__(self):
        return f"Course({self.course_id}, {self.name}, {self.category}, {self.status})"


class CourseManager:
    """
    Manages a collection of Course objects with full CRUD support.
    Data is persisted to a JSON file (locally or on GitHub) so it
    survives app restarts.
    """

    def __init__(self, file_path="courses.json"):
        self.file_path = file_path
        self.courses = []
        self.load_data()

    # -- persistence ------------------------------------------------------

    def load_data(self):
        if is_github_storage_enabled():
            raw = load_json_from_github(self.file_path)
        else:
            raw = load_json(self.file_path)
        items = raw.get("courses", []) if isinstance(raw, dict) else []
        self.courses = [Course.from_dict(item) for item in items]

    def save_data(self):
        data = {"courses": [c.to_dict() for c in self.courses]}
        if is_github_storage_enabled():
            return save_json_to_github(self.file_path, data, commit_message="Update courses.json via app")
        return save_json(self.file_path, data)

    # -- CRUD methods -------------------------------------------------------

    def add(self, name, course_id, category, status="Active"):
        """Add a new course. Returns (success, message)."""
        if self.search(course_id) is not None:
            return False, f"Course ID '{course_id}' already exists."
        course = Course(name, course_id, category, status)
        self.courses.append(course)
        self.save_data()
        return True, f"Course '{name}' added successfully."

    def search(self, course_id):
        """Search for a course by ID. Returns Course object or None."""
        for course in self.courses:
            if course.course_id == course_id:
                return course
        return None

    def update(self, course_id, name=None, category=None, status=None):
        """Update fields of an existing course. Returns (success, message)."""
        course = self.search(course_id)
        if course is None:
            return False, f"Course ID '{course_id}' not found."
        if name:
            course.name = name
        if category:
            course.category = category
        if status:
            course.status = status
        self.save_data()
        return True, f"Course '{course_id}' updated successfully."

    def delete(self, course_id):
        """Delete a course by ID. Returns (success, message)."""
        course = self.search(course_id)
        if course is None:
            return False, f"Course ID '{course_id}' not found."
        self.courses.remove(course)
        self.save_data()
        return True, f"Course '{course_id}' deleted successfully."

    def display(self):
        """Return a list of dicts for all courses (used to build tables)."""
        return [c.to_dict() for c in self.courses]
