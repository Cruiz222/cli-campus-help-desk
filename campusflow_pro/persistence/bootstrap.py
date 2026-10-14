
from pathlib import Path

from campusflow_pro.persistence.schema import (
    SCHEMA_VERSION,
)
from campusflow_pro.persistence.storage import (
    load_state,
)


def empty_state():
    """
    Return a fresh, empty schema-v2 document.

    Each call creates independent ticket and event lists.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "tickets": [],
        "events": [],
    }


def bootstrap_state(filename):
    """
    Load existing application state or initialize an empty state.

    Rules:
    - Missing file: return a new empty document.
    - Valid file: load and return its contents.
    - Corrupt/invalid file: propagate the error.
    - Never overwrite the existing file during startup.

    The empty state is returned in memory. It is not
    automatically written to disk.
    """
    path = Path(filename)

    try:
        return load_state(path)
    except FileNotFoundError:
        # Only a genuinely missing state file should initialize
        # a new document. A missing parent directory, for example,
        # must not be mistaken for a fresh installation.
        if path.parent.is_dir() and not path.exists():
            return empty_state()

        raise
