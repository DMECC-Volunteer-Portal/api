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
