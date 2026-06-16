from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LanguageFlashcardDeckCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    language: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("name", "language", "description", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None

        return value


class LanguageFlashcardDeckUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    language: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("name", "language", "description", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None

        return value


class LanguageFlashcardDeckResponse(BaseModel):
    id: str
    name: str
    language: str
    description: str | None
    card_count: int = Field(serialization_alias="cardCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class LanguageFlashcardDeckListResponse(BaseModel):
    items: list[LanguageFlashcardDeckResponse]


class LanguageFlashcardCardCreateRequest(BaseModel):
    front: str = Field(min_length=1, max_length=500)
    back: str = Field(min_length=1, max_length=500)
    example_sentence: str | None = Field(
        default=None,
        validation_alias="exampleSentence",
        max_length=1000,
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("front", "back", "example_sentence", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None

        return value


class LanguageFlashcardCardUpdateRequest(BaseModel):
    front: str | None = Field(default=None, min_length=1, max_length=500)
    back: str | None = Field(default=None, min_length=1, max_length=500)
    example_sentence: str | None = Field(
        default=None,
        validation_alias="exampleSentence",
        max_length=1000,
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("front", "back", "example_sentence", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None

        return value


class LanguageFlashcardCardResponse(BaseModel):
    id: str
    deck_id: str = Field(serialization_alias="deckId")
    front: str
    back: str
    example_sentence: str | None = Field(serialization_alias="exampleSentence")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class LanguageFlashcardCardListResponse(BaseModel):
    items: list[LanguageFlashcardCardResponse]


class LanguageFlashcardDeckDetailResponse(BaseModel):
    deck: LanguageFlashcardDeckResponse
    cards: list[LanguageFlashcardCardResponse]


class LanguageFlashcardSessionResponse(BaseModel):
    id: str
    deck_id: str = Field(serialization_alias="deckId")
    total_cards: int = Field(serialization_alias="totalCards")
    started_at: datetime = Field(serialization_alias="startedAt")
    cards: list[LanguageFlashcardCardResponse]

    model_config = ConfigDict(from_attributes=True)


class LanguageFlashcardReviewItemRequest(BaseModel):
    card_id: str = Field(validation_alias="cardId", min_length=1)
    is_known: bool = Field(validation_alias="isKnown")

    model_config = ConfigDict(extra="forbid")


class LanguageFlashcardReviewSubmitRequest(BaseModel):
    reviews: list[LanguageFlashcardReviewItemRequest] = Field(min_length=1)

    model_config = ConfigDict(extra="forbid")


class LanguageFlashcardReviewSummaryResponse(BaseModel):
    session_id: str = Field(serialization_alias="sessionId")
    total_cards: int = Field(serialization_alias="totalCards")
    known: int
    unknown: int
    accuracy: int
    completed_at: datetime = Field(serialization_alias="completedAt")
