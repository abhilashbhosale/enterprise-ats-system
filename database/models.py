"""
Database Models for Enterprise ATS
SQLAlchemy ORM Models for all entities
Author: Abhilash Bhosale
GitHub: https://github.com/abhilashbhosale
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Table, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Association tables for many-to-many relationships
candidate_skills = Table(
    'candidate_skills',
    Base.metadata,
    Column('candidate_id', Integer, ForeignKey('candidates.id')),
    Column('skill_id', Integer, ForeignKey('skills.id'))
)

candidate_tags = Table(
    'candidate_tags',
    Base.metadata,
    Column('candidate_id', Integer, ForeignKey('candidates.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

job_skills = Table(
    'job_skills',
    Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id')),
    Column('skill_id', Integer, ForeignKey('skills.id'))
)

interview_panel = Table(
    'interview_panel',
    Base.metadata,
    Column('interview_id', Integer, ForeignKey('interviews.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)


class User(Base):
    """User model with RBAC support"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='recruiter')  # admin, recruiter, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = relationship('Job', back_populates='recruiter')
    communications = relationship('Communication', back_populates='user')
    candidates = relationship('Candidate', back_populates='created_by_user')


class Candidate(Base):
    """Candidate model - core entity"""
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20))
    location = Column(String(150))
    current_title = Column(String(150))
    bio = Column(Text)
    rating = Column(Float, default=0.0)  # 0-5 star rating
    status = Column(String(50), default='new')  # new, screening, interview, offer, hired, rejected
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = relationship('Resume', back_populates='candidate', cascade='all, delete-orphan')
    parsed_data = relationship('ParsedResumeData', back_populates='candidate', cascade='all, delete-orphan')
    skills = relationship('Skill', secondary=candidate_skills, back_populates='candidates')
    tags = relationship('Tag', secondary=candidate_tags, back_populates='candidates')
    applications = relationship('Application', back_populates='candidate', cascade='all, delete-orphan')
    matches = relationship('CandidateJobMatch', back_populates='candidate', cascade='all, delete-orphan')
    interviews = relationship('Interview', back_populates='candidate', cascade='all, delete-orphan')
    communications = relationship('Communication', back_populates='candidate', cascade='all, delete-orphan')
    notes = relationship('CandidateNote', back_populates='candidate', cascade='all, delete-orphan')
    created_by_user = relationship('User', back_populates='candidates')


class Resume(Base):
    """Resume storage model"""
    __tablename__ = 'resumes'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_format = Column(String(10))  # pdf, docx, txt
    file_size = Column(Integer)  # bytes
    is_primary = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    candidate = relationship('Candidate', back_populates='resumes')
    parsed_data = relationship('ParsedResumeData', back_populates='resume', cascade='all, delete-orphan')


class ParsedResumeData(Base):
    """Extracted resume data via NLP"""
    __tablename__ = 'parsed_resume_data'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    resume_id = Column(Integer, ForeignKey('resumes.id'))
    full_text = Column(Text)  # Full resume text
    extracted_name = Column(String(255))
    extracted_email = Column(String(150))
    extracted_phone = Column(String(20))
    years_experience = Column(Float)
    summary = Column(Text)  # AI-generated summary
    strengths = Column(JSON)  # List of strengths
    weaknesses = Column(JSON)  # List of gaps
    raw_json = Column(JSON)  # Complete extraction
    parsing_score = Column(Float, default=0.0)  # 0-100% confidence
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship('Candidate', back_populates='parsed_data')
    resume = relationship('Resume', back_populates='parsed_data')


class Skill(Base):
    """Skills master data"""
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    skill_name = Column(String(150), unique=True, nullable=False)
    category = Column(String(100))  # technical, soft, domain, tools
    proficiency_levels = Column(JSON)  # beginner, intermediate, expert
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidates = relationship('Candidate', secondary=candidate_skills, back_populates='skills')
    jobs = relationship('Job', secondary=job_skills, back_populates='required_skills')


class Tag(Base):
    """Custom tags for candidates"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    tag_name = Column(String(100), unique=True, nullable=False)
    color = Column(String(20))  # For UI display
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    candidates = relationship('Candidate', secondary=candidate_tags, back_populates='tags')


class Job(Base):
    """Job description model"""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    job_title = Column(String(150), nullable=False)
    job_code = Column(String(50), unique=True, nullable=False)
    department = Column(String(100))
    description = Column(Text, nullable=False)
    required_skills = relationship('Skill', secondary=job_skills, back_populates='jobs')
    min_experience = Column(Float)  # years
    max_experience = Column(Float)
    salary_min = Column(Float)
    salary_max = Column(Float)
    location = Column(String(150))
    job_type = Column(String(50))  # full-time, part-time, contract
    status = Column(String(50), default='open')  # open, closed, on-hold
    recruiter_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recruiter = relationship('User', back_populates='jobs')
    applications = relationship('Application', back_populates='job', cascade='all, delete-orphan')
    matches = relationship('CandidateJobMatch', back_populates='job', cascade='all, delete-orphan')
    interviews = relationship('Interview', back_populates='job', cascade='all, delete-orphan')


class Application(Base):
    """Job application tracking"""
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    status = Column(String(50), default='applied')  # applied, screening, interview, offer, rejected
    applied_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship('Candidate', back_populates='applications')
    job = relationship('Job', back_populates='applications')


class CandidateJobMatch(Base):
    """AI-generated match scores"""
    __tablename__ = 'candidate_job_matches'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    overall_score = Column(Float)  # 0-100%
    skills_score = Column(Float)
    experience_score = Column(Float)
    education_score = Column(Float)
    skill_gaps = Column(JSON)  # Missing skills
    match_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship('Candidate', back_populates='matches')
    job = relationship('Job', back_populates='matches')


class Interview(Base):
    """Interview management"""
    __tablename__ = 'interviews'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    interview_type = Column(String(100))  # phone, technical, behavioral, final
    scheduled_date = Column(DateTime)
    completed_date = Column(DateTime)
    status = Column(String(50), default='scheduled')  # scheduled, completed, cancelled
    feedback = Column(Text)
    rating = Column(Float)  # 0-5
    panel_members = relationship('User', secondary=interview_panel)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship('Candidate', back_populates='interviews')
    job = relationship('Job', back_populates='interviews')


class Communication(Base):
    """Email/call/note tracking"""
    __tablename__ = 'communications'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    communication_type = Column(String(50))  # email, phone, note, message
    subject = Column(String(255))
    body = Column(Text)
    status = Column(String(50), default='sent')  # sent, received, pending
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship('Candidate', back_populates='communications')
    user = relationship('User', back_populates='communications')


class CandidateNote(Base):
    """Internal notes on candidates"""
    __tablename__ = 'candidate_notes'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    note_text = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    candidate = relationship('Candidate', back_populates='notes')


class PipelineStage(Base):
    """Kanban pipeline stages"""
    __tablename__ = 'pipeline_stages'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    stage_name = Column(String(100), nullable=False)
    order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    """Saved reports"""
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(50))  # funnel, pipeline, candidate, performance
    filters = Column(JSON)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)