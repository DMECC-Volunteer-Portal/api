from datetime import datetime

from fastapi import APIRouter, Depends, Request, Security
from fastapi.templating import Jinja2Templates

from website.api.auth import get_current_user_optional, get_current_user_required
from website.core import schemas

views = APIRouter()
templates = Jinja2Templates(directory="website/templates")


@views.get('/portal')
async def portal(
        request: Request,
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
):
    filled_entries = 0
    for attr in schemas.UserUpdateProfile.from_orm(current_user).__dict__.keys():
        if not (getattr(current_user, attr) is None or getattr(current_user, attr) == "" or getattr(current_user, attr) == "string"):
            filled_entries = filled_entries + 1
    total_hours = 0
    for record in current_user.volunteer_records:
        total_hours = total_hours + record.hours
    return templates.TemplateResponse("portal.html", {"request": request, "user": current_user, "filled_entries": filled_entries,
                                                      "total_hours": total_hours, "now": datetime.utcnow()})


@views.get('/community')
async def community(
        request: Request,
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer']),
):
    return templates.TemplateResponse("community.html", {"request": request})
