import datetime
from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from website.core import models, schemas


# TODO: replace add statements with execute insert (maybe)?


async def get_user(
        db: AsyncSession,
        id: Optional[int] = None,
        email: Optional[str] = None,
) -> Optional[models.User]:
    if id is not None:
        result = await db.execute(select(models.User).filter(models.User.id == id))
    elif email is not None:
        result = await db.execute(select(models.User).filter(models.User.email == email))
    else:
        return None
    return result.scalars().first()


async def get_top_volunteers(
        db: AsyncSession,
        limit: int,
        offset: int,
) -> list[models.User]:
    result = await db.execute(select(models.User).order_by(desc(
        select(func.sum(models.VolunteerRecord.hours)).filter(models.VolunteerRecord.user_id == models.User.id))).limit(limit).offset(offset))
    return result.scalars().all()


async def get_user_total_hours(
        db: AsyncSession,
        user_id: int,
) -> int:
    result = await db.execute(select(func.sum(models.VolunteerRecord.hours)).filter(models.VolunteerRecord.user_id == user_id))
    return result.scalars().first()


async def create_user(
        db: AsyncSession,
        user: schemas.UserCreate
) -> models.User:
    new_user = models.User(email=user.email, first_name=user.first_name, last_name=user.last_name, password=user.password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user_password(
        db: AsyncSession,
        user: schemas.UserUpdatePassword
) -> models.User:
    updated_user = await get_user(db, email=user.email)
    updated_user.password = user.new_password
    await db.commit()
    await db.refresh(updated_user)
    return updated_user


async def update_user_profile(
        db: AsyncSession,
        info: schemas.UserUpdateProfile,
        id: int
) -> models.User:
    user = await get_user(db, id)
    args = locals()
    for k, v in dict(args.items()).get('info'):
        if v is not None and v != "":
            setattr(user, k, v)
    await db.commit()
    await db.refresh(user)
    return user


async def create_user_permission_link(
        db: AsyncSession,
        info: schemas.UserPermissions,
) -> models.UserPermissions:
    new_link = models.UserPermissions(user_id=info.user_id, permission_name=info.permission_name)
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    return new_link


async def get_permission(
        db: AsyncSession,
        name: Optional[str] = None,
) -> Optional[models.Permission]:
    if name is not None:
        result = await db.execute(select(models.Permission).filter(models.Permission.name == name))
    else:
        return None
    return result.scalars().first()


async def create_permission(
        db: AsyncSession,
        info: schemas.Permission,
) -> models.Permission:
    new_permission = models.Permission(name=info.name)
    db.add(new_permission)
    await db.commit()
    await db.refresh(new_permission)
    return new_permission


async def get_region(
        db: AsyncSession,
        id: Optional[int] = None,
        name: Optional[str] = None,
) -> Optional[models.Region]:
    if id is not None:
        result = await db.execute(select(models.Region).filter(models.Region.id == id))
    elif name is not None:
        result = await db.execute(select(models.Region).filter(models.Region.name == name))
    else:
        return None
    return result.scalars().first()


async def create_region(
        db: AsyncSession,
        info: schemas.RegionCreate
) -> models.Region:
    new_region = models.Region(country=info.country, name=info.name, abbreviation=info.abbreviation)
    db.add(new_region)
    await db.commit()
    await db.refresh(new_region)
    return new_region


async def get_program(
        db: AsyncSession,
        id: Optional[int] = None,
) -> Optional[models.Program]:
    if id is not None:
        result = await db.execute(select(models.Program).filter(models.Program.id == id))
    else:
        return None
    return result.scalars().first()


async def create_program(
        db: AsyncSession,
        info: schemas.ProgramCreate,
) -> models.Program:
    new_program = models.Program(name=info.name, region_id=info.region_id)
    db.add(new_program)
    await db.commit()
    await db.refresh(new_program)
    return new_program


async def get_school(
        db: AsyncSession,
        id: Optional[int] = None,
        abbreviation: Optional[str] = None,
        name: Optional[str] = None
) -> Optional[models.School]:
    if id is not None:
        result = await db.execute(select(models.School).filter(models.School.id == id))
    elif abbreviation is not None:
        result = await db.execute(select(models.School).filter(models.School.abbreviation == abbreviation))
    elif name is not None:
        result = await db.execute(select(models.School).filter(models.School.name == name))
    else:
        return None
    return result.scalars().first()


async def create_school(
        db: AsyncSession,
        info: schemas.SchoolCreate,
) -> models.School:
    new_school = models.School(abbreviation=info.abbreviation, name=info.name, region_id=info.region_id)
    db.add(new_school)
    await db.commit()
    await db.refresh(new_school)
    return new_school


async def get_event(
        db: AsyncSession,
        id: int,
) -> models.Event:
    result = await db.execute(select(models.Event).filter(models.Event.id == id))
    return result.scalars().first()


async def get_recent_events_by_school(
        db: AsyncSession,
        school_id: int,
) -> list[models.Event]:
    result = await db.execute(
        select(models.Event).where(models.Event.schools.any(models.SchoolEventAssociation.school_id == school_id)).filter(
            models.Event.date < datetime.datetime.utcnow()).order_by(desc(models.Event.date)))
    return result.scalars().all()


async def create_event(
        db: AsyncSession,
        info: schemas.EventCreate,
) -> models.Event:
    new_event = models.Event(name=info.name, date=info.date)
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    return new_event


async def get_team(
        db: AsyncSession,
        id: Optional[int] = None,
) -> Optional[models.Team]:
    if id is not None:
        result = await db.execute(select(models.Team).filter(models.Team.id == id))
    else:
        return None
    return result.scalars().first()


async def get_teams_by_user(
        db: AsyncSession,
        user_id: int,
) -> list[models.Team]:
    result = await db.execute(select(models.Team).where(models.Team.members.any(models.TeamMembership.user_id == user_id)))
    return result.scalars().all()


async def create_team(
        db: AsyncSession,
        info: schemas.TeamCreate,
) -> models.Team:
    new_team = models.Team(name=info.name, program_id=info.program_id)
    db.add(new_team)
    await db.commit()
    await db.refresh(new_team)
    return new_team


async def get_role(
        db: AsyncSession,
        id: Optional[int] = None,
) -> Optional[models.Role]:
    if id is not None:
        result = await db.execute(select(models.Role).filter(models.Role.id == id))
    else:
        return None
    return result.scalars().first()


async def get_roles_by_team(
        db: AsyncSession,
        team_id: int,
) -> list[models.Role]:
    result = await db.execute(select(models.Role).where(models.Role.teams.any(models.TeamRoleAssociation.team_id == team_id)))
    return result.scalars().all()


async def get_roles_by_event(
        db: AsyncSession,
        event_id: int,
) -> list[models.Role]:
    result = await db.execute(select(models.Role).where(models.Role.events.any(models.EventRoleAssociation.event_id == event_id)))
    return result.scalars().all()


async def create_role(
        db: AsyncSession,
        info: schemas.RoleCreate,
) -> models.Role:
    new_role = models.Role(name=info.name)
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    return new_role


async def create_trait(
        db: AsyncSession,
        info: schemas.TraitCreate,
) -> models.Trait:
    new_trait = models.Trait(name=info.name)
    db.add(new_trait)
    await db.commit()
    await db.refresh(new_trait)
    return new_trait


async def create_feedback(
        db: AsyncSession,
        info: schemas.FeedbackCreate,
        user_id: int,
) -> models.Feedback:
    new_feedback = models.Feedback(date=info.date, content=info.content, to_user_id=info.to_user_id, from_user_id=user_id)
    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)
    return new_feedback


