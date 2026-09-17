import hashlib

def make_chunk_hash(source,content):
    text = content.replace("\r\n","\n")
    diges = hashlib.sha256(text.encode("UTF-8")).hexdigest()[:16]
    return f"{source}#{diges}"