"""Email templates CRUD."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import EmailTemplate
from schemas import EmailTemplateCreate, EmailTemplateOut

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("", response_model=list[EmailTemplateOut])
async def list_templates(db: AsyncSession = Depends(get_db)) -> Any:
    rows = (await db.execute(select(EmailTemplate))).scalars().all()
    return [EmailTemplateOut.model_validate(r) for r in rows]


@router.post("", response_model=EmailTemplateOut)
async def create_template(body: EmailTemplateCreate, db: AsyncSession = Depends(get_db)) -> Any:
    t = EmailTemplate(
        name=body.name,
        subject_template=body.subject_template,
        body_template=body.body_template,
        use_case=body.use_case,
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return EmailTemplateOut.model_validate(t)


@router.patch("/{template_id}", response_model=EmailTemplateOut)
async def patch_template(
    template_id: int, body: dict[str, Any], db: AsyncSession = Depends(get_db)
) -> Any:
    t = await db.get(EmailTemplate, template_id)
    if not t:
        raise HTTPException(404, "Template not found")
    for k in ("name", "subject_template", "body_template", "use_case"):
        if k in body:
            setattr(t, k, body[k])
    await db.commit()
    await db.refresh(t)
    return EmailTemplateOut.model_validate(t)
