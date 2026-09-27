"""Typed contracts between pipeline stages (and the schemas LLM output must match)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

EvidenceStatus = Literal["verified", "estimate", "inference", "unknown"]
Strategy = Literal["refurb", "extension", "split"]
VerdictCode = Literal["VIABLE", "CONDITIONAL", "NOT_VIABLE", "EXCLUDED", "INSUFFICIENT_EVIDENCE"]


# ---------- input ----------

class CaseInput(BaseModel):
    """One property to analyse. Anything the listing parser can't get can be given here."""

    case_id: str
    url: str | None = None
    address: str | None = None
    postcode: str | None = None
    asking_price: float | None = None
    tenure: str | None = None
    property_type: str | None = None  # detached | semi | terrace | end-terrace | bungalow | flat
    floor_area_m2: float | None = None
    bedrooms: int | None = None
    description: str | None = None
    photos: list[str] = Field(default_factory=list)          # local paths or URLs
    floorplans: list[str] = Field(default_factory=list)
    historical_images: list[str] = Field(default_factory=list)  # local paths, name must include year
    title_checked: bool = False  # True once the HMLR title register confirms freehold
    notes: str | None = None


# ---------- property ----------

class Property(BaseModel):
    case_id: str
    listing_url: str | None = None
    address: str | None = None
    house_number: str | None = None
    street: str | None = None
    postcode: str | None = None
    outward_code: str | None = None
    lat: float | None = None
    lon: float | None = None
    uprn: str | None = None
    asking_price: float | None = None
    tenure: str | None = None
    property_type: str | None = None
    floor_area_m2: float | None = None
    bedrooms: int | None = None
    description: str | None = None
    photos: list[str] = Field(default_factory=list)
    floorplans: list[str] = Field(default_factory=list)
    historical_images: list[str] = Field(default_factory=list)
    title_checked: bool = False
    identity_confidence: Literal["high", "medium", "low"] = "low"


class Constraints(BaseModel):
    conservation_area: bool | None = None
    listed_subject: bool | None = None
    listed_adjacent: bool | None = None
    article_4: bool | None = None
    tpo: bool | None = None
    flood_zone: int | None = None
    green_belt: bool | None = None
    plot_area_m2: float | None = None
    plot_frontage_m: float | None = None
    freehold_polygon_found: bool | None = None


# ---------- planning ----------

Readability = Literal["readable", "partial", "unreadable", "missing"]
Relation = Literal["subject", "adjoining", "opposite", "street", "nearby"]


class PlanningDoc(BaseModel):
    doc_id: str
    title: str | None = None
    path: str | None = None
    url: str | None = None


class PlanningApp(BaseModel):
    ref: str
    address: str | None = None
    description: str | None = None
    decision: str | None = None
    decision_date: str | None = None
    received_date: str | None = None
    app_type: str | None = None
    relation: Relation = "nearby"
    distance_m: float | None = None
    documents: list[PlanningDoc] = Field(default_factory=list)
    readability: Readability = "readable"


class TriageItem(BaseModel):
    ref: str
    relevance: Literal["material", "routine", "uncertain"]
    flip_link: Literal["refurb", "extension", "split", "value", "none"]
    reason: str


class TriageBatch(BaseModel):
    items: list[TriageItem]


class Citation(BaseModel):
    doc_id: str
    page: int


class ConditionItem(BaseModel):
    text: str
    removes_pd_rights: bool
    citation: Citation


class DeepDive(BaseModel):
    ref: str
    decision: str | None
    decision_date: str | None
    scheme_type: Literal["rear_extension", "side_extension", "loft", "new_dwelling", "conversion",
                         "demolition_rebuild", "other"]
    approved_depth_m: float | None = None
    approved_height_m: float | None = None
    conditions: list[ConditionItem] = Field(default_factory=list)
    refusal_reasons: list[str] = Field(default_factory=list)
    officer_reasoning: list[str] = Field(default_factory=list)
    status: Literal["implemented", "lapsed", "superseded", "extant", "unknown"] = "unknown"
    citations: list[Citation] = Field(default_factory=list)


class PlanningResult(BaseModel):
    apps: list[PlanningApp] = Field(default_factory=list)
    triage: dict[str, TriageItem] = Field(default_factory=dict)
    deep_dives: dict[str, DeepDive] = Field(default_factory=dict)
    pd_rights_removed: bool | None = None
    precedent: dict[str, dict] = Field(default_factory=dict)  # scheme_type -> stats
    snapshot_at: str | None = None


# ---------- imagery / condition ----------

class ImageryObservation(BaseModel):
    change: str
    first_seen_image: str
    date_range: str
    confidence: Literal["low", "medium", "high"]


class ImageryResult(BaseModel):
    images: list[dict] = Field(default_factory=list)  # {path, date, source}
    observations: list[ImageryObservation] = Field(default_factory=list)
    unmatched_changes: list[str] = Field(default_factory=list)


class AreaGrade(BaseModel):
    area: str
    grade: int = Field(ge=1, le=4)  # 1 = good, 4 = very poor
    evidence: str
    photo_index: int | None = None


class ConditionAssessment(BaseModel):
    grades: list[AreaGrade]
    structural_concern: bool
    notes: str


# ---------- valuation ----------

class Comp(BaseModel):
    address: str
    postcode: str | None = None
    date: str
    price: float
    property_type: str | None = None
    tenure: str | None = None
    floor_area_m2: float | None = None
    distance_m: float | None = None
    weight: float = 1.0
    excluded: bool = False
    exclusion_reason: str | None = None

    @property
    def ppsm(self) -> float | None:
        if self.floor_area_m2 and self.floor_area_m2 > 0:
            return self.price / self.floor_area_m2
        return None


class CompAdjustment(BaseModel):
    action: Literal["exclude", "weight", "flag"]
    comp_index: int | None = None
    weight: float | None = None
    reason: str


class CompReview(BaseModel):
    adjustments: list[CompAdjustment]
    comment: str


class Valuation(BaseModel):
    comps: list[Comp] = Field(default_factory=list)
    ppsm_median: float | None = None
    ppsm_as_is: float | None = None
    ppsm_refurbished: float | None = None
    street_ceiling: float | None = None
    value_as_is: float | None = None
    value_refurbished: float | None = None
    pre_review_value_refurbished: float | None = None
    review_comment: str | None = None
    review_shift: float | None = None
    search_widened: bool = False


# ---------- schemes / appraisal / verdict ----------

class Scheme(BaseModel):
    strategy: Strategy
    feasible: bool | None  # None = can't tell from the evidence
    route: str
    gdv: float | None = None
    works_cost: float | None = None
    added_area_m2: float | None = None
    planning_fee: float = 0
    months: int | None = None
    notes: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    consent_required: bool = False


class Appraisal(BaseModel):
    strategy: Strategy
    gdv: float
    max_price: float | None
    profit_at_asking: float | None
    poc_at_asking: float | None
    total_cost_at_asking: float | None
    months: int
    cost_lines_at_asking: dict[str, float] = Field(default_factory=dict)
    sensitivity: list[dict] = Field(default_factory=list)
    stress_profit_at_asking: float | None = None
    stress_max_price: float | None = None  # price at which the downside case breaks even


class Verdict(BaseModel):
    code: VerdictCode
    best_strategy: Strategy | None = None
    max_price: float | None = None
    reasons: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)


class ReportNarrative(BaseModel):
    summary: str
    key_risks: list[str]
    pre_exchange_checks: list[str]
