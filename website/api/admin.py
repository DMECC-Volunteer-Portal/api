import json

from fastapi import APIRouter, Security, Depends, status, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from website.api.auth import get_current_user_required
from website.core import crud, schemas
from website.core.database import get_session

admin = APIRouter()
templates = Jinja2Templates(directory="website/templates")


async def check_create_region(
        db: AsyncSession,
        info: schemas.RegionCreate
):
    errors = {}
    temp_region = await crud.get_region(db, name=info.name)
    if temp_region is not None:
        errors['all'] = "There is already a region with this name"
    if len(info.name) < 8:
        errors['name'] = "Region name must be at least 8 characters"
    if len(info.abbreviation) > 7:
        errors['abbreviation'] = "Region abbreviation must be at most 7 characters"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_region(db, info)
    return {"status": "success", "detail": "Created region!"}


@admin.post('/api/admin/create-region')
async def create_region(
        info: schemas.RegionCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['admin']),
        db: AsyncSession = Depends(get_session)
):
    return await check_create_region(db, info)


async def check_create_program(
        db: AsyncSession,
        info: schemas.ProgramCreate,
):
    errors = {}
    if len(info.name) < 3:
        errors['name'] = "Name must be at least 3 characters"
    region = await crud.get_region(db, id=info.region_id)
    if region is None:
        errors['region_id'] = "This region does not exist"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_program(db, info)
    return {"status": "success", "detail": "Created program!"}


@admin.post('/api/admin/create-program')
async def create_program(
        info: schemas.ProgramCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['admin']),
        db: AsyncSession = Depends(get_session)
):
    return await check_create_program(db, info)


async def check_create_school(
        db: AsyncSession,
        info: schemas.SchoolCreate,
):
    errors = {}
    region = await crud.get_region(db, id=info.region_id)
    if region is None:
        errors['region_id'] = "This region does not exist"
    school = await crud.get_school(db, abbreviation=info.abbreviation, name=info.name)
    if school is not None:
        errors['all'] = "School with this name or abbreviation already exists"
    if len(info.abbreviation) > 5:
        errors['abbreviation'] = "Abbreviation must be at most 5 characters"
    if len(info.name) < 6:
        errors['name'] = "School name must be at least 6 characters"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_school(db, info)
    return {"status": "success", "detail": "Created school!"}


@admin.post('/api/admin/create-school')
async def create_school(
        info: schemas.SchoolCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['admin']),
        db: AsyncSession = Depends(get_session)
):
    return await check_create_school(db, info)


async def check_create_trait(
        db: AsyncSession,
        info: schemas.TraitCreate,
):
    errors = {}
    if len(info.name) < 2:
        errors['name'] = "Trait name must be at least 2 characters"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_trait(db, info)
    return {"status": "success", "detail": "Created trait!"}


@admin.post('/api/admin/create-trait')
async def create_info(
        info: schemas.TraitCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['admin']),
        db: AsyncSession = Depends(get_session),
):
    return await check_create_trait(db, info)


async def check_log_payment(
        db: AsyncSession,
        info: schemas.PaymentCreate,
):
    errors = {}
    # TODO: date regex
    user = await crud.get_user(db, id=info.user_id)
    if user is None:
        errors['user_id'] = "This user does not exist"
    if info.amount > 10000:
        errors['amount'] = "Please double check the amount"
    if len(info.purpose) < 10:
        errors['purpose'] = "Payment purpose must be greater than 10 characters"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_payment(db, info)
    return {"status": "success", "detail": "Logged payment!"}


@admin.post('/api/admin/log-payment')
async def log_payment(
        info: schemas.PaymentCreate,
        current_user: schemas.User = Security(get_current_user_required, scopes=['admin']),
        db: AsyncSession = Depends(get_session),
):
    return await check_log_payment(db, info)


async def check_create_permission(
        db: AsyncSession,
        info: schemas.Permission
):
    errors = {}
    if len(info.name) < 3:
        errors['name'] = "Permission name must be at least 3 characters"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_permission(db, info)
    return {"status": "success", "detail": "Created permission!"}


@admin.post('/api/admin/create-permission')
async def create_permission(
        info: schemas.Permission,
        current_user: schemas.User = Security(get_current_user_required, scopes=['admin']),
        db: AsyncSession = Depends(get_session),
):
    return await check_create_permission(db, info)


async def check_user_permission_link(
        db: AsyncSession,
        info: schemas.UserPermissions
):
    errors = {}
    permission = await crud.get_permission(db, name=info.permission_name)
    if permission is None:
        errors['permission_name'] = "This permission does not exist"
    user = await crud.get_user(db, id=info.user_id)
    if user is None:
        errors['user_id'] = "This user does not exist"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    await crud.create_user_permission_link(db, info)
    return {"status": "success", "detail": "Added permission to user!"}


@admin.post('/api/admin/add-permission-to-user')
async def add_permission_to_user(
        info: schemas.UserPermissions,
        current_user: schemas.User = Security(get_current_user_required, scopes=['admin']),
        db: AsyncSession = Depends(get_session),
):
    return await check_user_permission_link(db, info)
