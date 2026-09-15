from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required
from sqlalchemy import select, text

from ticketing import db
from ticketing.models import Ticket, TicketStatus

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return render_template("main/index.html")


@main_bp.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ok", database="ok")
    except Exception:
        return jsonify(status="error", database="unavailable"), 503


@main_bp.get("/dashboard")
@login_required
def dashboard():
    query = select(Ticket)
    if not current_user.is_staff:
        query = query.where(Ticket.requester_id == current_user.id)
    tickets = list(db.session.scalars(query.order_by(Ticket.updated_at.desc())).all())
    counts = {status.value: sum(t.status == status for t in tickets) for status in TicketStatus}
    counts["total"] = len(tickets)
    counts["breached"] = sum(
        t.sla_breached and t.status not in {TicketStatus.RESOLVED, TicketStatus.CLOSED}
        for t in tickets
    )
    return render_template("main/dashboard.html", tickets=tickets[:8], counts=counts)
