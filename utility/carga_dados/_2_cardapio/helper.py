import base64


def base64_encode(string):
    byte_str = string.encode()
    base64_str = base64.b64encode(byte_str)
    base64_str = base64_str.decode()
    return base64_str
