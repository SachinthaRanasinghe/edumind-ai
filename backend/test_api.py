#!/usr/bin/env python
"""
EduMind AI - Phase 1 API Testing Script
Tests all major API endpoints
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_authentication():
    print_section("TEST 1: Authentication")
    
    # Login as student
    payload = {
        "email": "alice@student.edu",
        "password": "student123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/token/", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"   Access Token: {data['access'][:50]}...")
        return data['access']
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_courses(token):
    print_section("TEST 2: Fetch Courses")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/learning/courses/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Handle paginated response
        if isinstance(data, dict) and 'results' in data:
            courses = data['results']
        else:
            courses = data
            
        print(f"✅ Found {len(courses)} courses")
        for course in courses:
            print(f"   - {course['course_code']}: {course['title']}")
        return courses
    else:
        print(f"❌ Failed to fetch courses: {response.status_code}")
        return []

def test_quiz_generation(token, course_id):
    print_section("TEST 3: AI Quiz Generation")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "topic": "Python Basics",
        "difficulty": "medium",
        "num_questions": 3
    }
    
    response = requests.post(
        f"{BASE_URL}/learning/courses/{course_id}/generate_quiz/",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        quiz = response.json()
        print("✅ Quiz generated successfully!")
        print(f"   Questions: {len(quiz.get('questions', []))}")
        return quiz
    else:
        print(f"❌ Quiz generation failed: {response.status_code}")
        print(response.text)
        return None

def test_ai_tutor(token):
    print_section("TEST 4: AI Tutor Chat")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "message": "What is a variable in Python?",
        "context": "Python programming basics"
    }
    
    response = requests.post(
        f"{BASE_URL}/ai/tutor/chat/",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        tutor_response = response.json()
        print("✅ AI Tutor responded!")
        print(f"   Response: {tutor_response.get('response', '')[:100]}...")
        return tutor_response
    else:
        print(f"❌ AI Tutor failed: {response.status_code}")
        print(response.text)
        return None

def test_student_progress(token):
    print_section("TEST 5: Student Progress")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/learning/progress/", headers=headers)
    
    if response.status_code == 200:
        progress = response.json()
        print("✅ Progress data retrieved!")
        print(f"   Data: {json.dumps(progress, indent=2)[:200]}...")
        return progress
    else:
        print(f"❌ Failed to get progress: {response.status_code}")
        return None

def main():
    print("\n" + "🚀" * 30)
    print("   EDUMIND AI - PHASE 1 API TESTING")
    print("🚀" * 30)
    
    # Test 1: Authentication
    token = test_authentication()
    if not token:
        print("\n❌ Tests aborted - Authentication failed")
        return
    
    # Test 2: Courses
    courses = test_courses(token)
    
    # Test 3: Quiz Generation (if courses exist)
    if courses and len(courses) > 0:
        test_quiz_generation(token, courses[0]['id'])
    
    # Test 4: AI Tutor
    test_ai_tutor(token)
    
    # Test 5: Student Progress
    test_student_progress(token)
    
    print("\n" + "="*60)
    print("  TESTING COMPLETE!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server!")
        print("   Make sure the backend is running on http://localhost:8000")
        print("   Run: cd backend && source venv/bin/activate && python manage.py runserver")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
