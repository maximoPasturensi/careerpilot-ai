from pydantic import BaseModel, Field
from typing import Optional, Literal

class Experience(BaseModel):
    company: str = Field(..., description = "Nombre de la empresa.")
    role: str = Field(..., description = "Cargo/Puesto ocupado")
    start_date: str = Field(..., description = "Fecha de inicio, formato 'MMM YYYY'")
    end_date: Optional[str] = Field(None, description = "Fecha de fin, 'MMM YYYY o None si es actual'")
    is_current: bool = Field(default=False, description= "True, si es el puesto actual")
    bullets: list[str] = Field(
        default_factory = list,
        description = "Logros/responsabilidades, idealmente redactados en formato STAR"
    )

class Education(BaseModel):
    institution: str = Field(..., description= "Nombre de la institucion educativa")
    degree: str = Field(..., description= "Titulo o carrera obtenida/ en curso")
    field_of_study: Optional[str] = Field(None, description= "Area de estudio, si difiere del titulo")
    end_date: Optional[str] = Field(None, description="Año/fecha de finalizacion, o None si esta en curso")

class Skill(BaseModel):
    name: str = Field(..., description="Nombre de la habilidad,ej. 'Python o Liderazgo de equipos'")
    category: Literal["hard", "soft", "tool", "language"] = Field(
        ..., description= "Categoria de la habilidad"
    )

class CVProfile(BaseModel):
    full_name: str = Field(..., description= "Nombre completo del candidato")
    headline: Optional[str] = Field(None, description="Titulo profesional breve, ej 'Data Analyst'")
    summary: Optional[str] = Field(None, description="Resumen profesional de 2-3 lineas")
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)

class JobDescription(BaseModel):
    job_title: str = Field(..., description="Titulo del puesto ofertado")
    company_name: Optional[str] = Field(None, description="Nombre de la empresa, si esta disponible")
    seniority_level: Optional[str] = Field (
        None, description="Nivel del puesto, ej. 'Junior', 'Semi-senior', 'Senior'"
    )

    location: Optional[str] = Field(None, description="Ciudad/pais de la oferta, si especifica")
    remote_type: Optional[Literal["remoto", "hibrido", "presencial"]] = Field(
        None, description="Modalidad de trabajo"
    )

    salary_range: Optional[str] = Field(
        None, description="Rango salarial mencionado, como texto libre (ej. 'USD 1500-2000')"
    )

    responsibilities: list[str] = Field(
        default_factory=list, description="Principales responsabilidades del puesto"
    )

    required_hard_skills: list[str] = Field(
        default_factory=list, description="Habilidades tecnicas requeridas o deseadas"
    )

    required_soft_skills: list[str] = Field(
        default_factory=list, description="Habilidades blandas requeridas o deseadas"
    )

class SkillJudgment(BaseModel):
    required_skill: str = Field(..., description="El skill requerido que se esta evaluando")
    is_match: bool = Field(..., description="True si el candidato tiene esta skill o una equivalente real")
    matched_cv_skill: Optional[str] = Field(
        None, description="El skill del CV que cubre este requisito, si is_match es True"
    )
    reasoning: str = Field(..., description="Justificacion breve (1 frase) de la decision")

class GapAnalysisJudgment(BaseModel):
    judgments: list[SkillJudgment]

class MatchResult(BaseModel):
    overall_score: float = Field(..., description="Score de compatibilidad global, 0-100")
    hard_skills_score: float = Field(..., description="Score solo de hard skills, 0-100")
    soft_skills_score: float = Field(..., description="Score solo de soft skills, 0-100")
    hard_skills_detail: list[dict] = Field(default_factory=list)
    soft_skills_detail: list[dict] = Field(default_factory=list)
    missing_keywords: list[str] = Field(
        default_factory=list, description="Skills requeridos que representan gaps reales"
    )

class AdaptedBullet(BaseModel):
    original: str = Field(..., description="El bullet original del CV, sin modificar")
    adapted: str = Field(..., description="Version reescrita en formato STAR, alineada a la oferta")

class AdaptedExperience(BaseModel):
    company: str
    role: str
    start_date: str
    end_date: Optional[str] = None
    is_current: bool = False
    bullets: list[AdaptedBullet] = Field(default_factory=list)

class AdaptedCV(BaseModel):
    full_name: str
    headline: str = Field(..., description="Headline adaptado al puesto ej. 'Data Engineer' en vez de generico")
    summary: str = Field(..., description="Resumen de 2-3 lineas reescrito para alinear con la oferta")
    experience: list[AdaptedExperience]
    education: list[Education]
    highlighted_skills: list[str] = Field(
        ..., description="Skills del candidate reordenados por relevancia para esta oferta especifica"
    )

class CoverLetter(BaseModel):
    opening: str = Field(..., description="Parrafe de apertura: quien es el candidato y por que escribe")
    body: str = Field(..., description="Parrafo(s) centrales: por que encaja con el puesto, con ejemplos concretos")
    closing: str = Field(..., description="Cierre: llamado a la accion, agradecimiento")
    tone_used: str = Field(..., description="Tono aplicado, ej: 'formal corporativo' o 'cercano y directo'")

class InterviewQA(BaseModel):
    question: str = Field(..., description="Pregunta probable de la entrevista")
    question_type: Literal["technical", "behavioral"] = Field(
        ..., description="Tipo de pregunta"
    )
    suggested_answer: str = Field(
        ..., description="Respuesta sugerida basada en la experiencia REAL del candidato"
    )
    tip: str = Field(
        ..., description="Consejo breve de como presentar la respuesta (1 frase)"
    )

class InterviewKit(BaseModel):
    questions: list[InterviewQA] = Field(..., description="5 preguntas probables con respuestas sugeridas")
    preparation_note: str = Field(
        ..., description="Nota breve sobre en que areas deberia reforzar la preparacion el candidato"
    )

class PipelineResult(BaseModel):
    cv_profile: CVProfile
    job_description: JobDescription
    match_result: MatchResult
    adapted_cv: AdaptedCV
    cover_letter: CoverLetter
    interview_kit: InterviewKit
    processing_time_seconds: float = Field(
        ..., description="Tiempo total de procesamiento, para la metrica de ahorro de tiempo"
    )