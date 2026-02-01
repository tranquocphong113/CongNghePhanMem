import requests
from tabulate import tabulate

BASE_URL = "http://127.0.0.1:8000/"

ROLES = [
    "SYSTEM_ADMIN",
    "TENANT_ADMIN",
    "PM",
    "DEV",
    "BA",
    "QA",
    "CUSTOMER",
]

CREDENTIALS = {
    "SYSTEM_ADMIN": {"username": "system@fusion.com", "password": "123456"},
    "TENANT_ADMIN": {"username": "tenant_admin@fusion.com", "password": "123"},
    "PM": {"username": "pm@fusion.com", "password": "123"},
    "DEV": {"username": "dev@fusion.com", "password": "123"},
    "BA": {"username": "ba@fusion.com", "password": "123"},
    "QA": {"username": "qa@fusion.com", "password": "123"},
    "CUSTOMER": {"username": "customer@fusion.com", "password": "123"},
}

FUNCTIONS = [
    {
        "name": "Create Project",
        "method": "POST",
        "url": "/projects",
        "payload": {"name": "RBAC Test Project"},
    },
    {
        "name": "Update Project",
        "method": "PUT",
        "url": "/projects/1",
        "payload": {"name": "RBAC Updated Project"},
    },
    {
        "name": "View Projects",
        "method": "GET",
        "url": "/projects",
    },
    {
        "name": "Invite User",
        "method": "POST",
        "url": "/projects/1/invite",
        "payload": {"user_id": 1, "role_in_project": "DEV"},
    },
    {
        "name": "Create Task",
        "method": "POST",
        "url": "/tasks/project/1",
        "payload": {"title": "RBAC Task", "description": "Test task"},
    },
    {
        "name": "Update Task",
        "method": "PUT",
        "url": "/tasks/1",
        "payload": {"title": "RBAC Task Updated", "description": "Updated"},
    },
    {
        "name": "Update Status",
        "method": "PUT",
        "url": "/tasks/1/status",
        "payload": {"status": "IN_PROGRESS"},
    },
]


def login(role: str) -> str:
    url = BASE_URL + "/users/login"
    try:
        response = requests.post(url, data=CREDENTIALS[role], timeout=10)
    except requests.RequestException:
        return ""
    if response.status_code != 200:
        return ""
    data = response.json()
    return data.get("access_token", "")


def auth_headers(token: str) -> dict:
    if not token:
        return {}
    return {"Authorization": "Bearer " + token}


def call_api(token: str, method: str, url: str, payload: dict | None) -> int:
    headers = auth_headers(token)
    full_url = BASE_URL + url
    try:
        if method == "GET":
            response = requests.get(full_url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(full_url, headers=headers, json=payload or {}, timeout=10)
        elif method == "PUT":
            response = requests.put(full_url, headers=headers, json=payload or {}, timeout=10)
        else:
            return 0
        return response.status_code
    except requests.RequestException:
        return 0


def status_icon(status_code: int) -> str:
    if status_code in (200, 201):
        return "?"
    if status_code in (401, 403, 404):
        return "?"
    return "?"


def run_tests() -> None:
    tokens = {}
    failed_roles = set()

    for role in ROLES:
        token = login(role)
        if token:
            tokens[role] = token
        else:
            failed_roles.add(role)

    headers = ["Function"] + ROLES
    rows = []

    for function in FUNCTIONS:
        row = [function["name"]]
        for role in ROLES:
            if role in failed_roles:
                row.append("?")
                continue
            status_code = call_api(
                tokens[role],
                function["method"],
                function["url"],
                function.get("payload"),
            )
            row.append(status_icon(status_code))
        rows.append(row)

    print(tabulate(rows, headers=headers, tablefmt="github"))


if __name__ == "__main__":
    run_tests()
