"""Gmail API: send and poll for replies."""

from __future__ import annotations

import asyncio
import base64
import os
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import BACKEND_DIR, settings

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def _resolve(p: str) -> Path:
    path = Path(p)
    if path.is_absolute():
        return path
    return BACKEND_DIR / path


class GmailService:
    def __init__(
        self,
        credentials_path: str | None = None,
        token_path: str | None = None,
    ) -> None:
        self.credentials_path = str(_resolve(credentials_path or settings.gmail_credentials_path))
        self.token_path = str(_resolve(token_path or settings.gmail_token_path))
        self.service: Any = None

    def authenticate(self) -> None:
        creds: Credentials | None = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Gmail credentials not found at {self.credentials_path}"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=8090)
            os.makedirs(os.path.dirname(self.token_path) or ".", exist_ok=True)
            with open(self.token_path, "w") as f:
                f.write(creds.to_json())
        self.service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    def _ensure(self) -> None:
        if self.service is None:
            self.authenticate()

    def send_email_sync(
        self,
        to: str,
        subject: str,
        body: str,
        reply_to_message_id: str | None = None,
        thread_id: str | None = None,
    ) -> dict[str, str]:
        self._ensure()
        msg = MIMEText(body)
        msg["to"] = to
        msg["subject"] = subject
        if reply_to_message_id:
            msg["In-Reply-To"] = reply_to_message_id
            msg["References"] = reply_to_message_id
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        send_body: dict[str, Any] = {"raw": raw}
        if thread_id:
            send_body["threadId"] = thread_id
        result = (
            self.service.users()
            .messages()
            .send(userId="me", body=send_body)
            .execute()
        )
        return {
            "gmail_message_id": result["id"],
            "gmail_thread_id": result.get("threadId", ""),
        }

    def _get_thread_id(self, message_id: str) -> str | None:
        self._ensure()
        m = (
            self.service.users()
            .messages()
            .get(userId="me", id=message_id, format="minimal")
            .execute()
        )
        return m.get("threadId")

    def check_for_replies_sync(
        self, since_history_id: str | None
    ) -> tuple[list[dict[str, Any]], str | None]:
        self._ensure()
        message_ids: list[str] = []
        new_history_id: str | None = None
        if since_history_id:
            try:
                history = (
                    self.service.users()
                    .history()
                    .list(
                        userId="me",
                        startHistoryId=since_history_id,
                        historyTypes=["messageAdded"],
                        labelIds=["INBOX"],
                    )
                    .execute()
                )
                for record in history.get("history", []) or []:
                    for added in record.get("messagesAdded", []) or []:
                        mid = added.get("message", {}).get("id")
                        if mid:
                            message_ids.append(mid)
                new_history_id = history.get("historyId")
            except Exception:
                since_history_id = None
        if not since_history_id:
            results = (
                self.service.users()
                .messages()
                .list(userId="me", labelIds=["INBOX"], maxResults=50)
                .execute()
            )
            for m in results.get("messages", []) or []:
                if m.get("id"):
                    message_ids.append(m["id"])
            profile = self.service.users().getProfile(userId="me").execute()
            new_history_id = str(profile.get("historyId", ""))

        emails: list[dict[str, Any]] = []
        for msg_id in message_ids:
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )
            emails.append(self._parse_message(msg))
        return emails, new_history_id

    def _parse_message(self, msg: dict[str, Any]) -> dict[str, Any]:
        headers_list = msg.get("payload", {}).get("headers", [])
        headers = {h["name"].lower(): h["value"] for h in headers_list}
        body = ""
        payload = msg.get("payload", {})

        def walk_parts(parts: list) -> str:
            nonlocal body
            for part in parts:
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    return base64.urlsafe_b64decode(part["body"]["data"]).decode(
                        errors="replace"
                    )
                if part.get("parts"):
                    t = walk_parts(part["parts"])
                    if t:
                        return t
            return ""

        if payload.get("parts"):
            body = walk_parts(payload["parts"]) or body
        elif payload.get("body", {}).get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode(errors="replace")

        from_hdr = headers.get("from", "")
        from_name = from_hdr.split("<")[0].strip() if from_hdr else ""
        received = msg.get("internalDate")
        return {
            "gmail_message_id": msg["id"],
            "gmail_thread_id": msg.get("threadId"),
            "from_email": from_hdr,
            "from_name": from_name,
            "subject": headers.get("subject", ""),
            "body_text": body,
            "body_snippet": (msg.get("snippet") or "")[:200],
            "received_at": received,
        }


async def send_email_async(
    svc: GmailService,
    to: str,
    subject: str,
    body: str,
    reply_to_message_id: str | None = None,
    thread_id: str | None = None,
) -> dict[str, str]:
    return await asyncio.to_thread(
        svc.send_email_sync, to, subject, body, reply_to_message_id, thread_id
    )


async def check_for_replies_async(
    svc: GmailService, since_history_id: str | None
) -> tuple[list[dict[str, Any]], str | None]:
    return await asyncio.to_thread(svc.check_for_replies_sync, since_history_id)
