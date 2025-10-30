from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Links(BaseModel):
    """Link with label and URL"""
    label: Optional[str] = Field(None, description="Label for the link")
    url: Optional[str] = Field(None, description="URL of the link")


class PersonalDetails(BaseModel):
    """Personal information of the candidate"""
    fullName: str = Field(..., description="Full name of the candidate")
    email: str = Field(..., description="Email address")
    contactNumber: Optional[str] = Field(None, description="Contact phone number")
    country: Optional[str] = Field(None, description="Country")
    city: Optional[str] = Field(None, description="City")


class RoleDetails(BaseModel):
    """Role and professional summary details"""
    summary: Optional[str] = Field("", description="Professional summary or bio")
    linkedInURL: Optional[str] = Field("", description="LinkedIn profile URL")
    additionalLinks: Optional[List[Links]] = Field(default_factory=list, description="Additional links (portfolio, GitHub, etc.)")


class EducationLineItems(BaseModel):
    """Individual education entry"""
    institute: str = Field(..., description="Educational institution name")
    degree: str = Field(..., description="Degree or qualification obtained")
    startDate: datetime = Field(..., description="Start date of education")
    endDate: Optional[datetime] = Field(None, description="End date of education (null if ongoing)")
    location: str = Field(..., description="Location of the institute")
    description: Optional[str] = Field("", description="Additional details or achievements")


class WorkExperienceLineItems(BaseModel):
    """Individual work experience entry"""
    company: str = Field(..., description="Company name")
    role: str = Field(..., description="Job title or role")
    startDate: datetime = Field(..., description="Start date of employment")
    endDate: Optional[datetime] = Field(None, description="End date of employment (null if current)")
    location: str = Field(..., description="Location of the job")
    description: Optional[str] = Field("", description="Job responsibilities and achievements")


class CustomSectionLineItems(BaseModel):
    """Individual custom section entry"""
    header: str = Field(..., description="Main header for the entry")
    subHeader: Optional[str] = Field("", description="Sub-header or additional title")
    description: Optional[str] = Field("", description="Description or details")


class Education(BaseModel):
    """Education section"""
    fieldName: str = Field(..., description="Name of the education section")
    lineItem: List[EducationLineItems] = Field(..., description="List of education entries")


class WorkExperience(BaseModel):
    """Work experience section"""
    fieldName: str = Field(..., description="Name of the work experience section")
    lineItem: Optional[List[WorkExperienceLineItems]] = Field(default_factory=list, description="List of work experience entries")


class CustomSections(BaseModel):
    """Custom sections for additional information"""
    sectionID: str = Field(..., description="Unique identifier for the section")
    sectionName: str = Field(..., description="Display name of the section")
    lineItems: Optional[List[CustomSectionLineItems]] = Field(default_factory=list, description="List of items in this section")


class Skills(BaseModel):
    """Skills section"""
    fieldName: Optional[str] = Field(None, description="Name of the skills section")
    data: Optional[str] = Field(None, description="Skills data (comma-separated or formatted text)")


class Resume(BaseModel):
    """Complete resume data structure for PDF extraction"""
    personalDetails: PersonalDetails = Field(..., description="Personal information")
    roleDetails: RoleDetails = Field(..., description="Role and summary details")
    education: Education = Field(..., description="Education section")
    workExperience: Optional[WorkExperience] = Field(None, description="Work experience section")
    skills: Optional[Skills] = Field(None, description="Skills section")
    customSections: Optional[List[CustomSections]] = Field(default_factory=list, description="Additional custom sections")