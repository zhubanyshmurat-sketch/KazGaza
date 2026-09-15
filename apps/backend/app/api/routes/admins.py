from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.auth.rbac import require_dispatcher_or_above, require_super_admin
from app.auth.security import hash_password
from app.models.admin import Admin
from app.repositories import admin_repo
from app.schemas.admin import AdminCreate, AdminOut, AdminUpdate

router = APIRouter(prefix="/admins", tags=["admins"])


@router.get("", response_model=list[AdminOut], dependencies=[Depends(require_dispatcher_or_above)])
async def list_admins(db: AsyncSession = Depends(get_db)):
    # DISPATCHER needs the roster to assign applications to staff;
    # creating/editing accounts below remains SUPER_ADMIN-only.
    return await admin_repo.list_all(db)


@router.post(
    "", response_model=AdminOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_super_admin)]
)
async def create_admin(data: AdminCreate, db: AsyncSession = Depends(get_db)):
    existing = await admin_repo.get_by_email(db, data.email)
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Бұл email тіркелген.")
    admin = Admin(
        name=data.name,
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin


@router.patch("/{admin_id}", response_model=AdminOut, dependencies=[Depends(require_super_admin)])
async def update_admin(admin_id: int, data: AdminUpdate, db: AsyncSession = Depends(get_db)):
    admin = await admin_repo.get_by_id(db, admin_id)
    if not admin:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Қызметкер табылмады.")
    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data:
        password = update_data.pop("password")
        if password:
            admin.password_hash = hash_password(password)
    for field, value in update_data.items():
        setattr(admin, field, value)
    await db.commit()
    await db.refresh(admin)
    return admin
