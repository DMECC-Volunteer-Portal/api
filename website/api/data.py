import datetime
import json

from fastapi import APIRouter, Security, Depends, status, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from website.api.auth import get_current_user_required
from website.core import crud, schemas
from website.core.database import get_session

data = APIRouter()
templates = Jinja2Templates(directory="website/templates")


@data.get('/api/user/current-user')  # TODO: only for testing only
async def get_current_user(
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
        db: AsyncSession = Depends(get_session)
):
    user = await crud.get_user(db, id=current_user.id)
    return schemas.User.from_orm(user)


async def check_update_profile(
        db: AsyncSession,
        info: schemas.UserUpdateProfile,
        user_id: int,
):
    errors = {}
    school = await crud.get_school(db, id=info.school_id)
    if school is None and info.school_id is not None:
        errors['school_id'] = "This school doesn't exist"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.update_user_profile(db, info, user_id)
    return {"status": "success", "detail": "Updated profile!"}


@data.post('/api/user/update-profile')
async def update_profile(
        info: schemas.UserUpdateProfile,
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
        db: AsyncSession = Depends(get_session)
):
    return await check_update_profile(db, info, current_user.id)


async def check_give_feedback(
        db: AsyncSession,
        info: schemas.FeedbackCreate,
        user_id: int,
):
    errors = {}
    # TODO: datetime regex
    if len(info.content) < 5:
        errors['content'] = "Feedback content must be at least 5 characters"
    to_user = await crud.get_user(db, id=info.to_user_id)
    if to_user is None or to_user.id == user_id:
        errors['to_user_id'] = "Cannot give feedback to this user"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_feedback(db, info, user_id)
    return {"status": "success", "detail": "Gave feedback!"}


@data.post('/api/user/give-feedback')
async def give_feedback(
        info: schemas.FeedbackCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
        db: AsyncSession = Depends(get_session)
):
    return await check_give_feedback(db, info, current_user.id)


async def check_log_volunteer_record(
        db: AsyncSession,
        info: schemas.VolunteerRecordCreate,
        user_id: int,
):
    errors = {}
    # TODO: datetime regex
    if info.hours > 20:
        errors['hours'] = "You are entering in a large amount of hours at once. Please contact a team leader/admin to submit hours"
    if len(info.reflection) < 25:
        errors['reflection'] = "Your reflection must be at least 25 characters"
    if info.event_id is None and info.team_id is None:
        errors['all'] = "Volunteer record must be related to a team or event"
    elif info.event_id is not None and info.team_id is not None:
        errors['all'] = "Choose team or event, not both"
    if info.event_id is not None:
        event = await crud.get_event(db, id=info.event_id)
        if event is None:
            errors['event_id'] = "This event does not exist"
    if info.team_id is not None:
        team = await crud.get_team(db, id=info.team_id)
        if team is None:
            errors['team_id'] = "This team does not exist"
    role = await crud.get_role(db, id=info.role_id)
    if role is None:  # TODO: role must be related to event or team, and user must have access to that role
        errors['role_id'] = "This role does not exist"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_volunteer_record(db, info, user_id)
    return {"status": "success", "detail": "Logged volunteer record!"}


@data.post('/api/user/log-volunteer-record')
async def log_volunteer_record(
        info: schemas.VolunteerRecordCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
        db: AsyncSession = Depends(get_session)
):
    return await check_log_volunteer_record(db, info, current_user.id)


async def check_create_request(
        db: AsyncSession,
        info: schemas.RequestCreate,
        user_id: int,
):
    errors = {}
    # TODO: datetime regex
    if len(info.purpose) < 10:
        errors['purpose'] = "Please describe the purpose of this request in more detail (at least 10 characters)"
    if len(info.content) < 20:
        errors['content'] = "Content length must be at least 20 characters"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_request(db, info, user_id)
    return {"status": "success", "detail": "Created request!"}


@data.post('/api/user/create-request')
async def create_reqeust(
        info: schemas.RequestCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
        db: AsyncSession = Depends(get_session)
):
    return await check_create_request(db, info, current_user.id)


@data.get('/api/data/get-recent-events')
async def get_recent_events(
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
        db: AsyncSession = Depends(get_session)
):
    events = {}
    events['0'] = "Select an event"
    for event in await crud.get_recent_events_by_school(db, current_user.school.id):
        events[event.id] = event.name
    if len(events) == 1:
        events['0'] = "No available events"
    return json.dumps(events)


@data.get('/api/data/get-roles-of-event')
async def get_event_roles(
        event_id: int,
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
        db: AsyncSession = Depends(get_session)
):
    roles = {}
    roles['0'] = "Select a position"
    for role in await crud.get_roles_by_event(db, event_id):
        roles[role.id] = role.name
    if len(roles) == 1:
        roles['0'] = "No available positions"
    return json.dumps(roles)


@data.get('/api/data/get-teams-of-user')
async def get_user_teams(
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
        db: AsyncSession = Depends(get_session)
):
    teams = {}
    teams['0'] = "Select a team"
    for team in await crud.get_teams_by_user(db, current_user.id):
        teams[team.id] = team.name
    if len(teams) == 1:
        teams['0'] = "No available teams"
    return json.dumps(teams)


@data.get('/api/data/get-roles-of-team')  # TODO: only show roles user has
async def get_team_roles(
        team_id: int,
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
        db: AsyncSession = Depends(get_session)
):
    roles = {}
    roles['0'] = "Select a position"
    for role in await crud.get_roles_by_team(db, team_id):
        roles[role.id] = role.name
    if len(roles) == 1:
        roles['0'] = "No available positions"
    return json.dumps(roles)


@data.get('/api/data/get-recent-records-of-user')
async def get_recent_records_of_user(
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
        db: AsyncSession = Depends(get_session)
):
    records = {}
    count = 0
    for entry in await crud.get_volunteer_records_by_user(db, current_user.id):
        count = count + 1
        if entry.team_id is None:
            activity = entry.event.name
        else:
            activity = entry.team.name
        records[count] = json.dumps({"date": entry.date.isoformat(), "activity": activity, "position": entry.role.name, "hours": entry.hours})
    return json.dumps(records)


@data.get('/api/data/get-top-volunteers')
async def get_top_volunteer(
        db: AsyncSession = Depends(get_session)
):
    volunteers = {}
    count = 0
    for volunteer in await crud.get_top_volunteers(db, 10, 0):
        count = count + 1
        total_hours = await crud.get_user_total_hours(db, volunteer.id)
        if volunteer.start_date is None:
            yrs = 0
        else:
            yrs = (datetime.datetime.now().date() - volunteer.start_date).days
        if volunteer.school is None:
            school = "_"
            org = "_"
            loc = "_"
        else:
            school = volunteer.school.abbreviation
            org = volunteer.school.region.abbreviation
            loc = volunteer.school.region.country
        if volunteer.training_level is None:
            lvl = "_"
        else:
            lvl = volunteer.training_level
        if volunteer.rank is None:
            rnk = "_"
        else:
            rnk = volunteer.rank

        volunteers[count] = json.dumps(
            {"name": f"{volunteer.first_name} {volunteer.last_name}", "school": school, "org": org, "loc": loc, "lvl": lvl, "yrs": yrs,
             "hrs": total_hours, "rnk": rnk})
    return json.dumps(volunteers)
