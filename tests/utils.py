import uuid


def uuid_str() -> str:
    """Generate a UUID as a string.

    Returns:
        str: A UUID
    """
    return str(uuid.uuid4())
