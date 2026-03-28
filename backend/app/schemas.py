from pydantic import BaseModel, Field


class LoginBody(BaseModel):
    username: str
    password: str
    role: str


class RegisterBody(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class MeResponse(BaseModel):
    user: UserOut


class JobOut(BaseModel):
    id: int
    title: str
    description: str
    department: str | None
    location: str | None
    employment_type: str | None
    is_open: bool
    created_at: str


class JobsListResponse(BaseModel):
    jobs: list[JobOut]


class JobApplicantOut(BaseModel):
    application_id: int
    applicant_id: int
    username: str
    original_filename: str
    applied_at: str


class JobApplicantsResponse(BaseModel):
    applicants: list[JobApplicantOut]


class MyApplicationOut(BaseModel):
    application_id: int
    original_filename: str
    applied_at: str


class ResumeUploadResponse(BaseModel):
    application_id: int
    original_filename: str
    applied_at: str


class HrApplicantResumeResponse(BaseModel):
    application_id: int
    applicant_id: int
    username: str
    original_filename: str
    applied_at: str
    created_new_user: bool


class ResumeSummaryItem(BaseModel):
    application_id: int
    username: str
    summary: str


class TopPickOut(BaseModel):
    application_id: int
    username: str
    reason: str


class ResumeSummariesResponse(BaseModel):
    summaries: list[ResumeSummaryItem]
    top_pick: TopPickOut | None = None
    model: str
