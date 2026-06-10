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


class MetadataResponse(BaseModel):
    key: str
    content: dict | None = None


class MetadataListResponse(BaseModel):
    items: list[MetadataResponse]
    total: int