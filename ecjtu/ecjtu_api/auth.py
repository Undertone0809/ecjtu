import base64
# from ecjtu.client import _get_enc_password
KEY = "zxcvbnmasdgfhjklpoiuytrewq"

def encode(stud_id, pwd):
    # enc_pwd = _get_enc_password(pwd);
    token = base64.b64encode(f"{stud_id}:{pwd}".encode()).decode()
    return token

def decode(token):
    stud_id, enc_pwd = base64.b64decode(token.encode()).decode().split(":")
    return stud_id, enc_pwd