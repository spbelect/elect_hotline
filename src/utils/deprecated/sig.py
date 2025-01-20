from base64 import urlsafe_b64encode
from dataclasses import asdict
from datetime import datetime
from hashlib import blake2b
from hmac import compare_digest
from typing import Optional
#from urllib import parse

import json
import secrets
import urllib

from django.conf import settings
from django.utils.timezone import now
from pydantic import EmailStr
from pydantic import BaseModel
from pydantic.dataclasses import dataclass


#join_org: Optional[str] = None   # Join to this organization after successful login.
#redirect_url: Optional[str] = None   # Redirect to this page after a successful login.


class SignedUrlArgs(BaseModel):
    """ 
     передаваемый в GET запросе.
    """
    salt: str   # Automatically generated random string.
    time_created: datetime  # Time when this url was created.
    email: EmailStr
    
    def __init__(self, signature=None, **kwargs):
        kwargs.setdefault('salt', secrets.token_hex(32))
        kwargs.setdefault('time_created', now())
        
        super().__init__(**kwargs)
        self._json = self.model_dump_json(exclude_none=True)
        
        if signature and not verify(self._json, signature):
            raise Exception('Signature invalid')
    
    def urlencode(self):
        return urllib.parse.urlencode(dict(
            signature=sign(self._json), **json.loads(self._json)
        ))
        
    

def sign(string: str) -> str:
    h = blake2b(digest_size=20, key=settings.SECRET_KEY.encode('utf8'))
    h.update(string.encode('utf8'))
    return urlsafe_b64encode(h.hexdigest().encode()).decode()


def verify(string: str, sig: str) -> bool:
    good_sig = sign(string)
    return compare_digest(good_sig, sig)
