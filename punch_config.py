__config_version__ = 1

GLOBALS = {
    "serializer": "{{major}}.{{minor}}.{{patch}}",
}

FILES = [{"path": "setup.cfg", "serializer": "version = {{major}}.{{minor}}.{{patch}}"}]

VERSION = ["major", "minor", "patch"]

VCS = {
    "name": "git",
    "commit_message": (
        "Version updated from {{ current_version }}" " to {{ new_version }}"
    ),
    "options": {
        "target_branch": "main",
    },
}
