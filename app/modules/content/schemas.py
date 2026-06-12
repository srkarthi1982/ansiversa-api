from pydantic import BaseModel


class PrincipleCard(BaseModel):
    title: str
    points: list[str]


class PersonInfo(BaseModel):
    kicker: str
    title: str
    image: str | None = None
    imageAlt: str
    paragraphs: list[str]


class CommunityCard(BaseModel):
    title: str
    points: list[str]


class FutureAction(BaseModel):
    label: str
    path: str
    primary: bool


class TimelineItem(BaseModel):
    date: str
    title: str
    description: str


class StorySection(BaseModel):
    kicker: str
    title: str
    paragraphs: list[str]


class PrinciplesSection(BaseModel):
    kicker: str
    title: str
    description: str
    cards: list[PrincipleCard]


class PartnershipSection(BaseModel):
    kicker: str
    title: str
    paragraphs: list[str]


class CommunitySection(BaseModel):
    kicker: str
    title: str
    description: str
    cards: list[CommunityCard]


class ProblemSection(BaseModel):
    kicker: str
    title: str
    description: str
    points: list[str]


class FutureSection(BaseModel):
    kicker: str
    title: str
    paragraphs: list[str]
    actions: list[FutureAction]


class TimelineSection(BaseModel):
    kicker: str
    title: str
    description: str
    items: list[TimelineItem]


class AboutResponse(BaseModel):
    story: StorySection
    principles: PrinciplesSection
    people: list[PersonInfo]
    partnership: PartnershipSection
    community: CommunitySection
    problem: ProblemSection
    future: FutureSection
    timeline: TimelineSection


class MetadataCreateRequest(BaseModel):
    content: dict | None = None


class LegalSection(BaseModel):
    title: str
    paragraphs: list[str]


class LegalResponse(BaseModel):
    title: str
    description: str
    sections: list[LegalSection]


class MetadataResponse(BaseModel):
    key: str
    content: dict | None = None


class MetadataListResponse(BaseModel):
    items: list[MetadataResponse]
    total: int


class HomeAction(BaseModel):
    label: str
    path: str
    primary: bool


class HomeCard(BaseModel):
    title: str
    description: str
    points: list[str] | None = None


class HeroSection(BaseModel):
    kicker: str
    title: str
    description: str
    actions: list[HomeAction]


class EcosystemSection(BaseModel):
    kicker: str
    title: str
    description: str
    cards: list[HomeCard]


class CreatorsSection(BaseModel):
    kicker: str
    title: str
    description: str
    cards: list[HomeCard]


class AudienceSection(BaseModel):
    kicker: str
    title: str
    description: str
    cards: list[HomeCard]


class GettingStartedSection(BaseModel):
    kicker: str
    title: str
    description: str
    steps: list[HomeCard]


class FounderPerson(BaseModel):
    name: str
    role: str
    description: str
    image: str | None = None


class FoundersSection(BaseModel):
    people: list[FounderPerson]
    summary: str


class HomeResponse(BaseModel):
    hero: HeroSection
    ecosystem: EcosystemSection
    creators: CreatorsSection
    audience: AudienceSection
    gettingStarted: GettingStartedSection
    founders: FoundersSection


class PricingAction(BaseModel):
    label: str
    path: str
    primary: bool


class PricingHeroSection(BaseModel):
    kicker: str
    title: str
    description: str
    actions: list[PricingAction]


class PricingPlan(BaseModel):
    name: str
    description: str
    price: str
    suffix: str
    features: list[str]
    action: PricingAction


class PricingIncludedSection(BaseModel):
    kicker: str
    title: str
    description: str
    features: list[str]


class PricingComparisonRow(BaseModel):
    plan: str
    bestFor: str
    price: str
    apps: str
    support: str


class PricingComparisonSection(BaseModel):
    kicker: str
    title: str
    description: str
    columns: list[str]
    rows: list[PricingComparisonRow]


class PricingResponse(BaseModel):
    hero: PricingHeroSection
    plans: list[PricingPlan]
    included: PricingIncludedSection
    comparison: PricingComparisonSection
