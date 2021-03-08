import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

#file = open ('entry.note', 'rb') -rb = readbytes

def despPrint(text):
    f = open("output.txt", "w")
    f.write(text + "\n")
    f.close()

def generateKey(inpPass):
    password = inpPass.encode()
    salt = b',\x0c\x98\x96"\xea\x01\x9e\x0b~\xb5\xe3Y\x8c\x1e\xdb'
    kdf = PBKDF2HMAC (
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def verifyKey(key):
    key = key.decode()
    key = generateKey(key).decode()
    trueKey = open("key.key", "r").read()
    return(key == trueKey)

def encryptString(key, entry):
    encodedEntry = entry.encode()
    f = Fernet(key)
    return f.encrypt(encodedEntry).decode()

def decryptString(key, encryptEntry):
    encryptEntry = encryptEntry.encode()
    f = Fernet(key)
    return f.decrypt(encryptEntry).decode()
