from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import CurrentTenant
from app.auth.email_change_otp import consume_email_change_otp, generate_email_change_otp
from app.auth.jwt import create_access_token
from app.auth.reset_tokens import consume_reset_token, generate_reset_token
from app.auth.signup_otp import consume_signup_otp, generate_signup_otp
from app.auth.users import (
    EmailAlreadyRegisteredError,
    authenticate,
    create_user_with_hash,
    hash_password,
    invite_user,
    set_email,
    set_password,
    user_exists,
)
from app.config import settings
from app.models.schemas import (
    ChangeEmailRequestOtpRequest,
    ChangeEmailVerifyOtpRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    InviteEmployeeRequest,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
    SignupRequest,
    VerifyOtpRequest,
)
from app.notifications.mailer import MailerNotConfiguredError, send_email

router = APIRouter(prefix="/auth", tags=["auth"])

_EMAIL_ALREADY_REGISTERED = "An account with that email already exists"
_MAILER_NOT_CONFIGURED = "Email delivery is not configured on this server"


@router.post("/login")
async def login(request: LoginRequest) -> LoginResponse:
    user = authenticate(request.email, request.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    token = create_access_token(
        user.user_id, user.tenant_id, user.tenant_name, user.role, user.email, user.name
    )
    return LoginResponse(token=token)


@router.post("/signup/request-otp", status_code=status.HTTP_202_ACCEPTED)
async def request_signup_otp(request: SignupRequest) -> dict[str, str]:
    # Step 1 of signup: nothing is created yet. This is the ONLY path that
    # leads to a new organization (tenant) being created — always an admin
    # signup, finalized by /signup/verify-otp below. Employees never
    # self-signup; see /auth/invite for how they join an existing org.
    #
    # Unlike /forgot-password, it's fine (and necessary, per the spec of
    # this flow) to tell the caller up front that the email is already
    # registered — a 409 here doesn't hand an attacker anything they
    # couldn't already learn by attempting a normal signup.
    if user_exists(request.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=_EMAIL_ALREADY_REGISTERED
        )

    # Hash immediately — never hold the plaintext password in memory any
    # longer than this request needs it, even though the OTP store itself
    # is only in-memory and short-lived.
    password_hash = hash_password(request.password)
    code = generate_signup_otp(
        request.organization_name, request.email, password_hash, request.name
    )
    try:
        send_email(
            to=request.email,
            subject="Verify your email for SecureRAG",
            body=(
                f"Your SecureRAG email verification code is: {code}\n\n"
                "Enter this code to finish creating your account (valid for 10 minutes).\n\n"
                "If you didn't request this, you can safely ignore this email."
            ),
        )
    except MailerNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_MAILER_NOT_CONFIGURED,
        ) from exc
    return {"detail": f"A verification code has been sent to {request.email}."}


@router.post("/signup/verify-otp")
async def verify_signup_otp(request: VerifyOtpRequest) -> LoginResponse:
    # Step 2 of signup: only now does the organization/user actually get
    # created, using the org name + pre-hashed password stashed at
    # request-otp time.
    verified = consume_signup_otp(request.email, request.code)
    if verified is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That code is invalid or has expired. Please request a new one.",
        )
    try:
        user = create_user_with_hash(
            verified.organization_name, request.email, verified.password_hash, verified.name
        )
    except EmailAlreadyRegisteredError as exc:
        # Only possible if the account was created through some other path
        # during the OTP's validity window (e.g. a concurrent signup).
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=_EMAIL_ALREADY_REGISTERED
        ) from exc
    token = create_access_token(
        user.user_id, user.tenant_id, user.tenant_name, user.role, user.email, user.name
    )
    return LoginResponse(token=token)


