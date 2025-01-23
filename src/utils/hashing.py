import bcrypt


def verify_secret(plain_secret: str, hashed_secret: str) -> bool:
    """
    Verifies whether the given plain text secret matches the hashed secret.

    Args:
        plain_secret (str): The plain text secret to verify.
        hashed_secret (str): The hashed secret to compare against.

    Returns:
        bool: True if the plain text secret matches the hashed secret, False otherwise.
    """
    return bcrypt.checkpw(
        password=plain_secret.encode("utf-8"),
        hashed_password=hashed_secret.encode("utf-8"),
    )


def hash_secret(secret: str) -> str:
    """
    Hashes the given plain text secret using bcrypt.

    Args:
        secret (str): The plain text secret to hash.

    Returns:
        str: The resulting hashed secret as a string.
    """
    return bcrypt.hashpw(
        password=secret.encode("utf-8"),
        salt=bcrypt.gensalt(),
    ).decode("utf-8")
