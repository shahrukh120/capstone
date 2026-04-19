"""SMTP-based email sender + meeting link generator.

Uses Python's built-in smtplib/email libraries — no extra dependencies.
Works with any SMTP provider (Gmail App Passwords, SendGrid, Mailgun, Outlook, etc.).

Environment variables required:
  SMTP_HOST      e.g. smtp.gmail.com
  SMTP_PORT      e.g. 587
  SMTP_USER      e.g. your@gmail.com
  SMTP_PASSWORD  e.g. Gmail App Password (16 chars, no spaces)
  SMTP_FROM      e.g. "AI-ATS Recruiter <your@gmail.com>"  (optional, defaults to SMTP_USER)
  SMTP_USE_TLS   "true" (default) or "false"
"""
from __future__ import annotations

import logging
import os
import re
import smtplib
import ssl
import uuid
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# ── Config ──────────────────────────────────────────────────────────
SMTP_HOST     = os.environ.get("SMTP_HOST", "")
SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER     = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM     = os.environ.get("SMTP_FROM", SMTP_USER)
SMTP_USE_TLS  = os.environ.get("SMTP_USE_TLS", "true").lower() != "false"

SMTP_CONFIGURED = bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def is_valid_email(addr: Optional[str]) -> bool:
    """Basic RFC-compliant email validation."""
    if not addr or not isinstance(addr, str):
        return False
    return bool(EMAIL_RE.match(addr.strip()))


def generate_jitsi_link(prefix: str = "ats-interview") -> str:
    """Generate a free, no-auth Jitsi Meet room link.

    Jitsi rooms are created on first visit — no API call needed.
    Returns a URL with a random, unguessable room name.
    """
    # 12-char random suffix for un-guessability
    room = f"{prefix}-{uuid.uuid4().hex[:12]}"
    return f"https://meet.jit.si/{room}"


def send_email(
    to_addr: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> Tuple[bool, str]:
    """Send an email via configured SMTP. Returns (ok, message)."""
    if not SMTP_CONFIGURED:
        return False, "SMTP not configured. Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD env vars."

    if not is_valid_email(to_addr):
        return False, f"Invalid recipient email: {to_addr}"

    if not subject or not subject.strip():
        return False, "Subject required"

    if not body or not body.strip():
        return False, "Body required"

    try:
        msg = EmailMessage()
        msg["Subject"] = subject.strip()
        msg["From"] = SMTP_FROM or SMTP_USER
        msg["To"] = to_addr
        msg["Message-ID"] = make_msgid(domain="ats.local")
        if reply_to:
            msg["Reply-To"] = reply_to
        msg.set_content(body)
        if html_body:
            msg.add_alternative(html_body, subtype="html")

        context = ssl.create_default_context()
        if SMTP_PORT == 465:
            # Implicit SSL
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=20) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # STARTTLS (587 standard)
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
                server.ehlo()
                if SMTP_USE_TLS:
                    server.starttls(context=context)
                    server.ehlo()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)

        logger.info(f"Email sent to {to_addr}: {subject[:60]}")
        return True, "Email sent successfully"
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP auth failed: {e}")
        return False, "SMTP authentication failed. Check SMTP_USER/SMTP_PASSWORD (Gmail needs App Password)."
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return False, f"SMTP error: {str(e)[:200]}"
    except Exception as e:
        logger.exception("Unexpected email error")
        return False, f"Failed to send: {str(e)[:200]}"


def send_interview_invite(
    candidate_name: str,
    to_addr: str,
    job_title: str,
    company_name: str = "Our Team",
    meeting_link: Optional[str] = None,
    meeting_datetime: Optional[str] = None,  # ISO8601 or human-friendly
    interviewer_name: Optional[str] = None,
    custom_message: Optional[str] = None,
    auto_jitsi: bool = False,
) -> Tuple[bool, str, dict]:
    """Send a templated interview invitation email.

    Returns (ok, message, details) where details includes the meeting link used.
    """
    # Resolve meeting link
    link = meeting_link.strip() if meeting_link else None
    if not link and auto_jitsi:
        link = generate_jitsi_link()
    link_source = "custom" if meeting_link else ("jitsi" if auto_jitsi else "none")

    # Build subject + body
    subject = f"Interview Invitation — {job_title} at {company_name}"

    greeting = f"Hi {candidate_name or 'there'},"
    time_line = f"\n\n📅 **When:** {meeting_datetime}" if meeting_datetime else ""
    link_line = f"\n🔗 **Meeting link:** {link}" if link else ""
    interviewer_line = f"\n\nYou'll be speaking with {interviewer_name}." if interviewer_name else ""
    custom_line = f"\n\n{custom_message.strip()}" if custom_message else ""

    body = f"""{greeting}

Thank you for your interest in the {job_title} role at {company_name}.
We'd love to invite you to an interview to learn more about your experience
and discuss how you might fit our team.{time_line}{link_line}{interviewer_line}{custom_line}

Please confirm your availability by replying to this email. If the timing
doesn't work, let us know and we'll find a slot that fits your schedule.

Looking forward to speaking with you!

Best regards,
{company_name} Recruitment Team
""".strip()

    # HTML version (nicer formatting)
    time_html = f'<p style="margin:8px 0;"><strong>📅 When:</strong> {meeting_datetime}</p>' if meeting_datetime else ""
    link_html = f'<p style="margin:8px 0;"><strong>🔗 Meeting link:</strong> <a href="{link}" style="color:#4f46e5;">{link}</a></p>' if link else ""
    interviewer_html = f'<p style="margin:12px 0;">You\'ll be speaking with <strong>{interviewer_name}</strong>.</p>' if interviewer_name else ""
    custom_html = f'<div style="margin:16px 0; padding:12px; background:#f9fafb; border-left:3px solid #4f46e5; border-radius:4px;">{custom_message}</div>' if custom_message else ""

    html_body = f"""<!DOCTYPE html>
<html><body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; line-height:1.6; color:#1f2937; max-width:600px; margin:0 auto; padding:24px;">
  <div style="background:#4f46e5; color:white; padding:20px 24px; border-radius:8px 8px 0 0;">
    <h2 style="margin:0; font-size:20px;">Interview Invitation</h2>
    <p style="margin:4px 0 0; opacity:0.9; font-size:14px;">{job_title} at {company_name}</p>
  </div>
  <div style="border:1px solid #e5e7eb; border-top:none; padding:24px; border-radius:0 0 8px 8px;">
    <p>Hi {candidate_name or 'there'},</p>
    <p>Thank you for your interest in the <strong>{job_title}</strong> role at <strong>{company_name}</strong>. We'd love to invite you to an interview to learn more about your experience and discuss how you might fit our team.</p>
    {time_html}
    {link_html}
    {interviewer_html}
    {custom_html}
    <p style="margin-top:20px;">Please confirm your availability by replying to this email. If the timing doesn't work, let us know and we'll find a slot that fits your schedule.</p>
    <p>Looking forward to speaking with you!</p>
    <p style="margin-top:24px; color:#6b7280; font-size:13px;">Best regards,<br/><strong>{company_name}</strong> Recruitment Team</p>
  </div>
  <p style="text-align:center; color:#9ca3af; font-size:11px; margin-top:16px;">Sent via AI-Powered ATS</p>
</body></html>"""

    ok, msg = send_email(to_addr, subject, body, html_body=html_body)
    details = {
        "to": to_addr,
        "subject": subject,
        "meeting_link": link,
        "meeting_link_source": link_source,
        "meeting_datetime": meeting_datetime,
    }
    return ok, msg, details
