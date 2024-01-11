# salt.py

import os

# Check if SALT has been generated and stored
SALT_FILE = 'salt.txt'

if os.path.isfile(SALT_FILE):
    # Read the SALT from the file
    with open(SALT_FILE, 'rb') as file:
        SALT = file.read()
else:
    # Generate a new SALT
    SALT = os.urandom(16)

    # Store the SALT in a file for future use
    with open(SALT_FILE, 'wb') as file:
        file.write(SALT)

# Export the SALT variable
__all__ = ['SALT']
