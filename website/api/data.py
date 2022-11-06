import datetime
import json

from fastapi import APIRouter, Security, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from website.api.auth import get_current_user_required
from website.core import crud, schemas
from website.core.database import get_session

data = APIRouter()


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


@data.get('/api/data/get-roles-of-event')  # TODO: only show roles user has
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


@data.get('/api/data/get-top-volunteers')  # TODO: create snapshot and rank all volunteers
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
