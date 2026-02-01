from sqlalchemy.orm import Session

from database.models.audit_log import AuditLog


def log_action(
    db: Session,
    user_id: int,
    action: str,
    details: str | None = None,
    project_id: int | None = None,
    task_id: int | None = None,
) -> None:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        details=details,
        project_id=project_id,
        task_id=task_id,
    )
    db.add(entry)
    db.commit()
