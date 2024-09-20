import base64
import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def decrypt_form_data(encrypted_data_base64, encrypted_key_base64, iv_base64, private_key_path='private_key.pem'):
    with open(private_key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )

    aes_key_base64 = private_key.decrypt(
        base64.b64decode(encrypted_key_base64),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode('utf-8')
    aes_key = base64.b64decode(aes_key_base64)

    encrypted_data_bytes = base64.b64decode(encrypted_data_base64)
    iv = base64.b64decode(iv_base64)

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data_bytes) + decryptor.finalize()

    from cryptography.hazmat.primitives import padding as padding_sym
    unpadder = padding_sym.PKCS7(128).unpadder()
    data_bytes = unpadder.update(padded_data) + unpadder.finalize()

    json_string = data_bytes.decode('utf-8')

    form_data = json.loads(json_string)
    return form_data

encrypted_data_base64 = '...'  # Dados criptografados
encrypted_key_base64 = '...'   # Chave AES criptografada
iv_base64 = '...'              # IV usado na criptografia

form_data = decrypt_form_data(encrypted_data_base64, encrypted_key_base64, iv_base64)
print(form_data)

