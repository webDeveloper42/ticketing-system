# ruff: noqa: E501
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

OUTPUT = Path("output/resumes/Raymond_Frias_Resume_SE_Revised.docx")
BLUE = RGBColor(36, 76, 139)
INK = RGBColor(45, 45, 45)


def font(run, size=8.75, bold=False, italic=False, color=INK):
    run.font.name = "Arial"
    rpr = run._element.get_or_add_rPr()
    rpr.rFonts.set(qn("w:ascii"), "Arial")
    rpr.rFonts.set(qn("w:hAnsi"), "Arial")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color


def heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2.5)
    font(p.add_run(text), 10.25, bold=True, color=BLUE)
    ppr = p._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "7")
    bottom.set(qn("w:color"), "244C8B")
    bottom.set(qn("w:space"), "2")
    borders.append(bottom)
    ppr.append(borders)


def text_line(doc, label, value):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0.5)
    p.paragraph_format.line_spacing = 1.0
    font(p.add_run(label + ": "), 8.6, bold=True)
    font(p.add_run(value), 8.6)


def role_line(doc, title, dates):
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    table.columns[0].width = Inches(5.45)
    table.columns[1].width = Inches(1.5)
    left, right = table.rows[0].cells
    left_p, right_p = left.paragraphs[0], right.paragraphs[0]
    left_p.paragraph_format.space_after = right_p.paragraph_format.space_after = Pt(0)
    font(left_p.add_run(title), 8.75, bold=True)
    font(right_p.add_run(dates), 8.75, bold=True)
    right_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def link_line(doc, value):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(1)
    font(p.add_run(value), 8.55, italic=True, color=BLUE)


def bullet(doc, value):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.20)
    p.paragraph_format.first_line_indent = Inches(-0.12)
    p.paragraph_format.space_after = Pt(0.65)
    p.paragraph_format.line_spacing = 0.96
    font(p.add_run(value), 8.45)


doc = Document()
section = doc.sections[0]
section.top_margin = Inches(0.38)
section.bottom_margin = Inches(0.38)
section.left_margin = Inches(0.48)
section.right_margin = Inches(0.48)
normal = doc.styles["Normal"]
normal.font.name = "Arial"
normal.font.size = Pt(8.75)
normal.paragraph_format.space_after = Pt(0)

name = doc.add_paragraph()
name.alignment = WD_ALIGN_PARAGRAPH.CENTER
name.paragraph_format.space_after = Pt(0.5)
font(name.add_run("Raymond Frias-Amaro"), 22, bold=True, color=BLUE)

contact = doc.add_paragraph()
contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
contact.paragraph_format.space_after = Pt(3)
font(contact.add_run("rfrias1869@gmail.com  |  github.com/webDeveloper42  |  raymondfrias.com  |  Suitland, MD 20746"), 8.45, bold=True)

heading(doc, "ENTRY-LEVEL SOFTWARE ENGINEER")
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(1)
p.paragraph_format.line_spacing = 1.0
font(p.add_run("Entry-level software engineer with hands-on experience building and deploying full-stack MERN applications from concept to production. Ready to bring full-stack ownership to an entry-level software engineering or help desk support role. Bilingual: English and Spanish."), 8.55)

heading(doc, "EDUCATION")
role_line(doc, "Software Engineer Certificate, TripleTen", "Graduated April 2026")

heading(doc, "TECHNICAL SKILLS")
text_line(doc, "Languages & Frameworks", "Python, JavaScript, HTML5, CSS3, React, Node.js, Express, Flask, Jinja")
text_line(doc, "Data & APIs", "MySQL, SQLite, SQLAlchemy ORM, MongoDB, RESTful API design, third-party API integration")
text_line(doc, "Tools & Practices", "Git, GitHub Actions, Render, responsive web design, OOP, BEM, accessibility, pytest, Ruff, Bandit, CI/CD")

heading(doc, "KEY SKILLS")
text_line(doc, "Communication", "Bilingual in English and Spanish; clear written and verbal communication")
text_line(doc, "Problem-Solving", "Self-directed troubleshooting and debugging across the full application stack")
text_line(doc, "Collaboration & Leadership", "Cross-functional teamwork; leadership and integrity built through Eagle Scout achievement")
text_line(doc, "Work Style", "Adaptable, fast learner, detail-oriented, strong time management on self-managed projects")

heading(doc, "PROFESSIONAL EXPERIENCE")
role_line(doc, "Software Engineer, Founder of Discover Yourself Website", "10/2025 - Present")
link_line(doc, "discover-yourself.app")
for item in [
    "Architected and launched a full-stack MERN web application from concept to a live, monetized product using HTML, CSS, JavaScript, and React to deliver a responsive user experience.",
    "Engineered RESTful APIs with Express and MongoDB to connect the React frontend, enabling secure user accounts and reliable data access.",
    "Automated cloud deployment through GitHub Actions CI/CD pipelines, streamlining releases to Render and improving deployment reliability.",
    "Strengthened backend security and search visibility by applying Node.js best practices and SEO optimization techniques.",
]:
    bullet(doc, item)

role_line(doc, "Software Engineer, TicketDesk System - Discover Yourself Website", "09/2026 - Present")
link_line(doc, "Local IT service management application")
for item in [
    "Built a role-based ticketing system with Python, Flask, SQLAlchemy, SQLite, Jinja, and BEM CSS for incident intake, searchable queues, assignment, SLA tracking, comments, and audit history.",
    "Applied OOP, application factories, blueprints, and a service layer to separate HTTP handling, ticket workflows, persistence, and presentation concerns.",
    "Implemented requester, agent, and administrator permissions with PBKDF2 password hashing, CSRF protection, parameterized ORM queries, validation, and restrictive security headers.",
    "Created an idempotent local setup script that generates secrets, initializes and seeds SQLite, and launches the application through a Python virtual environment.",
    "Built 20 model, integration, workflow, and abuse-case tests reaching 91% coverage; added Ruff and Bandit checks plus a risk-based exploratory QA plan.",
]:
    bullet(doc, item)

heading(doc, "AWARDS")
role_line(doc, "Eagle Scout Certificate, Boy Scouts of America, Troop 1869, Washington DC", "01/2010 - 01/2018")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUTPUT)
