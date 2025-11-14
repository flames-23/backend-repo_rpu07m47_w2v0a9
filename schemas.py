"""
Database Schemas for Gym App

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name (e.g., Trainer -> "trainer").
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class Trainer(BaseModel):
    name: str = Field(..., description="Full name of the trainer")
    specialty: str = Field(..., description="Primary specialty e.g., Strength, HIIT, Yoga")
    bio: Optional[str] = Field(None, description="Short bio of the trainer")
    experience_years: int = Field(0, ge=0, le=60, description="Years of experience")
    avatar_url: Optional[str] = Field(None, description="Public image URL")
    socials: Optional[dict] = Field(default=None, description="Social links like instagram, twitter")


class GymClass(BaseModel):
    title: str = Field(..., description="Class title e.g., Power HIIT")
    description: Optional[str] = Field(None, description="Short class description")
    difficulty: str = Field(..., description="Beginner, Intermediate, Advanced")
    duration_minutes: int = Field(..., ge=15, le=180)
    trainer_id: Optional[str] = Field(None, description="Reference to trainer _id as string")
    schedule: List[str] = Field(default_factory=list, description="List of weekly times e.g., ['Mon 7:00', 'Wed 18:00']")


class MembershipPlan(BaseModel):
    name: str = Field(..., description="Plan name e.g., Pro, Elite")
    price_monthly: float = Field(..., ge=0, description="Monthly price in USD")
    features: List[str] = Field(default_factory=list, description="List of included features")
    best_value: bool = Field(False, description="Highlight as best value")


class Lead(BaseModel):
    name: str = Field(...)
    email: str = Field(...)
    phone: Optional[str] = Field(None)
    interest: Optional[str] = Field(None, description="Area of interest e.g., Weight Loss, Muscle Gain")
    message: Optional[str] = Field(None)


class Booking(BaseModel):
    class_id: str = Field(..., description="Booked class _id as string")
    name: str = Field(..., description="Member name")
    email: str = Field(...)
    note: Optional[str] = Field(None)
