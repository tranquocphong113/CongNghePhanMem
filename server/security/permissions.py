from fastapi import HTTPException

ROLE_SYSTEM_ADMIN = "SYSTEM_ADMIN"
ROLE_TENANT_ADMIN = "TENANT_ADMIN"
ROLE_PM = "PM"
ROLE_BA = "BA"
ROLE_SUPPORT = "SUPPORT"
ROLE_DEV = "DEV"
ROLE_QA = "QA"
ROLE_CUSTOMER = "CUSTOMER"


def require_role(user_role: str, allowed_roles: set[str]) -> None:
    if user_role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not enough permissions")
