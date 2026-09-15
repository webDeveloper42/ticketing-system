from datetime import datetime, timedelta, timezone
from enum import Enum

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, Index
from werkzeug.security import check_password_hash, generate_password_hash

from ticketing import db


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Role(str, Enum):
    REQUESTER = "requester"
    AGENT = "agent"
    ADMIN = "admin"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False, default=Role.REQUESTER)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return self.role in {Role.AGENT, Role.ADMIN}

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256:600000")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Ticket(db.Model):
    __table_args__ = (
        CheckConstraint("length(title) >= 5", name="ck_ticket_title_length"),
        Index("ix_ticket_queue", "status", "priority", "created_at"),
    )
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default="general")
    priority = db.Column(db.Enum(Priority), nullable=False, default=Priority.MEDIUM)
    status = db.Column(db.Enum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    requester_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)
    resolved_at = db.Column(db.DateTime)
    requester = db.relationship("User", foreign_keys=[requester_id], backref="requested_tickets")
    assignee = db.relationship("User", foreign_keys=[assignee_id], backref="assigned_tickets")
    comments = db.relationship(
        "Comment", backref="ticket", cascade="all, delete-orphan", order_by="Comment.created_at"
    )

    @property
    def reference(self):
        return f"TKT-{self.id:05d}"

    @property
    def sla_due_at(self):
        hours = {Priority.CRITICAL: 4, Priority.HIGH: 8, Priority.MEDIUM: 24, Priority.LOW: 72}
        return self.created_at + timedelta(hours=hours[self.priority])

    @property
    def sla_breached(self):
        finish = self.resolved_at or utcnow()
        return finish > self.sla_due_at


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    internal = db.Column(db.Boolean, nullable=False, default=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    author = db.relationship("User")


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), index=True)
    action = db.Column(db.String(80), nullable=False)
    detail = db.Column(db.String(500), nullable=False, default="")
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    actor = db.relationship("User")
