import ipaddress
import re
import socket
from urllib.parse import urlsplit, urlunsplit

def validate_public_url(value: str) -> str:
    if not isinstance(value, str) or len(value) > 4096:
        raise ValueError("Invalid URL")
    parts = urlsplit(value.strip())
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError("Only public HTTP or HTTPS URLs are supported")
    if parts.username or parts.password:
        raise ValueError("URLs containing credentials are not supported")
    host = parts.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
        raise ValueError("Local network URLs are not allowed")
    try:
        ip = ipaddress.ip_address(host)
        if not ip.is_global:
            raise ValueError("Private or reserved IP addresses are not allowed")
    except ValueError as exc:
        if str(exc).startswith("Private") or str(exc).startswith("Local"):
            raise
        try:
            records = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        except socket.gaierror:
            raise ValueError("Host could not be resolved")
        for record in records:
            address = ipaddress.ip_address(record[4][0])
            if not address.is_global:
                raise ValueError("Host resolves to a private or reserved address")
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))

def safe_zip_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return (name[:64] or "gallery")
