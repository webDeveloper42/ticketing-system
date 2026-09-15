from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_, select

from ticketing import db
from ticketing.forms import CommentForm, TicketForm, UpdateTicketForm
from ticketing.models import Priority, Role, Ticket, TicketStatus, User
from ticketing.services import TicketService

tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")


def staff_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_staff:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def accessible_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    if not current_user.is_staff and ticket.requester_id != current_user.id:
        abort(404)
    return ticket


@tickets_bp.get("")
@login_required
def list_tickets():
    query = select(Ticket)
    if not current_user.is_staff:
        query = query.where(Ticket.requester_id == current_user.id)
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    search = request.args.get("q", "").strip()[:100]
    if status in {s.value for s in TicketStatus}:
        query = query.where(Ticket.status == TicketStatus(status))
    if priority in {p.value for p in Priority}:
        query = query.where(Ticket.priority == Priority(priority))
    if search:
        query = query.where(
            or_(Ticket.title.ilike(f"%{search}%"), Ticket.description.ilike(f"%{search}%"))
        )
    tickets = db.session.scalars(query.order_by(Ticket.updated_at.desc())).all()
    return render_template(
        "tickets/list.html", tickets=tickets, statuses=TicketStatus, priorities=Priority
    )


@tickets_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = TicketForm()
    if form.validate_on_submit():
        ticket = TicketService.create(
            requester=current_user,
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            priority=Priority(form.priority.data),
        )
        flash(f"{ticket.reference} was created. Support can now track your request.", "success")
        return redirect(url_for("tickets.detail", ticket_id=ticket.id))
    return render_template("tickets/create.html", form=form)


@tickets_bp.route("/<int:ticket_id>", methods=["GET", "POST"])
@login_required
def detail(ticket_id):
    ticket = accessible_ticket(ticket_id)
    form = CommentForm()
    if form.validate_on_submit():
        TicketService.add_comment(
            ticket=ticket, author=current_user, body=form.body.data, internal=form.internal.data
        )
        flash("Update added.", "success")
        return redirect(url_for("tickets.detail", ticket_id=ticket.id))
    comments = [c for c in ticket.comments if current_user.is_staff or not c.internal]
    return render_template("tickets/detail.html", ticket=ticket, comments=comments, form=form)


@tickets_bp.route("/<int:ticket_id>/manage", methods=["GET", "POST"])
@staff_required
def manage(ticket_id):
    ticket = accessible_ticket(ticket_id)
    form = UpdateTicketForm()
    agents = db.session.scalars(
        select(User).where(User.role.in_([Role.AGENT, Role.ADMIN]), User.active.is_(True))
    ).all()
    form.assignee_id.choices = [(0, "Unassigned")] + [
        (u.id, f"{u.name} ({u.role.value})") for u in agents
    ]
    if request.method == "GET":
        form.status.data = ticket.status.value
        form.priority.data = ticket.priority.value
        form.assignee_id.data = ticket.assignee_id or 0
    if form.validate_on_submit():
        assignee = db.session.get(User, form.assignee_id.data) if form.assignee_id.data else None
        if assignee and not assignee.is_staff:
            abort(400)
        TicketService.update(
            ticket=ticket,
            actor=current_user,
            status=TicketStatus(form.status.data),
            priority=Priority(form.priority.data),
            assignee=assignee,
        )
        flash("Ticket updated.", "success")
        return redirect(url_for("tickets.detail", ticket_id=ticket.id))
    return render_template("tickets/manage.html", ticket=ticket, form=form)
