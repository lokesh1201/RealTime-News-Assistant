# helpers.py

import re
import hashlib

def sanitize_markdown(text):
    text = re.sub(r'<(?!\/?(strong|em|p|h[1-6]|ul|ol|li|blockquote|code|pre|a|br|hr)(\s[^>]*)?\/?>)[^>]*>', '', text)
    return text

def generate_unique_key(text, suffix=""):
    hash_obj = hashlib.md5(text.encode())
    hash_str = hash_obj.hexdigest()[:8]
    return f"{suffix}_{hash_str}"