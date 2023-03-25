from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import rsa


class RSA():
    # Generate keys RSA
    def generate_keys(self, length_key):
        (public_key, private_key) = rsa.newkeys(length_key)
        with open('pub.pem', 'wb') as p:
            p.write(public_key.save_pkcs1('PEM'))
        with open('sec.pem', 'wb') as p:
            p.write(private_key.save_pkcs1('PEM'))

    # Load keys RSA
    def load_keys(self):
        with open('pub.pem', 'rb') as p:
            public_key = rsa.PublicKey.load_pkcs1(p.read())
        with open('sec.pem', 'rb') as p:
            private_key = rsa.PrivateKey.load_pkcs1(p.read())
        return private_key, public_key

    # Encrypt message
    def encrypt(self, message, key):
        return rsa.encrypt(message, key)

    # Decrypt message
    def decrypt(self, message, key):
        try:
            return rsa.decrypt(message, key)
        except Exception:
            return False

    # Convert string to public key
    def convert(self, string, separator):
        string_public_key = separator.join(string).encode()
        public_key = rsa.PublicKey.load_pkcs1(string_public_key)
        return public_key


class aes():
    # Generate AES key
    def create_key(self, size=16):
        key = get_random_bytes(size)
        file_out = open('key.key', 'wb')
        file_out.write(key)
        file_out.close()
        return key

    # Read AES key
    def read_key(self, file):
        return open(f'{file}', 'rb').read()

    # Encrypt message
    def encrypt(self, key, message):
        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext = cipher.encrypt(message)
        return ciphertext, cipher.nonce

    # Decrypt message
    def decrypt(self, key, ciphertext, nonce):
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        message = cipher.decrypt(ciphertext)
        return message
