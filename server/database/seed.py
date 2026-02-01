from database.db import SessionLocal
from database.models.user import User
from security.jwt import hash_password


def seed_system_admin() -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "system@fusion.com").first()
        if existing:
            return
        admin = User(
            name="System Admin",
            email="system@fusion.com",
            password_hash=hash_password("123456"),
            role="SYSTEM_ADMIN",
            tenant_id=0,
            is_locked=False,
        )
        db.add(admin)
        db.commit()
    finally:
        db.close()
