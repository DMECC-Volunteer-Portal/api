import json

from fastapi import APIRouter, Security, Depends, status, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from website.api.auth import get_current_user_required
from website.core import crud, schemas
from website.core.database import get_session

training = APIRouter()
templates = Jinja2Templates(directory="website/templates")


async def check_log_training_record(
        db: AsyncSession,
        info: schemas.TrainingRecordCreate,
        user_id: int,
):
    errors = {}
    # TODO: datetime regex, training level regex
    coach = await crud.get_user(db, id=info.coach_id)
    if coach is None:  # TODO: or if is not coach
        errors['coach_id'] = "The selected user is not a valid coach"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_training_record(db, info, user_id)
    return {"status": "success", "detail": "Logged training record!"}


@training.post('/api/training/log-training-record')  # TODO: not an api access point, training will automatically create and generate training logs
async def log_training_record(
        info: schemas.TrainingRecordCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['admin']),
        db: AsyncSession = Depends(get_session),
):
    return await check_log_training_record(db, info, current_user.id)
