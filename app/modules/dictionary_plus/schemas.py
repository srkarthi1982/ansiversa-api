from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = " ".join(value.strip().split())
        return normalized or None

    return value


def _normalize_saved_word_ids(value: object) -> object:
    if isinstance(value, list):
        seen: set[str] = set()
        normalized: list[str] = []
        for item in value:
            word_id = str(item).strip()
            if word_id and word_id not in seen:
                seen.add(word_id)
                normalized.append(word_id)
        return normalized

    return value


class DictionaryWordPayload(BaseModel):
    word: str = Field(min_length=1, max_length=120)
    definition: str = Field(min_length=1, max_length=3000)
    pronunciation: str | None = Field(default=None, max_length=120)
    part_of_speech: str | None = Field(
        default=None,
        validation_alias="partOfSpeech",
        max_length=80,
    )
    example_sentence: str | None = Field(
        default=None,
        validation_alias="exampleSentence",
        max_length=1000,
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator(
        "word",
        "definition",
        "pronunciation",
        "part_of_speech",
        "example_sentence",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class DictionaryLookupCreateRequest(DictionaryWordPayload):
    pass


class SavedWordCreateRequest(DictionaryWordPayload):
    lookup_id: str | None = Field(
        default=None,
        validation_alias="lookupId",
        max_length=36,
    )

    @field_validator("lookup_id", mode="before")
    @classmethod
    def normalize_lookup_id(cls, value: object) -> object:
        return _normalize_text(value)


class DictionaryLookupResponse(BaseModel):
    id: str
    word: str
    definition: str
    pronunciation: str | None
    part_of_speech: str | None = Field(serialization_alias="partOfSpeech")
    example_sentence: str | None = Field(serialization_alias="exampleSentence")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class DictionaryLookupListResponse(BaseModel):
    items: list[DictionaryLookupResponse]


class SavedWordResponse(BaseModel):
    id: str
    lookup_id: str | None = Field(serialization_alias="lookupId")
    word: str
    definition: str
    pronunciation: str | None
    part_of_speech: str | None = Field(serialization_alias="partOfSpeech")
    example_sentence: str | None = Field(serialization_alias="exampleSentence")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class SavedWordListResponse(BaseModel):
    items: list[SavedWordResponse]


class WordListCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=140)
    description: str | None = Field(default=None, max_length=1000)
    saved_word_ids: list[str] = Field(
        default_factory=list,
        validation_alias="savedWordIds",
        max_length=200,
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("saved_word_ids", mode="before")
    @classmethod
    def normalize_saved_word_ids(cls, value: object) -> object:
        return _normalize_saved_word_ids(value)


class WordListUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=140)
    description: str | None = Field(default=None, max_length=1000)
    saved_word_ids: list[str] | None = Field(
        default=None,
        validation_alias="savedWordIds",
        max_length=200,
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("saved_word_ids", mode="before")
    @classmethod
    def normalize_saved_word_ids(cls, value: object) -> object:
        return _normalize_saved_word_ids(value)


class WordListResponse(BaseModel):
    id: str
    title: str
    description: str | None
    saved_word_ids: list[str] = Field(serialization_alias="savedWordIds")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class WordListsResponse(BaseModel):
    items: list[WordListResponse]
