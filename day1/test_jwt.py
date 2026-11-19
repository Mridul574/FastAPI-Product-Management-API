import jwt

from datetime import datetime, timedelta, timezone

from security import SECRET_KEY, ALGORITHM, decode_access_token


# Create an already expired token
expired_payload = {
    "sub": "45",
    "role": "seller",
    "exp": datetime.now(timezone.utc) - timedelta(seconds=1)
}

# Generate the expired token
expired_token = jwt.encode(
    expired_payload,
    SECRET_KEY,
    algorithm=ALGORITHM
)

# Try to decode the expired token
try:
    decode_access_token(expired_token)
    print("FAIL: Expired token was accepted!")

except jwt.ExpiredSignatureError:
    print("PASS: Expired token was rejected!")


# Create a valid token
valid_payload = {
    "sub": "45",
    "role": "seller",
    "exp": datetime.now(timezone.utc) + timedelta(minutes=5)
}

valid_token = jwt.encode(
    valid_payload,
    SECRET_KEY,
    algorithm=ALGORITHM
)

# Split JWT into 3 parts
parts = valid_token.split(".")

# Change one character in the signature
new_first_char = "A" if parts[2][0] != "A" else "B"

parts[2] = new_first_char + parts[2][1:]

modified_token = ".".join(parts)

# Try to decode modified token
try:
    decode_access_token(modified_token)
    print("FAIL: Modified token was accepted!")

except jwt.InvalidSignatureError:
    print("PASS: Modified token was rejected!")