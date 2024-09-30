"""
Google robot verification.
version: reCAPTCHA v3
"""
import aiohttp

from snatcher.storage.mongo import get_security_key


async def robot_verification(token: str):
    if not token:
        return False
    key = get_security_key('robot')
    data = {'response': token, 'secret': key}
    url = 'https://www.recaptcha.net/recaptcha/api/siteverify'
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        response = await session.post(url, data=data)
        try:
            verified = await response.json()
        except aiohttp.ContentTypeError:
            return False
    if not verified['success']:
        return False
    if verified['score'] < 0.5:
        return False
    return True