async def create_training_record(
        db: AsyncSession,
        info: schemas.TrainingRecordCreate,
        user_id: int,
) -> models.TrainingRecord:
    new_training_record = models.TrainingRecord(date=info.date, level=info.level, completed=info.completed, coach_id=info.coach_id, user_id=user_id)
    db.add(new_training_record)
    await db.commit()
    await db.refresh(new_training_record)
    return new_training_record


async def get_volunteer_records_by_user(
        db: AsyncSession,
        user_id: int,
) -> list[models.VolunteerRecord]:
    result = await db.execute(select(models.VolunteerRecord).filter(models.VolunteerRecord.user_id == user_id).filter(
        models.VolunteerRecord.date < datetime.datetime.utcnow()).order_by(desc(models.VolunteerRecord.date)))
    return result.scalars().all()


async def create_volunteer_record(
        db: AsyncSession,
        info: schemas.VolunteerRecordCreate,
        user_id: int,
) -> models.VolunteerRecord:
    new_volunteer_record = models.VolunteerRecord(date=info.date, hours=info.hours, reflection=info.reflection, event_id=info.event_id,
                                                  team_id=info.team_id, role_id=info.role_id, user_id=user_id)
    db.add(new_volunteer_record)
    await db.commit()
    await db.refresh(new_volunteer_record)
    return new_volunteer_record


async def create_request(
        db: AsyncSession,
        info: schemas.RequestCreate,
        user_id: int,
) -> models.Request:
    new_request = models.Request(date=info.date, purpose=info.purpose, content=info.content, user_id=user_id)
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)
    return new_request


async def create_payment(
        db: AsyncSession,
        info: schemas.PaymentCreate,
) -> models.Payment:
    new_payment = models.Payment(date=info.date, amount=info.amount, purpose=info.purpose, user_id=info.user_id)
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)
    return new_payment


async def create_school_event_link(
        db: AsyncSession,
        info: schemas.SchoolEventAssociation,
) -> models.SchoolEventAssociation:
    new_link = models.SchoolEventAssociation(school_id=info.school_id, event_id=info.event_id, supervisor=info.supervisor,
                                             supervisor_contact=info.supervisor_contact)
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    return new_link


async def create_event_role_link(
        db: AsyncSession,
        info: schemas.EventRoleAssociation,
) -> models.EventRoleAssociation:
    new_link = models.EventRoleAssociation(event_id=info.event_id, role_id=info.role_id)
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    return new_link


async def create_team_role_link(
        db: AsyncSession,
        info: schemas.TeamRoleAssociation,
) -> models.TeamRoleAssociation:
    new_link = models.TeamRoleAssociation(team_id=info.team_id, role_id=info.role_id)
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    return new_link


async def create_team_membership(
        db: AsyncSession,
        info: schemas.TeamMembership,
) -> models.TeamMembership:
    new_membership = models.TeamMembership(team_id=info.team_id, user_id=info.user_id, role_id=info.role_id)
    db.add(new_membership)
    await db.commit()
    await db.refresh(new_membership)
    return new_membership
