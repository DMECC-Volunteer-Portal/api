from sqlalchemy import Boolean, Column, ForeignKey, Date, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, unique=True)
    email = Column(String, unique=True, index=True)

    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)
    #
    preferred_name = Column(String)
    photo_permission = Column(Boolean)
    communication_id = Column(String)
    phone_number = Column(String)
    parent_first_name = Column(String)
    parent_last_name = Column(String)
    parent_email = Column(String)
    parent_communication_id = Column(String)
    parent_phone_number = Column(String)
    #
    grade_level = Column(Integer)
    english_literacy = Column(String)
    start_date = Column(Date)
    training_level = Column(String)
    rank = Column(String)
    desired_major = Column(String)
    volunteer_status = Column(String)
    volunteer_goals = Column(String)
    #
    school_id = Column(Integer, ForeignKey("school.id"))
    school = relationship("School", uselist=False, back_populates="students", lazy='selectin')
    teams = relationship("TeamMembership", lazy='selectin')
    traits = relationship("UserTraitAssociation", lazy='selectin')
    feedback_received = relationship("Feedback", back_populates="recipient", foreign_keys="[Feedback.to_user_id]", lazy='selectin')
    feedback_given = relationship("Feedback", back_populates="author", foreign_keys="[Feedback.from_user_id]", lazy='selectin')
    training_records = relationship("TrainingRecord", back_populates="user", foreign_keys="[TrainingRecord.user_id]", lazy='selectin')
    volunteer_records = relationship("VolunteerRecord", back_populates="user", lazy='selectin')
    requests = relationship("Request", back_populates="user", lazy='selectin')
    payments = relationship("Payment", back_populates="user", lazy='selectin')
    #
    permissions = relationship("UserPermissions", lazy='selectin')


class UserPermissions(Base):
    __tablename__ = "user_permissions"

    user_id = Column(ForeignKey("user.id"), primary_key=True)
    permission_name = Column(ForeignKey("permission.name"), primary_key=True)


class Permission(Base):
    __tablename__ = "permission"

    name = Column(String, primary_key=True)


class Region(Base):
    __tablename__ = "region"

    id = Column(Integer, primary_key=True, unique=True)
    country = Column(String)
    name = Column(String, unique=True)
    abbreviation = Column(String)
    #
    schools = relationship("School", back_populates="region", lazy='selectin')
    programs = relationship("Program", back_populates="region", lazy='selectin')


class Program(Base):
    __tablename__ = "program"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, unique=True)
    #
    region_id = Column(Integer, ForeignKey("region.id"))
    region = relationship("Region", uselist=False, back_populates="programs", lazy='selectin')
    teams = relationship("Team", back_populates="program", lazy='selectin')


class School(Base):
    __tablename__ = "school"

    id = Column(Integer, primary_key=True, unique=True)
    abbreviation = Column(String, unique=True)
    name = Column(String, unique=True)
    #
    region_id = Column(Integer, ForeignKey("region.id"))
    region = relationship("Region", uselist=False, back_populates="schools", lazy='selectin')
    students = relationship("User", back_populates="school", lazy='selectin')
    events = relationship("SchoolEventAssociation", lazy='selectin')


class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    date = Column(Date)
    #
    schools = relationship("SchoolEventAssociation", lazy='selectin')
    roles = relationship("EventRoleAssociation", lazy='selectin')
    volunteer_records = relationship("VolunteerRecord", lazy='selectin')


class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    #
    volunteer_records = relationship("VolunteerRecord", lazy='selectin')
    program_id = Column(Integer, ForeignKey("program.id"))
    program = relationship("Program", uselist=False, back_populates="teams", lazy='selectin')
    members = relationship("TeamMembership", lazy='selectin')
    roles = relationship("TeamRoleAssociation", lazy='selectin')


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    #
    events = relationship("EventRoleAssociation", lazy='selectin')
    teams = relationship("TeamRoleAssociation", lazy='selectin')


class Trait(Base):
    __tablename__ = "trait"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, unique=True)
    date = Column(DateTime)
    content = Column(String)
    #
    to_user_id = Column(Integer, ForeignKey("user.id"))
    recipient = relationship("User", uselist=False, back_populates="feedback_received", foreign_keys="[Feedback.to_user_id]", lazy='selectin')
    from_user_id = Column(Integer, ForeignKey("user.id"))
    author = relationship("User", uselist=False, back_populates="feedback_given", foreign_keys="[Feedback.from_user_id]", lazy='selectin')


class TrainingRecord(Base):
    __tablename__ = "training_record"

    id = Column(Integer, primary_key=True, unique=True)
    date = Column(DateTime)
    level = Column(String)
    completed = Column(Boolean)
    #
    coach_id = Column(Integer, ForeignKey("user.id"))
    coach = relationship("User", uselist=False, foreign_keys="[TrainingRecord.coach_id]", lazy='selectin')
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", uselist=False, back_populates="training_records", foreign_keys="[TrainingRecord.user_id]", lazy='selectin')


class VolunteerRecord(Base):
    __tablename__ = "volunteer_record"

    id = Column(Integer, primary_key=True, unique=True)
    date = Column(DateTime)
    hours = Column(Integer)
    reflection = Column(String)
    #
    role_id = Column(Integer, ForeignKey("role.id"))
    role = relationship("Role", uselist=False, lazy='selectin')
    team_id = Column(Integer, ForeignKey("team.id"))
    team = relationship("Team", uselist=False, back_populates="volunteer_records", lazy='selectin')
    event_id = Column(Integer, ForeignKey("event.id"))
    event = relationship("Event", uselist=False, back_populates="volunteer_records", lazy='selectin')
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", uselist=False, back_populates="volunteer_records", lazy='selectin')


class Request(Base):
    __tablename__ = "request"

    id = Column(Integer, primary_key=True, unique=True)
    date = Column(DateTime)
    purpose = Column(String)
    content = Column(String)
    #
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", uselist=False, back_populates="requests", lazy='selectin')


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, unique=True)
    date = Column(DateTime)
    amount = Column(Integer)
    purpose = Column(String)
    #
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", uselist=False, back_populates="payments", lazy='selectin')


class TeamMembership(Base):
    __tablename__ = "team_membership"

    user_id = Column(ForeignKey("user.id"), primary_key=True)
    team_id = Column(ForeignKey("team.id"), primary_key=True)
    role_id = Column(ForeignKey("role.id"), primary_key=True)


class UserTraitAssociation(Base):
    __tablename__ = "user_trait_association"

    user_id = Column(ForeignKey("user.id"), primary_key=True)
    trait_id = Column(ForeignKey("trait.id"), primary_key=True)
    count = Column(Integer)


class SchoolEventAssociation(Base):
    __tablename__ = "school_event_association"

    school_id = Column(ForeignKey("school.id"), primary_key=True)
    event_id = Column(ForeignKey("event.id"), primary_key=True)
    supervisor = Column(String)
    supervisor_contact = Column(String)


class EventRoleAssociation(Base):
    __tablename__ = "event_role_association"

    event_id = Column(ForeignKey("event.id"), primary_key=True)
    role_id = Column(ForeignKey("role.id"), primary_key=True)


class TeamRoleAssociation(Base):
    __tablename__ = "team_role_association"

    team_id = Column(ForeignKey("team.id"), primary_key=True)
    role_id = Column(ForeignKey("role.id"), primary_key=True)
