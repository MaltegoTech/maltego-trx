"""Maltego OAuth Crypto Helper"""
import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, padding as primitives_padding
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from requests.auth import AuthBase


class MaltegoOauth:
    """
    A Crypto Helper for Maltego OAuth Secrets received from the Transform Distribution Server
    The TDS will send back an encrypted combination of the following :
    1. Token
    2. Token Secret
    3. Refresh Token
    4. Expires In

    Contains Methods:
        1. decrypt_secrets(private_key_path="pem file", ciphertext="request.getTransformSetting('name from TDS')")
    """

    @staticmethod
    def _rsa_decrypt(private_key_path=None, ciphertext=None, password=None):
        """
        RSA Decryption function, returns decrypted plaintext in b64 encoding
        """
        ciphertext = base64.b64decode(ciphertext)

        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(),
                                                             password,
                                                             backend=None)
            plaintext = private_key.decrypt(ciphertext, asymmetric_padding.PKCS1v15())

        return plaintext

    @staticmethod
    def _aes_decrypt(key=None, ciphertext=None):
        """
        AES Decryption function, returns decrypted plaintext value
        """
        key = base64.b64decode(key)
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        ciphertext = base64.b64decode(ciphertext)
        padded_b64_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = primitives_padding.PKCS7(128).unpadder()
        plaintext = (unpadder.update(padded_b64_plaintext) + unpadder.finalize()).decode('utf8')
        return plaintext

    @classmethod
    def decrypt_secrets(cls, private_key_path=None, encoded_ciphertext=None):
        """
        The TDS will send back an encrypted combination of the following :
        1. Token
        2. Token Secret
        3. Refresh Token
        4. Expires In

        This function decodes the combinations and decrypts as required and returns a dictionary with the following keys
                {"token":"",
                "token_secret": "",
                "refresh_token": "",
                "expires_in": ""}
        """

        encrypted_fields = encoded_ciphertext.split("$")

        if len(encrypted_fields) == 1:
            token = cls._rsa_decrypt(private_key_path, encrypted_fields[0])
            token_fields = {
                "token": token
            }

        elif len(encrypted_fields) == 2:
            token = cls._rsa_decrypt(private_key_path, encrypted_fields[0])
            token_secret = cls._rsa_decrypt(private_key_path, encrypted_fields[1])
            token_fields = {
                "token": token,
                "token_secret": token_secret
            }

        elif len(encrypted_fields) == 3:
            aes_key = cls._rsa_decrypt(private_key_path, encrypted_fields[2])
            token = cls._aes_decrypt(aes_key, encrypted_fields[0])
            token_secret = cls._aes_decrypt(aes_key, encrypted_fields[1])
            token_fields = {
                "token": token,
                "token_secret": token_secret
            }
        elif len(encrypted_fields) == 4:
            token = cls._rsa_decrypt(private_key_path, encrypted_fields[0])
            token_secret = cls._rsa_decrypt(private_key_path, encrypted_fields[1])
            refresh_token = cls._rsa_decrypt(private_key_path, encrypted_fields[2])
            expires_in = cls._rsa_decrypt(private_key_path, encrypted_fields[3])
            token_fields = {
                "token": token,
                "token_secret": token_secret,
                "refresh_token": refresh_token,
                "expires_in": expires_in
            }
        elif len(encrypted_fields) == 5:
            aes_key = cls._rsa_decrypt(private_key_path, encrypted_fields[4])
            token = cls._aes_decrypt(aes_key, encrypted_fields[0])
            token_secret = cls._aes_decrypt(aes_key, encrypted_fields[1])
            refresh_token = cls._aes_decrypt(aes_key, encrypted_fields[2])
            expires_in = cls._aes_decrypt(aes_key, encrypted_fields[3])
            token_fields = {
                "token": token,
                "token_secret": token_secret,
                "refresh_token": refresh_token,
                "expires_in": expires_in
            }
        else:
            token_fields = {
                "token": "",
                "token_secret": "",
                "refresh_token": "",
                "expires_in": ""
            }

        return token_fields


class OAuth2BearerToken(AuthBase):
    """Implements OAuth2 Bearer access token authentication.

    Pass this object via the `auth` parameter to a request or a
    session object in order to authenticate your requests.

    Example usage, once you have the `access_token`:

    class GreetPerson(DiscoverableTransform):

        @classmethod
        def create_entities(cls, request, response):
            person_name = request.Value

            private_key_path = "private_key.pem"

            encrypted_secrets = request.getTransformSetting('maltego.web.api.key.linkedin')

            token_fields = MaltegoCrypto.decrypt_secrets(private_key_path,encrypted_secrets)

            api_url = ("https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))")
            auth = OAuth2BearerToken(token_fields['token'])
            result = requests.get(api_url,auth=auth)

            response.addEntity(Phrase, result.text)
    """

    def __init__(self, access_token):
        self.access_token = access_token

    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer {}'.format(
            self.access_token
        )
        return request
