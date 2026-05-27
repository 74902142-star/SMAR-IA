from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_security_db, Rule
from auth import require_role, get_current_user
from routers.audit import record_audit
from typing import Optional

router = APIRouter(prefix="/api/rules", tags=["rules"])


class RuleCreate(BaseModel):
    name: str
    condition: str
    action: str
    duration_minutes: Optional[int] = 60
    enabled: Optional[bool] = True


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    condition: Optional[str] = None
    action: Optional[str] = None
    duration_minutes: Optional[int] = None
    enabled: Optional[bool] = None


def _rule_to_dict(rule: Rule) -> dict:
    return {
        "id": rule.id,
        "name": rule.name,
        "condition": rule.condition,
        "action": rule.action,
        "duration_minutes": rule.duration_minutes,
        "enabled": bool(rule.enabled),
    }


@router.get("/")
def get_rules(db: Session = Depends(get_security_db), current_user=Depends(get_current_user)):
    rules = db.query(Rule).all()
    return [_rule_to_dict(r) for r in rules]


@router.post("/")
def create_rule(rule_data: RuleCreate, db: Session = Depends(get_security_db), current_user=Depends(require_role("admin"))):
    new_rule = Rule(
        name=rule_data.name,
        condition=rule_data.condition,
        action=rule_data.action,
        duration_minutes=rule_data.duration_minutes or 60,
        enabled=rule_data.enabled if rule_data.enabled is not None else True,
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    record_audit(db, current_user.username, "RULE_CREATE", f"rule:{new_rule.id}", rule_data.name)
    return _rule_to_dict(new_rule)


@router.put("/{rule_id}")
def update_rule(rule_id: int, rule_data: RuleUpdate, db: Session = Depends(get_security_db), current_user=Depends(require_role("admin"))):
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    update_data = rule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    db.commit()
    record_audit(db, current_user.username, "RULE_UPDATE", f"rule:{rule_id}", str(update_data))
    return _rule_to_dict(rule)


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_security_db), current_user=Depends(require_role("admin"))):
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    record_audit(db, current_user.username, "RULE_DELETE", f"rule:{rule_id}", rule.name)
    return {"message": "Rule deleted"}
