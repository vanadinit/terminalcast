import socket
from contextlib import closing


def get_my_ip() -> str:
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if not ip.startswith("127."):
            return ip

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect(("8.8.8.8", 53))
        return s.getsockname()[0]


def get_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('0.0.0.0', 0))
        return s.getsockname()[1]
