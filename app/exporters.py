from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import plotly.graph_objects as go
from rapidfuzz import fuzz

from app.models import AdaptedCV, CoverLetter, CVProfile, JobDescription, MatchResult

styles = getSampleStyleSheet()
h1_style = ParagraphStyle("H1", parent=styles["Heading1"], spaceAfter=6)
h2_style = ParagraphStyle("H2", parent=styles["Heading2"], spaceAfter=4, spaceBefore=10)
body_style = ParagraphStyle("Body", parent=styles["Normal"], spaceAfter=6, leading=14)

def generate_cv_pdf(adapted: AdaptedCV) -> bytes:
    """Genera el CV adaptado como PDF descargable, listo para enviar."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.6 * inch, bottomMargin= 0.6 * inch)
    story = []

    story.append(Paragraph(adapted.full_name, h1_style))
    story.append(Paragraph(adapted.headline, styles["Italic"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(adapted.summary, body_style))

    story.append(Paragraph("Experiencia", h2_style))
    for exp in adapted.experience:
        end = exp.end_date or "Actual"
        story.append(Paragraph(f"<b>{exp.role}</b> - {exp.company} ({exp.start_date} - {end})", body_style))
        for bullet in exp.bullets:
            story.append(Paragraph(f"• {bullet.adapted}", body_style))
        story.append(Spacer(1, 6))

    story.append(Paragraph("Educacion", h2_style))
    for edu in adapted.education:
        end = edu.end_date or "En curso"
        story.append(Paragraph(f"<b>{edu.degree}</b> - {edu.institution} ({end})", body_style))

    story.append(Paragraph("Skills destacados", h2_style))
    story.append(Paragraph(",".join(adapted.highlighted_skills), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def compute_ats_keyword_coverage(adapted: AdaptedCV, job: JobDescription) -> dict:
    """% de keywords de la oferta que aparecen (literal o casi-literal) en el CV adaptado.
    Es una aproximacion simple tipo ATS real, no usa el LLM-judge del matching engine."""
    cv_full_text = (
        adapted.summary + " " + adapted.headline + " " +
        " ".join(adapted.highlighted_skills) + " " +
        " ".join(b.adapted for exp in adapted.experience for b in exp.bullets)
    ).lower()

    all_keywords = job.required_hard_skills + job.required_soft_skills
    if not all_keywords:
        return {"coverage_pct": 100.0, "matched": [], "missing": []}

    matched, missing = [], []
    for kw in all_keywords:
        found = fuzz.partial_ratio(kw.lower(), cv_full_text) >= 80
        (matched if found else missing).append(kw)

    coverage_pct = round((len(matched) / len(all_keywords)) * 100, 1)
    return {"coverage_pct": coverage_pct, "matched": matched, "missing": missing}

def _estimate_experience_alignment(cv: CVProfile, job: JobDescription) -> float:
    """HEURISTICA simple, no un score validado: aproxima alineacion de experiencia comparando
    cantidad de experiencias relevantes del candidato contra el seniority pedido.
    No reemplaza un analisis real de años de experiencia"""
    num_experiences = len(cv.experience)
    if job.seniority_level and "junior" in job.seniority_level.lower():
        target = 1
    elif job.seniority_level and "senior" in job.seniority_level.lower():
        target = 3
    else:
        target = 2 # semi senior

    ratio = min(num_experiences / target, 1.0) if target else 1.0
    return round(ratio * 100, 1)

def _estimate_domain_alignment(cv: CVProfile, job: JobDescription) -> float:
    """HEURISTICA simple, no un score validado: similitud textual entre el resumen/headline
    del candidato y el titulo + responsabilidades del puesto."""
    cv_text = f"{cv.headline or ''} {cv.summary or ''}".lower()
    job_text = f"{job.job_title} {' '.join(job.responsibilities)}".lower()
    score = fuzz.token_set_ratio(cv_text, job_text)
    return round(score, 1)

def build_radar_chart(match: MatchResult, cv: CVProfile, job: JobDescription) -> go.Figure:
    """Radar de 4 ejes: 2 con datos reales del matching engine, 2 con heuristicas aproximadas."""
    exp_score = _estimate_experience_alignment(cv, job)
    domain_score = _estimate_domain_alignment(cv, job)

    categories = ["Hard Skills", "Soft Skills", "Experiencia (aprox.)", "Alineacion de Dominio (aprox.)"]
    values = [match.hard_skills_score, match.soft_skills_score, exp_score, domain_score]
    values += values[:1]
    categories += categories[:1]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories, fill="toself", name="Compatibilidad"
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig