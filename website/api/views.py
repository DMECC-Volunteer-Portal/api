from datetime import datetime

from fastapi import APIRouter, Depends, Request, Security
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from website.api.auth import get_current_user_optional, get_current_user_required
from website.core import schemas, crud
from website.core.database import get_session
from website.core.utils import four_digit_number

views = APIRouter()
templates = Jinja2Templates(directory="website/templates")


@views.get('/portal')
async def portal(
        request: Request,
        db: AsyncSession = Depends(get_session),
        current_user: schemas.User = Security(get_current_user_required),
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
        current_user: schemas.User = Security(get_current_user_required),
        db: AsyncSession = Depends(get_session)
):
    hours = await crud.get_total_company_hours(db)
    hours_year = await crud.get_total_company_hours_past_year(db)
    hours_display = four_digit_number(hours)
    hours_year_display = four_digit_number(hours_year)
    total_volunteers = await crud.get_volunteer_count(db)

    return templates.TemplateResponse("community.html", {"request": request, "hours_display": hours_display,
                                                         "hours_year_display": hours_year_display, "hours_year": hours_year,
                                                         "volunteer_count": total_volunteers})
