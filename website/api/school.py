import json

from fastapi import APIRouter, Security, Depends, status, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from website.api.auth import get_current_user_required
from website.core import crud, schemas
from website.core.database import get_session

school = APIRouter()
templates = Jinja2Templates(directory="website/templates")


async def check_create_event(
        db: AsyncSession,
        info: schemas.EventCreate
):
    errors = {}
    if len(info.name) < 6:
        errors['name'] = "Event name must be at least 6 characters"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_event(db, info)
    return {"status": "success", "detail": "Created event!"}


@school.post('/api/school/create-event')
async def create_school(
        info: schemas.EventCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['school']),
        db: AsyncSession = Depends(get_session)
):
    return await check_create_event(db, info)


async def check_create_role(
        db: AsyncSession,
        info: schemas.RoleCreate,
):
    errors = {}
    if len(info.name) < 2:
        errors['name'] = "Role name must be at least 2 characters"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_role(db, info)
    return {"status": "success", "detail": "Created role!"}


@school.post('/api/school/create-role')
async def create_role(
        info: schemas.RoleCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['school']),
        db: AsyncSession = Depends(get_session)
):
    return await check_create_role(db, info)


async def check_school_event_link(
        db: AsyncSession,
        info: schemas.SchoolEventAssociation,
):
    errors = {}
    school = await crud.get_school(db, id=info.school_id)
    if school is None:
        errors['school_id'] = "This school doesn't exist"
    event = await crud.get_event(db, info.event_id)
    if event is None:
        errors['event_id'] = "This event does not exist"
    if len(info.supervisor) < 3:
        errors['supervisor'] = "Supervisor must be greater than 3 characters"
    if len(info.supervisor_contact) < 5:
        errors['supervisor_contact'] = "Supervisor contact must be greater than 5 characters"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_school_event_link(db, info)
    return {"status": "success", "detail": "Linked school and event!"}


@school.post('/api/school/add-event-to-school')
async def add_event_to_school(
        info: schemas.SchoolEventAssociation,
        current_user: schemas.User = Security(get_current_user_required, scopes=['school']),
        db: AsyncSession = Depends(get_session)
):
    return await check_school_event_link(db, info)


async def check_event_role_link(
        db: AsyncSession,
        info: schemas.EventRoleAssociation,
):
    errors = {}
    event = await crud.get_event(db, id=info.event_id)
    if event is None:
        errors['event_id'] = "This event does not exist"
    role = await crud.get_role(db, id=info.role_id)
    if role is None:
        errors['role_id'] = "This role does not exist"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_event_role_link(db, info)
    return {"status": "success", "detail": "Linked event and role!"}


@school.post('/api/school/add-role-to-event')
async def add_role_to_event(
        info: schemas.EventRoleAssociation,
        current_user: schemas.User = Security(get_current_user_required, scopes=['school']),
        db: AsyncSession = Depends(get_session)
):
    return await check_event_role_link(db, info)
