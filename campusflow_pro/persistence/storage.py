
import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path

from campusflow_pro.persistence.schema import validate_document


def load_state(filename):
    """
    Load and validate a schema-v2 JSON document.

    Missing, corrupt, or invalid files raise errors.
    No partial state is returned.
    """
    path = Path(filename)

    with path.open("r", encoding="utf-8") as file:
        try:
            document = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError("Invalid JSON state file") from error

    validate_document(document)
    return document


def save_state(document, filename):
    """
    Atomically save a validated schema-v2 document.

    Write to a temporary file in the destination directory,
    flush and fsync it, then atomically replace the target.

    On failure, remove the temporary file and preserve the
    previously saved target whenever replacement has not
    occurred.
    """
    validate_document(document)

    path = Path(filename)
    parent = path.parent

    if not parent.is_dir():
        raise FileNotFoundError(
            f"Destination directory does not exist: {parent}"
        )

    # Take a snapshot before serialization.
    snapshot = deepcopy(document)

    # Serialize before creating a temporary file.
    serialized = json.dumps(
        snapshot,
        indent=4,
        ensure_ascii=False,
        allow_nan=False,
    )

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(serialized)
            temporary.flush()
            os.fsync(temporary.fileno())

        os.replace(temporary_path, path)
        temporary_path = None

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
