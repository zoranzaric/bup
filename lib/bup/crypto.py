import nacl
import hashlib
import getpass
import sys

hashkey = None
enckey = None


def encrypt_buffer(content):
    key = get_encryptionkey()
    iv  = nacl.randombytes(24)
    content = iv + nacl.crypto_secretbox(str(content), iv, key)
    return buffer(content)

def decrypt_buffer(content):
    key = get_encryptionkey()
    content = str(content)
    iv = content[:24]
    content = content[24:]
    content = nacl.crypto_secretbox_open(content, iv, key)
    return content

def sha512(msg):
    return hashlib.sha512(msg).digest()

def sha256(msg):
    return hashlib.sha256(msg).digest()

def kdf(passphrase, salt):
    """
     given a passphrase and a salt this function derivates 
     two keys that will later be used for encryption/hashblinding

     this is up for review ... alternatives are pbkdf2 and b/scrypt

     TODO: make number of iterations variable (benchmark it on bup init)
    """
    U = ""
    for i in xrange(65536):
        U = sha256(U + salt + passphrase + str(i))
    return [sha256("0" + U), sha256("1" + U)]


def ask_passphrase():
    global enckey
    global hashkey
    pw1 = "pw1"
    pw2 = "pw2"
    while pw1 != pw2:
        pw1 = getpass.getpass("Enter Passphrase:")
        pw2 = getpass.getpass("Repeat Passphrase:")
        if (pw1 != pw2):
            sys.stderr.write("Passphrases did not match!\n")
    keys = kdf(pw1, "bupsalt") # TODO: get salt from salt file in repository
    hashkey = keys[0]
    enckey = keys[0]

# two lazy getters
def get_encryptionkey():
    if not enckey:
        ask_passphrase()
    return enckey

def get_hashkey():
    if not hashkey:
        ask_passphrase()
    return hashkey

