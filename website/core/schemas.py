from datetime import datetime, date
from typing import Optional, Any

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class UserUpdatePassword(UserBase):
    old_password: str
    new_password: str


class UserUpdateProfile(BaseModel):
    preferred_name: Optional[str] = None
    photo_permission: Optional[bool] = False
    communication_id: Optional[str] = None
    phone_number: Optional[str] = None
    parent_first_name: Optional[str] = None
    parent_last_name: Optional[str] = None
    parent_email: Optional[str] = None
    parent_communication_id: Optional[str] = None
    parent_phone_number: Optional[str] = None
    grade_level: Optional[int] = None
    english_literacy: Optional[str] = None
    start_date: Optional[date] = None
    training_level: Optional[str] = None
    desired_major: Optional[str] = None
    volunteer_status: Optional[str] = None
    volunteer_goals: Optional[str] = None
    school_id: Optional[int] = None

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserCommunication(UserBase):
    preferred_name: Optional[str] = None
    photo_permission: Optional[bool] = False
    communication_id: Optional[str] = None
    phone_number: Optional[str] = None
    parent_first_name: Optional[str] = None
    parent_last_name: Optional[str] = None
    parent_email: Optional[str] = None
    parent_communication_id: Optional[str] = None
    parent_phone_number: Optional[str] = None


class UserVolunteerism(UserBase):
    grade_level: Optional[int] = None
    english_literacy: Optional[str] = None
    start_date: Optional[date] = None
    training_level: Optional[str] = None
    rank: Optional[str] = None
    desired_major: Optional[str] = None
    volunteer_status: Optional[str] = None
    volunteer_goals: Optional[str] = None
    school: Optional[Any] = None
    teams: list[Any] = []
    traits: list[Any] = []
    feedback_received: list[Any] = []
    feedback_given: list[Any] = []
    training_records: list[Any] = []
    volunteer_records: list[Any] = []
    requests: list[Any] = []
    payments: list[Any] = []


class User(UserCommunication, UserVolunteerism):
    id: int


class UserPermissions(BaseModel):
    user_id: int
    permission_name: str


class Permission(BaseModel):
    name: str

    class Config:
        orm_mode = True


class RegionBase(BaseModel):
    country: str
    name: str
    abbreviation: str

    class Config:
        orm_mode = True


class RegionCreate(RegionBase):
    pass


class Region(RegionBase):
    id: int
    schools: list[Any] = []
    programs: list[Any] = []


class ProgramBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class ProgramCreate(ProgramBase):
    region_id: int


class Program(ProgramBase):
    id: int
    region: list[Any] = []
    teams: list[Any] = []


class SchoolBase(BaseModel):
    abbreviation: str
    name: str

    class Config:
        orm_mode = True


class SchoolCreate(SchoolBase):
    region_id: int


class School(SchoolBase):
    id: int
    region: Optional[Any] = None
    students: list[Any] = []
    events: list[Any] = []


class EventBase(BaseModel):
    name: str
    date: date

    class Config:
        orm_mode = True


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int
    schools: list[Any] = []
    roles: list[Any] = []
    volunteer_records: list[Any] = []


class TeamBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class TeamCreate(TeamBase):
    program_id: int


class Team(TeamBase):
    id: int
    program: list[Any] = []
    members: list[Any] = []
    roles: list[Any] = []


class RoleBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int


class TraitBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class TraitCreate(TraitBase):
    pass


class Trait(TraitBase):
    id: int


class FeedbackBase(BaseModel):
    date: datetime
    content: str

    class Config:
        orm_mode = True


class FeedbackCreate(FeedbackBase):
    to_user_id: int


class Feedback(FeedbackBase):
    id: int
    recipient: Any
    author: Any


class TrainingRecordBase(BaseModel):
    date: datetime
    level: str
    completed: bool

    class Config:
        orm_mode = True


class TrainingRecordCreate(TrainingRecordBase):
    coach_id: int


class TrainingRecord(TrainingRecordBase):
    user: Any
    coach: Any


class VolunteerRecordBase(BaseModel):
    date: datetime
    hours: int
    reflection: str

    class Config:
        orm_mode = True


class VolunteerRecordCreate(VolunteerRecordBase):
    event_id: Optional[int] = None
    team_id: Optional[int] = None
    role_id: int


class VolunteerRecord(VolunteerRecordBase):
    id: int
    user: Any
    event: Optional[Any] = None
    team: Optional[Any] = None
    role: Any


class RequestBase(BaseModel):
    date: datetime
    purpose: str
    content: str

    class Config:
        orm_mode = True


class RequestCreate(RequestBase):
    pass


class Request(RequestBase):
    id: int
    user: Any


class PaymentBase(BaseModel):
    date: datetime
    amount: int
    purpose: str

    class Config:
        orm_mode = True


class PaymentCreate(PaymentBase):
    user_id: int


class Payment(PaymentBase):
    id: int
    user: Any


class TeamMembership(BaseModel):
    user_id: int
    team_id: int
    role_id: int

    class Config:
        orm_mode = True


class UserTraitAssociation(BaseModel):
    user_id: int
    trait_id: int
    count: Optional[int] = 1

    class Config:
        orm_mode = True


class SchoolEventAssociation(BaseModel):
    supervisor: str
    supervisor_contact: str
    school_id: int
    event_id: int

    class Config:
        orm_mode = True


class EventRoleAssociation(BaseModel):
    event_id: int
    role_id: int

    class Config:
        orm_mode = True


class TeamRoleAssociation(BaseModel):
    team_id: int
    role_id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    iss: str  # issuer
    sub: str  # subject (email), must be unique
    iat: int  # utc unix time
    exp: int  # expires at utc unix time
    jti: str  # token identifier
    scopes: list[str] = []  # permissions
