import hashlib
import uuid

def generate_unique_hash():
    unique_id = uuid.uuid4().hex  # Generate a unique UUID
    hash_object = hashlib.md5(unique_id.encode())  # Create an MD5 hash object
    hex_dig = hash_object.hexdigest()  # Get the hexadecimal digest
    return hex_dig[:5].lower()