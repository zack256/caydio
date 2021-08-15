from passlib.hash import sha256_crypt

def hash_password(plaintext_password):
    return sha256_crypt.hash(plaintext_password)

def verify_password(plaintext, password):
    return sha256_crypt.verify(plaintext, password)