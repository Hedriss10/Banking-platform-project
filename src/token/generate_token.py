from cryptography.hazmat.primitives import serialization, hashes


def load_private_key():
    with open('src/token/private_key.pem', 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    return private_key

def get_public_key_str():
    private_key = load_private_key()
    public_key = private_key.public_key()
    pem_public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    pem_public_key_str = pem_public_key_bytes.decode('utf-8')
    return pem_public_key_str