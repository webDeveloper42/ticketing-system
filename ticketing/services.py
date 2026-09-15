from datetime import datetime, timezone

from flask import has_request_context, request

from ticketing import db
from ticketing.models import AuditLog, Comment, Ticket, TicketStatus


class TicketService:
    @staticmethod
    def create(*, requester, title, description, category, priority):
        ticket = Ticket(
            requester=requester,
            title=title.strip(),
            description=description.strip(),
            category=category,
            priority=priority,
        )
        db.session.add(ticket)
        db.session.flush()
        TicketService.audit(requester, ticket, "ticket.created", f"Priority: {priority.value}")
        db.session.commit()
        return ticket

    @staticmethod
    def update(*, ticket, actor, status, priority, assignee):
        changes = []
        if ticket.status != status:
            changes.append(f"status {ticket.status.value} -> {status.value}")
            ticket.status = status
            ticket.resolved_at = (
                datetime.now(timezone.utc).replace(tzinfo=None)
                if status in {TicketStatus.RESOLVED, TicketStatus.CLOSED}
                else None
            )
        if ticket.priority != priority:
            changes.append(f"priority {ticket.priority.value} -> {priority.value}")
            ticket.priority = priority
        if ticket.assignee != assignee:
            changes.append(f"assignee -> {assignee.email if assignee else 'unassigned'}")
            ticket.assignee = assignee
        if changes:
            TicketService.audit(actor, ticket, "ticket.updated", "; ".join(changes))
            db.session.commit()

    @staticmethod
    def add_comment(*, ticket, author, body, internal=False):
        comment = Comment(
            ticket=ticket, author=author, body=body.strip(), internal=internal and author.is_staff
        )
        db.session.add(comment)
        TicketService.audit(
            author, ticket, "comment.added", "Internal note" if comment.internal else "Public reply"
        )
        db.session.commit()
        return comment

    @staticmethod
    def audit(actor, ticket, action, detail=""):
        db.session.add(
            AuditLog(
                actor=actor,
                ticket_id=ticket.id,
                action=action,
                detail=detail,
                ip_address=request.remote_addr if has_request_context() else None,
            )
        )
