import json

from fastapi import APIRouter, Security, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from website.api.auth import get_current_user_required
from website.core import crud, schemas
from website.core.database import get_session

user = APIRouter()


@user.get('/api/user/current-user')  # TODO: only for testing only
async def get_current_user(
        current_user: schemas.User = Security(get_current_user_required),
        db: AsyncSession = Depends(get_session)
):
    user = await crud.get_user(db, id=current_user.id)
    # user = await crud.get_user(db, id=1)
    filled_entries = 0
    for attr in schemas.UserUpdateProfile.from_orm(user).__dict__.keys():
        if not (getattr(user, attr) is None or getattr(user, attr) == "" or getattr(user, attr) == "string"):
            filled_entries = filled_entries + 1
    return json.dumps({
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "school": user.school.name,
        "org_name": user.school.region.name,
        "org_abbr": user.school.region.abbreviation,
        "country": user.school.region.country,
        "start_date": user.start_date,
        "grade": user.grade_level,
        "rank": user.rank,
        "v_level": user.training_level,
        "filled_entries": filled_entries
    }, default=str)


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


@user.post('/api/user/update-profile')
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


@user.post('/api/user/give-feedback')
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


@user.post('/api/user/log-volunteer-record')
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


@user.post('/api/user/create-request')
async def create_reqeust(
        info: schemas.RequestCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
        db: AsyncSession = Depends(get_session)
):
    return await check_create_request(db, info, current_user.id)


@user.get('/api/user/get-teams-of-user')
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


@user.get('/api/user/get-recent-records-of-user')
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
            continue  # TODO: shows only events and not teams
        records[count] = json.dumps({"date": entry.date.isoformat(), "activity": activity, "position": entry.role.name, "hours": entry.hours})
    return json.dumps(records)


@user.get('/api/user/total-hours')
async def get_total_hours(
        current_user: schemas.User = Security(get_current_user_required),
        db: AsyncSession = Depends(get_session)
):
    return await crud.get_user_total_hours(db, current_user.id)
