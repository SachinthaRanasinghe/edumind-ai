"""
Script to create sample data for testing EduMind AI platform.
Run: python manage.py shell < create_sample_data.py
Or: python manage.py shell
     >>> exec(open('create_sample_data.py').read())
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User, Student, Teacher
from learning.models import Course, Topic, Assessment, Question
from datetime import datetime, timedelta
from django.utils import timezone

print("🚀 Creating sample data for EduMind AI...")

# Create sample teachers
print("\n📚 Creating teachers...")
teachers_data = [
    {"email": "prof.smith@edumind.ai", "first_name": "John", "last_name": "Smith", "employee_id": "TEACH001", "department": "Computer Science"},
    {"email": "prof.johnson@edumind.ai", "first_name": "Sarah", "last_name": "Johnson", "employee_id": "TEACH002", "department": "Mathematics"},
]

teachers = []
for data in teachers_data:
    user, created = User.objects.get_or_create(
        email=data["email"],
        defaults={
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "user_type": "teacher",
            "is_active": True,
        }
    )
    if created:
        user.set_password("teacher123")
        user.save()
        print(f"  ✅ Created user: {user.email}")
    
    teacher, created = Teacher.objects.get_or_create(
        user=user,
        defaults={
            "employee_id": data["employee_id"],
            "department": data["department"],
            "specialization": ["Programming", "Algorithms"] if data["department"] == "Computer Science" else ["Algebra", "Calculus"]
        }
    )
    teachers.append(teacher)
    if created:
        print(f"  ✅ Created teacher: {teacher}")

# Create sample students
print("\n🎓 Creating students...")
students_data = [
    {"email": "alice@student.edu", "first_name": "Alice", "last_name": "Brown", "student_id": "STU001", "grade_level": 10},
    {"email": "bob@student.edu", "first_name": "Bob", "last_name": "Wilson", "student_id": "STU002", "grade_level": 10},
    {"email": "charlie@student.edu", "first_name": "Charlie", "last_name": "Davis", "student_id": "STU003", "grade_level": 11},
    {"email": "diana@student.edu", "first_name": "Diana", "last_name": "Martinez", "student_id": "STU004", "grade_level": 11},
]

students = []
for data in students_data:
    user, created = User.objects.get_or_create(
        email=data["email"],
        defaults={
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "user_type": "student",
            "is_active": True,
        }
    )
    if created:
        user.set_password("student123")
        user.save()
        print(f"  ✅ Created user: {user.email}")
    
    student, created = Student.objects.get_or_create(
        user=user,
        defaults={
            "student_id": data["student_id"],
            "grade_level": data["grade_level"],
            "learning_style": "visual",
        }
    )
    students.append(student)
    if created:
        print(f"  ✅ Created student: {student}")

# Create sample courses
print("\n📖 Creating courses...")
courses_data = [
    {
        "course_code": "CS101",
        "title": "Introduction to Python Programming",
        "description": "Learn the basics of Python programming language",
        "subject": "Computer Science",
        "grade_level": 10,
        "teacher": teachers[0],
    },
    {
        "course_code": "MATH201",
        "title": "Algebra Fundamentals",
        "description": "Master algebraic concepts and problem-solving",
        "subject": "Mathematics",
        "grade_level": 10,
        "teacher": teachers[1],
    },
]

courses = []
for data in courses_data:
    course, created = Course.objects.get_or_create(
        course_code=data["course_code"],
        defaults=data
    )
    courses.append(course)
    if created:
        print(f"  ✅ Created course: {course}")

# Create topics for Python course
print("\n📝 Creating topics...")
python_topics = [
    {
        "title": "Variables and Data Types",
        "description": "Understanding variables, integers, strings, and basic data types",
        "order_index": 1,
        "difficulty_level": "beginner",
        "estimated_duration": 30,
    },
    {
        "title": "Control Structures",
        "description": "If statements, loops, and conditional logic",
        "order_index": 2,
        "difficulty_level": "beginner",
        "estimated_duration": 45,
    },
    {
        "title": "Functions and Modules",
        "description": "Creating reusable code with functions",
        "order_index": 3,
        "difficulty_level": "intermediate",
        "estimated_duration": 60,
    },
]

topics = []
for topic_data in python_topics:
    topic, created = Topic.objects.get_or_create(
        course=courses[0],
        title=topic_data["title"],
        defaults={**topic_data, "course": courses[0]}
    )
    topics.append(topic)
    if created:
        print(f"  ✅ Created topic: {topic.title}")

# Create a sample assessment
print("\n✍️ Creating assessments...")
assessment, created = Assessment.objects.get_or_create(
    course=courses[0],
    title="Python Basics Quiz",
    defaults={
        "description": "Test your knowledge of Python fundamentals",
        "assessment_type": "quiz",
        "total_points": 100,
        "passing_score": 70,
        "is_adaptive": True,
        "time_limit": 30,
        "created_by": teachers[0],
        "topic": topics[0],
    }
)
if created:
    print(f"  ✅ Created assessment: {assessment}")

# Create sample questions
print("\n❓ Creating questions...")
questions_data = [
    {
        "question_type": "multiple_choice",
        "question_text": "What is the correct way to create a variable in Python?",
        "question_data": {
            "options": [
                "var x = 5",
                "x = 5",
                "int x = 5",
                "x := 5"
            ],
            "correct_answer": "x = 5",
            "explanation": "In Python, you simply assign a value to a variable name without declaring its type."
        },
        "points": 10,
        "difficulty_level": "easy",
        "topic_tags": [str(topics[0].id)],
    },
    {
        "question_type": "multiple_choice",
        "question_text": "Which of the following is NOT a valid Python data type?",
        "question_data": {
            "options": [
                "int",
                "string",
                "boolean",
                "char"
            ],
            "correct_answer": "char",
            "explanation": "Python uses 'str' for strings, not 'char'. There is no char data type in Python."
        },
        "points": 10,
        "difficulty_level": "medium",
        "topic_tags": [str(topics[0].id)],
    },
    {
        "question_type": "true_false",
        "question_text": "Python is a case-sensitive language.",
        "question_data": {
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Python is case-sensitive, meaning 'Variable' and 'variable' are different identifiers."
        },
        "points": 10,
        "difficulty_level": "easy",
        "topic_tags": [str(topics[0].id)],
    },
]

for i, q_data in enumerate(questions_data, 1):
    question, created = Question.objects.get_or_create(
        assessment=assessment,
        question_text=q_data["question_text"],
        defaults={**q_data, "assessment": assessment, "order_index": i}
    )
    if created:
        print(f"  ✅ Created question: {question.question_text[:50]}...")

print("\n" + "="*70)
print("✨ Sample data creation complete!")
print("="*70)

print("\n📊 Summary:")
print(f"  Teachers created: {len(teachers)}")
print(f"  Students created: {len(students)}")
print(f"  Courses created: {len(courses)}")
print(f"  Topics created: {len(topics)}")
print(f"  Questions created: {len(questions_data)}")

print("\n🔑 Login Credentials:")
print("\n  Admin:")
print("    Email: admin@edumind.ai")
print("    Password: admin123")

print("\n  Teachers:")
for t_data in teachers_data:
    print(f"    Email: {t_data['email']}")
    print(f"    Password: teacher123")

print("\n  Students:")
for s_data in students_data:
    print(f"    Email: {s_data['email']}")
    print(f"    Password: student123")

print("\n🎯 Next Steps:")
print("  1. Start the backend: python manage.py runserver")
print("  2. Start the frontend: cd ../frontend && npm run dev")
print("  3. Visit: http://localhost:3000")
print("  4. Login with any of the credentials above!")

print("\n✅ All done! Happy testing! 🚀\n")
