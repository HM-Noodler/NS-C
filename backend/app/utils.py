import hashlib
import random
import string


def generate_password_with_md5():
    """
    Generates a random 8-character password and returns both the password
    and its MD5 hash.

    Returns:
        tuple: (password, md5_hash) - the original password and its MD5 hash
    """
    # Define character set: letters (uppercase + lowercase) and digits
    characters = string.ascii_letters + string.digits

    # Generate random 8-character password
    password = "".join(random.choice(characters) for _ in range(8))

    # Convert password to MD5 hash
    md5_hash = hashlib.md5(password.encode("utf-8")).hexdigest()

    return password, md5_hash


def generate_random_password(length=12):
    """
    Generates a random password of specified length.

    Args:
        length (int): Length of the password to generate. Default is 12.

    Returns:
        str: Randomly generated password.
    """
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))

def split_name(name: str):
    """
    Splits a full name into first_name, middle_name (optional), and last_name.
    
    Args:
        name (str): The full name to split
        
    Returns:
        dict: A dictionary containing the name components. Possible keys:
            - 'first_name': Always present if name is not empty
            - 'middle_name': Present when there are 3 or more name parts
            - 'last_name': Present when there are 2 or more name parts
    """
    parts = name.strip().split()
    
    if not parts:
        return {}
    
    result = {"first_name": parts[0]}
    
    if len(parts) >= 3:
        result["middle_name"] = parts[1]
        result["last_name"] = " ".join(parts[2:])
    elif len(parts) == 2:
        result["last_name"] = parts[1]
        
    return result
