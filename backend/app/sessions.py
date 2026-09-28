import hashlib
import secrets

from fastapi import Request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from .errors import AppError

COOKIE = "clinical_session"


def session_owner(request: Request, required=True):
    token = request.cookies.get(COOKIE)
    signer = URLSafeTimedSerializer(
        request.app.state.settings.session_secret, salt="clinical-session-v1"
    )
    try:
        value = signer.loads(token or "", max_age=60 * 60 * 24 * 30)
        if not isinstance(value, str) or len(value) != 64:
            raise BadSignature("Invalid session")
        return hashlib.sha256(value.encode()).hexdigest()
    except (BadSignature, SignatureExpired):
        if required:
            raise AppError(
                401,
                "session_required",
                "Your session expired. Refresh the page and try again.",
            )
        return None


def create_session(response, settings):
    signer = URLSafeTimedSerializer(settings.session_secret, salt="clinical-session-v1")
    response.set_cookie(
        COOKIE,
        signer.dumps(secrets.token_hex(32)),
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
    )
