import hashlib, re

def anonymize_phone(phone: str) -> str:
    return re.sub(r'\d(?=\d{4})', '*', phone)

def anonymize_name(name: str) -> str:
    parts = name.split()
    return " ".join(p[0] + "*" * (len(p) - 1) for p in parts)

__all__ = ["anonymize_name", "anonymize_phone"]