@router.post("/invite", status_code=status.HTTP_201_CREATED)
async def invite_employee(request: InviteEmployeeRequest, tenant: CurrentTenant) -> dict[str, str]:
    # Admin-only: adds a teammate to the CALLER's own tenant (never a new
    # one), active immediately with the email/name/password the admin gave
    # it — there is no public signup for employees, and no email-OTP step
    # here (an admin vouching for a known teammate is treated as sufficient
    # verification). If this member later changes their own email, that
    # still goes through the OTP-verified change-email flow like anyone
    # else's — see /auth/change-email/*.
    if tenant.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an organization admin can invite teammates",
        )

    try:
        invite_user(
            tenant.tenant_id, tenant.tenant_name, request.email, request.password, request.name
        )
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=_EMAIL_ALREADY_REGISTERED
        ) from exc

    return {"detail": f"{request.email} has been added to {tenant.tenant_name}."}


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(request: ForgotPasswordRequest) -> dict[str, str]:
    # Always return the same response whether or not the email is
    # registered — revealing that in the response would let an attacker
    # enumerate valid accounts. Only actually send an email when it exists.
    if user_exists(request.email):
        token = generate_reset_token(request.email)
        reset_link = f"{settings.frontend_base_url}/reset-password?token={token}"
        try:
            send_email(
                to=request.email,
                subject="Reset your SecureRAG password",
                body=(
                    "We received a request to reset your SecureRAG password.\n\n"
                    f"Reset it here (valid for 30 minutes): {reset_link}\n\n"
                    "If you didn't request this, you can safely ignore this email."
                ),
            )
        except MailerNotConfiguredError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=_MAILER_NOT_CONFIGURED,
            ) from exc
    return {"detail": "If that email is registered, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest) -> dict[str, str]:
    email = consume_reset_token(request.token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Reset link is invalid or has expired"
        )
    set_password(email, request.new_password)
    return {"detail": "Password has been reset. You can now log in with your new password."}


@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, tenant: CurrentTenant) -> dict[str, str]:
    # WHO is changing their password always comes from the verified JWT
    # (tenant.email) — never a client-supplied identifier. Re-verifying the
    # current password (rather than trusting the bearer token alone) means a
    # stolen-but-still-valid token can't be used to lock the real owner out.
    if authenticate(tenant.email, request.current_password) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        )
    set_password(tenant.email, request.new_password)
    return {"detail": "Password updated."}


@router.post("/change-email/request-otp", status_code=status.HTTP_202_ACCEPTED)
async def request_change_email_otp(
    request: ChangeEmailRequestOtpRequest, tenant: CurrentTenant
) -> dict[str, str]:
    # Sensitive action (it ultimately changes the login identity), so —
    # exactly like change-password above — require re-entering the current
    # password rather than trusting the bearer token alone. The account
    # being changed is always tenant.email/tenant.user_id from the verified
    # JWT, never request.new_email.
    if authenticate(tenant.email, request.current_password) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        )
    if user_exists(request.new_email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=_EMAIL_ALREADY_REGISTERED
        )

    code = generate_email_change_otp(tenant.user_id, request.new_email)
    try:
        send_email(
            to=request.new_email,
            subject="Verify your new email for SecureRAG",
            body=(
                f"Your SecureRAG email change verification code is: {code}\n\n"
                "Enter this code to confirm this address as your new SecureRAG login "
                "email (valid for 10 minutes).\n\n"
                "If you didn't request this, you can safely ignore this email."
            ),
        )
    except MailerNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_MAILER_NOT_CONFIGURED,
        ) from exc
    return {"detail": f"A verification code has been sent to {request.new_email}."}


@router.post("/change-email/verify-otp")
async def verify_change_email_otp(
    request: ChangeEmailVerifyOtpRequest, tenant: CurrentTenant
) -> LoginResponse:
    # The account being changed is tenant.user_id — derived from the
    # verified JWT — never a client-supplied identifier, so there's no
    # request body field naming whose email this is; that's the whole point
    # of keying the OTP store by user_id (see email_change_otp.py).
    new_email = consume_email_change_otp(tenant.user_id, request.code)
    if new_email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That code is invalid or has expired. Please request a new one.",
        )
    if user_exists(new_email):
        # Someone else registered this exact address while the code was
        # still pending — extremely unlikely, but don't silently clobber it.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=_EMAIL_ALREADY_REGISTERED
        )

    set_email(tenant.email, new_email)
    # Claims (email) just changed, so the old token's embedded email is
    # stale — issue a fresh one, same as every other flow that mutates
    # identity-bearing state.
    token = create_access_token(
        tenant.user_id, tenant.tenant_id, tenant.tenant_name, tenant.role, new_email, tenant.name
    )
    return LoginResponse(token=token)
