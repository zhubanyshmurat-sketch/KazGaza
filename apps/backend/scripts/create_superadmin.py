"""CLI helper to create the first SUPER_ADMIN account.

Usage (inside the backend container/venv):
    python -m scripts.create_superadmin --name "Admin" --email admin@example.com --password secret123
"""
import argparse
import asyncio

from app.auth.security import hash_password
from app.database import AsyncSessionLocal
from app.models.admin import Admin
from app.repositories import admin_repo
from kazgaza_shared import AdminRole


async def main(name: str, email: str, password: str) -> None:
    async with AsyncSessionLocal() as db:
        existing = await admin_repo.get_by_email(db, email)
        if existing:
            print(f"Admin with email {email} already exists.")
            return
        admin = Admin(
            name=name,
            email=email.lower(),
            password_hash=hash_password(password),
            role=AdminRole.SUPER_ADMIN,
        )
        db.add(admin)
        await db.commit()
        print(f"SUPER_ADMIN created: {email}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    asyncio.run(main(args.name, args.email, args.password))
