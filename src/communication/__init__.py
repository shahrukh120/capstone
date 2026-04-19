"""Candidate communication: email + meeting link generation."""
from src.communication.email_sender import (
    send_email,
    send_interview_invite,
    generate_jitsi_link,
    is_valid_email,
    SMTP_CONFIGURED,
)

__all__ = [
    "send_email",
    "send_interview_invite",
    "generate_jitsi_link",
    "is_valid_email",
    "SMTP_CONFIGURED",
]
