import json

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.dictionary_plus.models import DictionaryLookup, SavedWord, WordList
from app.modules.dictionary_plus.schemas import (
    DictionaryLookupCreateRequest,
    DictionaryLookupResponse,
    SavedWordCreateRequest,
    SavedWordResponse,
    WordListCreateRequest,
    WordListResponse,
    WordListUpdateRequest,
)


def _lookup_response(lookup: DictionaryLookup) -> DictionaryLookupResponse:
    return DictionaryLookupResponse.model_validate(lookup)


def _saved_word_response(saved_word: SavedWord) -> SavedWordResponse:
    return SavedWordResponse.model_validate(saved_word)


def _decode_saved_word_ids(value: str | None) -> list[str]:
    if not value:
        return []

    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        return []

    if not isinstance(decoded, list):
        return []

    seen: set[str] = set()
    ids: list[str] = []
    for item in decoded:
        word_id = str(item).strip()
        if word_id and word_id not in seen:
            seen.add(word_id)
            ids.append(word_id)

    return ids


def _encode_saved_word_ids(value: list[str]) -> str:
    return json.dumps(value, separators=(",", ":"))


def _word_list_response(word_list: WordList) -> WordListResponse:
    return WordListResponse(
        id=word_list.id,
        title=word_list.title,
        description=word_list.description,
        saved_word_ids=_decode_saved_word_ids(word_list.saved_word_ids),
        created_at=word_list.created_at,
        updated_at=word_list.updated_at,
    )


def _get_owned_lookup(db: Session, user: User, lookup_id: str) -> DictionaryLookup:
    lookup = db.get(DictionaryLookup, lookup_id)
    if not lookup or lookup.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary lookup was not found.",
        )

    return lookup


def _get_owned_saved_word(db: Session, user: User, saved_word_id: str) -> SavedWord:
    saved_word = db.get(SavedWord, saved_word_id)
    if not saved_word or saved_word.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved word was not found.",
        )

    return saved_word


def _get_owned_word_list(db: Session, user: User, word_list_id: str) -> WordList:
    word_list = db.get(WordList, word_list_id)
    if not word_list or word_list.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word list was not found.",
        )

    return word_list


def _validate_saved_word_ids(
    db: Session,
    user: User,
    saved_word_ids: list[str],
) -> list[str]:
    if not saved_word_ids:
        return []

    owned_ids = set(
        db.execute(
            select(SavedWord.id).where(
                SavedWord.user_id == user.id,
                SavedWord.id.in_(saved_word_ids),
            )
        )
        .scalars()
        .all()
    )
    missing_ids = [word_id for word_id in saved_word_ids if word_id not in owned_ids]
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Word lists can only contain saved words owned by the current user.",
        )

    return saved_word_ids


def list_lookups(db: Session, user: User) -> list[DictionaryLookupResponse]:
    lookups = list(
        db.execute(
            select(DictionaryLookup)
            .where(DictionaryLookup.user_id == user.id)
            .order_by(DictionaryLookup.updated_at.desc(), DictionaryLookup.word.asc())
        )
        .scalars()
        .all()
    )

    return [_lookup_response(lookup) for lookup in lookups]


def create_lookup(
    db: Session,
    user: User,
    payload: DictionaryLookupCreateRequest,
) -> DictionaryLookupResponse:
    lookup = DictionaryLookup(
        user_id=user.id,
        word=payload.word,
        definition=payload.definition,
        pronunciation=payload.pronunciation,
        part_of_speech=payload.part_of_speech,
        example_sentence=payload.example_sentence,
    )
    db.add(lookup)
    db.commit()
    db.refresh(lookup)

    return _lookup_response(lookup)


def list_saved_words(db: Session, user: User) -> list[SavedWordResponse]:
    saved_words = list(
        db.execute(
            select(SavedWord)
            .where(SavedWord.user_id == user.id)
            .order_by(SavedWord.updated_at.desc(), SavedWord.word.asc())
        )
        .scalars()
        .all()
    )

    return [_saved_word_response(saved_word) for saved_word in saved_words]


def create_saved_word(
    db: Session,
    user: User,
    payload: SavedWordCreateRequest,
) -> SavedWordResponse:
    if payload.lookup_id:
        _get_owned_lookup(db, user, payload.lookup_id)

    saved_word = SavedWord(
        user_id=user.id,
        lookup_id=payload.lookup_id,
        word=payload.word,
        definition=payload.definition,
        pronunciation=payload.pronunciation,
        part_of_speech=payload.part_of_speech,
        example_sentence=payload.example_sentence,
    )
    db.add(saved_word)
    db.commit()
    db.refresh(saved_word)

    return _saved_word_response(saved_word)


def delete_saved_word(db: Session, user: User, saved_word_id: str) -> None:
    saved_word = _get_owned_saved_word(db, user, saved_word_id)
    word_lists = list(
        db.execute(select(WordList).where(WordList.user_id == user.id))
        .scalars()
        .all()
    )
    for word_list in word_lists:
        saved_word_ids = [
            word_id
            for word_id in _decode_saved_word_ids(word_list.saved_word_ids)
            if word_id != saved_word.id
        ]
        word_list.saved_word_ids = _encode_saved_word_ids(saved_word_ids)

    db.delete(saved_word)
    db.commit()


def list_word_lists(db: Session, user: User) -> list[WordListResponse]:
    word_lists = list(
        db.execute(
            select(WordList)
            .where(WordList.user_id == user.id)
            .order_by(WordList.updated_at.desc(), WordList.title.asc())
        )
        .scalars()
        .all()
    )

    return [_word_list_response(word_list) for word_list in word_lists]


def create_word_list(
    db: Session,
    user: User,
    payload: WordListCreateRequest,
) -> WordListResponse:
    saved_word_ids = _validate_saved_word_ids(db, user, payload.saved_word_ids)
    word_list = WordList(
        user_id=user.id,
        title=payload.title,
        description=payload.description,
        saved_word_ids=_encode_saved_word_ids(saved_word_ids),
    )
    db.add(word_list)
    db.commit()
    db.refresh(word_list)

    return _word_list_response(word_list)


def update_word_list(
    db: Session,
    user: User,
    word_list_id: str,
    payload: WordListUpdateRequest,
) -> WordListResponse:
    word_list = _get_owned_word_list(db, user, word_list_id)
    updates = payload.model_dump(exclude_unset=True)
    if "saved_word_ids" in updates and updates["saved_word_ids"] is not None:
        updates["saved_word_ids"] = _encode_saved_word_ids(
            _validate_saved_word_ids(db, user, updates["saved_word_ids"])
        )
    for field, value in updates.items():
        setattr(word_list, field, value)
    db.commit()
    db.refresh(word_list)

    return _word_list_response(word_list)


def delete_word_list(db: Session, user: User, word_list_id: str) -> None:
    word_list = _get_owned_word_list(db, user, word_list_id)
    db.delete(word_list)
    db.commit()
