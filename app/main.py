import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import tempfile
from app.pipeline import run_full_pipeline
from app.cv_parser import extract_raw_text
import re
from app.exporters import (
    generate_cv_pdf, generate_cover_letter_pdf,
    compute_ats_keyword_coverage, build_radar_chart
)

def format_star_bullet(text: str) -> str:
    """Convierte 'Situacion: ... Tarea: ... Accion: ... Resultado: ...' en viñetas Markdown."""
    labels = ["Situacion", "Situacion", "Tarea", "Accion", "Accion", "Resultado"]
    pattern = r"(?=(?:" + "|".join(labels) + r"):)"
    parts = [p.strip() for p in re.split(pattern, text) if p.strip()]
    return "\n".join(f"- {p}" for p in parts)

st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 CareerPilot AI")
st.caption("Copiloto de busqueda laboral - de 45 minutos a segundos por postulacion")

# --- SIDEBAR: INPUTS ---
with st.sidebar:
    st.header("1. Tu CV")
    cv_input_mode = st.radio("¿Cómo querés cargar tu CV?", ["Subir archivo", "Pegar texto"])

    cv_raw_text = None
    if cv_input_mode == "Subir archivo":
        uploaded_file = st.file_uploader("PDF o Markdown", type=["pdf", "md", "txt"])
    else:
        cv_raw_text = st.text_area("Pega el texto de tu CV", height=200)

    st.header("2. Oferta laboral")
    job_raw_text = st.text_area("Pega el texto de la oferta", height=200)

    analyze_button = st.button("🔍 Analizar", type="primary", use_container_width=True)

# --- LOGICA DEL BOTON ANALIZAR ---
if analyze_button:
    # resolvemos el texto del cv segun el modo elegido
    if cv_input_mode == "Subir archivo":
        if uploaded_file is None:
            st.error("Subi un archivo de CV antes de analizar.")
            st.stop()
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        final_cv_text = extract_raw_text(tmp_path)
    else:
        if not cv_raw_text or not cv_raw_text.strip():
            st.error("Pega el texto de tu CV antes de analizar.")
            st.stop()
        final_cv_text = cv_raw_text

    if not job_raw_text or not job_raw_text.strip():
        st.error("Pega el texto de la oferta laboral antes de analizar.")
        st.stop()

    with st.spinner("Analizando tu CV y la oferta... esto toma unos segundos ⏳"):
        result = run_full_pipeline(final_cv_text, job_raw_text)
        st.session_state["pipeline_result"] = result

# --- AREA PRINCIAPL : MOSTRAR RESULTADOS SI YA HAY UNO GUARDADO
if "pipeline_result" in st.session_state:
    result = st.session_state["pipeline_result"]

    st.success(f"✅ Análisis completo en {result.processing_time_seconds}s")

    col1, col2, col3 = st.columns(3)
    col1.metric("Score de compatibilidad", f"{result.match_result.overall_score}%")
    col2.metric("Tiempo de procesamiento", f"{result.processing_time_seconds}s", "vs 45 min manual")
    col3.metric("Keywords faltantes", len(result.match_result.missing_keywords))

    st.write("**Gaps detectados:**", ", ".join(result.match_result.missing_keywords) or "Ninguno 🎉")

    st.divider()

    tab_cv, tab_letter, tab_interview, tab_detail = st.tabs(
        ["📝 CV Adaptado","✉️ Cover Letter","🎤 Kit de Entrevista","🔍 Detalle del Match"]
    )

    # --- TAB1: CV ADAPTADO (antes/despues) ---
    with tab_cv:
        adapted = result.adapted_cv
        st.subheader(adapted.headline)
        st.write(adapted.summary)
        st.write("**Skills destacados:**", ",".join(adapted.highlighted_skills))

        cv_pdf_bytes = generate_cv_pdf(adapted)
        st.download_button(
            "📄 Descargar CV adaptado (PDF)",
            data=cv_pdf_bytes,
            file_name=f"CV_{adapted.full_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
        )

        st.divider()
        ats = compute_ats_keyword_coverage(adapted, result.job_description)
        st.caption("🎯 Cobertura de keywords ATS (aproximado)")
        st.progress(ats["coverage_pct"] / 100)
        st.write(f"**{ats['coverage_pct']}%** de las keywords de la oferta aparecen en tu CV adaptado")
        if ats["missing"]:
            st.caption(f"Faltantes: {', '.join(ats['missing'])}")

        st.divider()

        for exp in adapted.experience:
            st.markdown(f"**{exp.role}** @ {exp.company}")
            for bullet in exp.bullets:
                col_before, col_after = st.columns(2)
                with col_before:
                    st.caption("Antes")
                    st.write(bullet.original)
                with col_after:
                    st.caption("Despues")
                    st.markdown(format_star_bullet(bullet.adapted))
            st.divider()

    # --- TAB 2: COVAER LETTER ---
    with tab_letter:
        letter = result.cover_letter
        st.caption(f"Tono: {letter.tone_used}")
        st.write(letter.opening)
        st.write(letter.body)
        st.write(letter.closing)

        letter_pdf_bytes = generate_cover_letter_pdf(letter, result.cv_profile.full_name)
        st.download_button(
            "✉️ Descargar Cover Letter (PDF)",
            data=letter_pdf_bytes,
            file_name=f"CoverLetter_{result.cv_profile.full_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
        )

    # --- TAB3: KIT DE ENTREVISTA ---
    with tab_interview:
        kit = result.interview_kit
        st.info(kit.preparation_note)
        for qa in kit.questions:
            badge = "🔧" if qa.question_type == "technical" else "🤝"
            with st.expander(f"{badge} {qa.question}"):
                st.write(qa.suggested_answer)
                st.caption(f"💡 Tip: {qa.tip}")

    # --- TAB4: DETALLE DEL MATCH (gap analysis completo) ---
    with tab_detail:
        match= result.match_result

        st.subheader("📡 Radar de compatibilidad")
        radar_fig = build_radar_chart(match, result.cv_profile, result.job_description)
        st.plotly_chart(radar_fig, use_container_width=True)
        st.caption("Hard Skills y Soft skills son scores calculados por el matching engine."
                   "Experiencia y Alineacion de Dominio son estimaciones aproximadas")

        st.divider()

        col_hard, col_soft = st.columns(2)
        col_hard.metric("Hard skills", f"{match.hard_skills_score}%")
        col_soft.metric("Soft skills", f"{match.soft_skills_score}%")

        st.subheader("Hard skills")
        for r in match.hard_skills_detail:
            icon = "❌" if r["is_gap"] else "✅"
            st.write(f"{icon} **{r['required_skill']}** — {r.get('reasoning', '')}")

        st.subheader("Soft skills")
        for r in match.soft_skills_detail:
            icon = "❌" if r["is_gap"] else "✅"
            st.write(f"{icon} **{r['required_skill']}** - {r.get('reasoning', '')}")

else:
    st.info("👈 Cargá tu CV y la oferta laboral en la barra lateral, y tocá 'Analizar' para empezar.")