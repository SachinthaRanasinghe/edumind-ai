# EduMind AI - Database Schema Design

## Overview
This document outlines the complete database schema for EduMind AI platform.

## Core Tables

### 1. Users & Authentication

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('student', 'teacher', 'admin')),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    profile_picture_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_type ON users(user_type);
```

#### students
```sql
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    grade_level INTEGER,
    date_of_birth DATE,
    parent_email VARCHAR(255),
    enrollment_date DATE DEFAULT CURRENT_DATE,
    learning_style VARCHAR(50), -- visual, auditory, kinesthetic, reading/writing
    current_gpa DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_students_student_id ON students(student_id);
```

#### teachers
```sql
CREATE TABLE teachers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100),
    specialization TEXT[],
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_teachers_user_id ON teachers(user_id);
```

### 2. Courses & Content

#### courses
```sql
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_code VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(100) NOT NULL,
    grade_level INTEGER,
    teacher_id UUID REFERENCES teachers(id),
    is_active BOOLEAN DEFAULT TRUE,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_courses_teacher ON courses(teacher_id);
CREATE INDEX idx_courses_subject ON courses(subject);
```

#### course_enrollments
```sql
CREATE TABLE course_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'dropped', 'failed')),
    final_grade DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id)
);

CREATE INDEX idx_enrollments_student ON course_enrollments(student_id);
CREATE INDEX idx_enrollments_course ON course_enrollments(course_id);
```

#### topics
```sql
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,
    prerequisites TEXT[], -- Array of topic IDs
    estimated_duration INTEGER, -- in minutes
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_topics_course ON topics(course_id);
```

### 3. Assessments & Submissions

#### assessments
```sql
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES topics(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assessment_type VARCHAR(20) NOT NULL CHECK (assessment_type IN ('quiz', 'assignment', 'exam', 'essay', 'project')),
    total_points DECIMAL(6,2) NOT NULL,
    passing_score DECIMAL(6,2),
    due_date TIMESTAMP,
    is_adaptive BOOLEAN DEFAULT FALSE,
    time_limit INTEGER, -- in minutes
    created_by UUID REFERENCES teachers(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assessments_course ON assessments(course_id);
CREATE INDEX idx_assessments_type ON assessments(assessment_type);
```

#### questions
```sql
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
    question_type VARCHAR(20) NOT NULL CHECK (question_type IN ('multiple_choice', 'true_false', 'short_answer', 'essay', 'coding')),
    question_text TEXT NOT NULL,
    question_data JSONB, -- Stores options, correct answers, etc.
    points DECIMAL(6,2) NOT NULL,
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    topic_tags TEXT[],
    order_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_questions_assessment ON questions(assessment_id);
CREATE INDEX idx_questions_difficulty ON questions(difficulty_level);
```

#### submissions
```sql
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score DECIMAL(6,2),
    max_score DECIMAL(6,2),
    percentage DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'graded', 'in_review')),
    time_spent INTEGER, -- in seconds
    attempt_number INTEGER DEFAULT 1,
    ai_graded BOOLEAN DEFAULT FALSE,
    graded_by UUID REFERENCES teachers(id),
    graded_at TIMESTAMP,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_submissions_assessment ON submissions(assessment_id);
CREATE INDEX idx_submissions_student ON submissions(student_id);
CREATE INDEX idx_submissions_status ON submissions(status);
```

#### submission_answers
```sql
CREATE TABLE submission_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID REFERENCES submissions(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    answer_data JSONB NOT NULL, -- Stores student's answer
    is_correct BOOLEAN,
    points_earned DECIMAL(6,2),
    ai_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_answers_submission ON submission_answers(submission_id);
```

### 4. Adaptive Learning & Performance Tracking

#### student_skill_profiles
```sql
CREATE TABLE student_skill_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
    mastery_level DECIMAL(4,2) DEFAULT 0.0 CHECK (mastery_level BETWEEN 0 AND 100),
    attempts_count INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    last_practiced TIMESTAMP,
    next_review TIMESTAMP, -- For spaced repetition
    difficulty_preference VARCHAR(20),
    learning_speed DECIMAL(4,2), -- Questions per hour
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id, topic_id)
);

CREATE INDEX idx_skill_profiles_student ON student_skill_profiles(student_id);
CREATE INDEX idx_skill_profiles_mastery ON student_skill_profiles(mastery_level);
```

#### learning_sessions
```sql
CREATE TABLE learning_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id),
    session_type VARCHAR(50) NOT NULL, -- quiz, study, ai_tutor, practice
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration INTEGER, -- in seconds
    questions_attempted INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    topics_covered TEXT[],
    session_data JSONB, -- Additional metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_student ON learning_sessions(student_id);
CREATE INDEX idx_sessions_date ON learning_sessions(started_at);
```

#### ai_tutor_conversations
```sql
CREATE TABLE ai_tutor_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    session_id UUID REFERENCES learning_sessions(id),
    topic_id UUID REFERENCES topics(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_student ON ai_tutor_conversations(student_id);
```

#### ai_tutor_messages
```sql
CREATE TABLE ai_tutor_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES ai_tutor_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'ai', 'system')),
    message TEXT NOT NULL,
    metadata JSONB, -- Stores context, hints provided, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation ON ai_tutor_messages(conversation_id);
```

### 5. Engagement & Analytics

#### student_engagement_logs
```sql
CREATE TABLE student_engagement_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL, -- login, quiz_start, quiz_complete, resource_view, etc.
    course_id UUID REFERENCES courses(id),
    activity_data JSONB,
    duration INTEGER, -- in seconds
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_engagement_student ON student_engagement_logs(student_id);
CREATE INDEX idx_engagement_timestamp ON student_engagement_logs(timestamp);
CREATE INDEX idx_engagement_activity ON student_engagement_logs(activity_type);
```

#### attendance_records
```sql
CREATE TABLE attendance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('present', 'absent', 'late', 'excused')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id, date)
);

CREATE INDEX idx_attendance_student ON attendance_records(student_id);
CREATE INDEX idx_attendance_date ON attendance_records(date);
```

### 6. Predictive Analytics & Dropout Prevention

#### student_risk_scores
```sql
CREATE TABLE student_risk_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    risk_score DECIMAL(5,2) NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    contributing_factors JSONB, -- Stores breakdown of risk factors
    recommended_interventions TEXT[],
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_scores_student ON student_risk_scores(student_id);
CREATE INDEX idx_risk_scores_level ON student_risk_scores(risk_level);
CREATE INDEX idx_risk_scores_date ON student_risk_scores(calculated_at);
```

#### intervention_actions
```sql
CREATE TABLE intervention_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    risk_score_id UUID REFERENCES student_risk_scores(id),
    action_type VARCHAR(50) NOT NULL, -- email, meeting, tutoring, counseling
    description TEXT NOT NULL,
    assigned_to UUID REFERENCES teachers(id),
    scheduled_date TIMESTAMP,
    completed_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    outcome TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interventions_student ON intervention_actions(student_id);
CREATE INDEX idx_interventions_status ON intervention_actions(status);
```

### 7. Grading Rubrics & AI Grading

#### grading_rubrics
```sql
CREATE TABLE grading_rubrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    assessment_id UUID REFERENCES assessments(id),
    criteria JSONB NOT NULL, -- Array of criteria with weights and descriptions
    total_points DECIMAL(6,2) NOT NULL,
    created_by UUID REFERENCES teachers(id),
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rubrics_assessment ON grading_rubrics(assessment_id);
```

#### ai_grading_results
```sql
CREATE TABLE ai_grading_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID REFERENCES submissions(id) ON DELETE CASCADE,
    rubric_id UUID REFERENCES grading_rubrics(id),
    overall_score DECIMAL(6,2) NOT NULL,
    criteria_scores JSONB NOT NULL, -- Breakdown by criteria
    strengths TEXT[],
    weaknesses TEXT[],
    suggestions TEXT[],
    confidence_score DECIMAL(4,2), -- 0-100
    model_used VARCHAR(100),
    processing_time INTEGER, -- milliseconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_grading_submission ON ai_grading_results(submission_id);
```

### 8. Notifications & Alerts

#### notifications
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    action_url TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at);
```

## Relationships Summary

```
users (1) ──────< (M) students
users (1) ──────< (M) teachers
teachers (1) ───< (M) courses
students (M) ──< (M) course_enrollments >── (M) courses
courses (1) ────< (M) topics
courses (1) ────< (M) assessments
assessments (1) < (M) questions
students (M) ──< (M) submissions >── (M) assessments
submissions (1) < (M) submission_answers >── (M) questions
students (1) ───< (M) student_skill_profiles
students (1) ───< (M) learning_sessions
students (1) ───< (M) ai_tutor_conversations
students (1) ───< (M) student_risk_scores
students (1) ───< (M) intervention_actions
```

## Data Retention Policy

- **User Data**: Retained indefinitely while account is active
- **Learning Sessions**: 2 years
- **Engagement Logs**: 1 year
- **Risk Scores**: Latest + 6 months history
- **AI Conversations**: 90 days (anonymized after)
- **Submissions**: Retained for academic record (indefinitely)

## Security Considerations

1. **Encryption**: All sensitive fields (emails, names) encrypted at rest
2. **Access Control**: Row-level security policies
3. **Audit Logging**: Track all data modifications
4. **Data Anonymization**: For ML model training
5. **GDPR Compliance**: Right to erasure, data portability

## Indexes Strategy

- Primary keys on all tables
- Foreign key indexes for joins
- Composite indexes for common query patterns
- Partial indexes for filtered queries
- Full-text search indexes where needed
