import json

from fastapi import APIRouter, Security, Depends, status, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from website.api.auth import get_current_user_required
from website.core import crud, schemas
from website.core.database import get_session

program = APIRouter()
templates = Jinja2Templates(directory="website/templates")


async def check_create_team(
        db: AsyncSession,
        info: schemas.TeamCreate
):
    errors = {}
    if len(info.name) < 6:
        errors['name'] = "Team name must be at least 6 characters"
    program = await crud.get_program(db, id=info.program_id)
    if program is None:
        errors['program_id'] = "This program does not exist"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_team(db, info)
    return {"status": "success", "detail": "Created team!"}


@program.post('/api/program/create-team')
async def create_team(
        info: schemas.TeamCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['program']),
        db: AsyncSession = Depends(get_session)
):
    return await check_create_team(db, info)


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


@program.post('/api/team/create-role')
async def create_role(
        info: schemas.RoleCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['team']),
        db: AsyncSession = Depends(get_session)
):
    return await check_create_role(db, info)


async def check_team_role_link(
        db: AsyncSession,
        info: schemas.TeamRoleAssociation,
):
    errors = {}
    team = await crud.get_team(db, id=info.team_id)
    if team is None:
        errors['event_id'] = "This team does not exist"
    role = await crud.get_role(db, id=info.role_id)
    if role is None:
        errors['role_id'] = "This role does not exist"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_team_role_link(db, info)
    return {"status": "success", "detail": "Linked team and role!"}


@program.post('/api/team/add-role-to-team')
async def add_role_to_team(
        info: schemas.TeamRoleAssociation,
        current_user: schemas.User = Security(get_current_user_required, scopes=['team']),
        db: AsyncSession = Depends(get_session)
):
    return await check_team_role_link(db, info)


async def check_team_membership(
        db: AsyncSession,
        info: schemas.TeamMembership,
):
    errors = {}
    team = await crud.get_team(db, id=info.team_id)
    if team is None:
        errors['team_id'] = "This team does not exist"
    role = await crud.get_role(db, id=info.role_id)
    if role is None:  # TODO: role must be in team
        errors['role_id'] = "This role does not exist"
    user = await crud.get_user(db, id=info.user_id)
    if user is None:
        errors['user_id'] = "This user does not exist"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_team_membership(db, info)
    return {"status": "success", "detail": "Created team membership!"}


@program.post('/api/team/add-user-to-team')
async def add_user_to_team(
        info: schemas.TeamMembership,
        current_user: schemas.User = Security(get_current_user_required, scopes=['team']),
        db: AsyncSession = Depends(get_session)
):
    return await check_team_membership(db, info)
