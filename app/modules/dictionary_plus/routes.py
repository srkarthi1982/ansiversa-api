from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.dictionary_plus.db import get_dictionary_plus_db
from app.modules.dictionary_plus.schemas import (
    DictionaryLookupCreateRequest,
    DictionaryLookupListResponse,
    DictionaryLookupResponse,
    SavedWordCreateRequest,
    SavedWordListResponse,
    SavedWordResponse,
    WordListCreateRequest,
    WordListResponse,
    WordListsResponse,
    WordListUpdateRequest,
)
from app.modules.dictionary_plus.service import (
    create_lookup,
    create_saved_word,
    create_word_list,
    delete_saved_word,
    delete_word_list,
    list_lookups,
    list_saved_words,
    list_word_lists,
    update_word_list,
)

router = APIRouter()


@router.get("/lookups", response_model=DictionaryLookupListResponse)
def get_dictionary_lookups(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_dictionary_plus_db)],
) -> DictionaryLookupListResponse:
    return DictionaryLookupListResponse(items=list_lookups(db, current_user))


@router.post(
    "/lookups",
    response_model=DictionaryLookupResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dictionary_lookup(
    payload: DictionaryLookupCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_dictionary_plus_db)],
) -> DictionaryLookupResponse:
    return create_lookup(db, current_user, payload)


@router.get("/saved-words", response_model=SavedWordListResponse)
def get_saved_words(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_dictionary_plus_db)],
) -> SavedWordListResponse:
    return SavedWordListResponse(items=list_saved_words(db, current_user))


@router.post(
    "/saved-words",
    response_model=SavedWordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dictionary_saved_word(
    payload: SavedWordCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_dictionary_plus_db)],
) -> SavedWordResponse:
    return create_saved_word(db, current_user, payload)


@router.delete("/saved-words/{saved_word_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dictionary_saved_word(
    saved_word_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_dictionary_plus_db)],
) -> None:
    delete_saved_word(db, current_user, saved_word_id)


@router.get("/word-lists", response_model=WordListsResponse)
def get_word_lists(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_dictionary_plus_db)],
) -> WordListsResponse:
    return WordListsResponse(items=list_word_lists(db, current_user))


@router.post(
    "/word-lists",
    response_model=WordListResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dictionary_word_list(
    payload: WordListCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_dictionary_plus_db)],
) -> WordListResponse:
    return create_word_list(db, current_user, payload)


@router.put("/word-lists/{word_list_id}", response_model=WordListResponse)
def update_dictionary_word_list(
    word_list_id: Annotated[str, Path(min_length=1)],
    payload: WordListUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_dictionary_plus_db)],
) -> WordListResponse:
    return update_word_list(db, current_user, word_list_id, payload)


@router.delete("/word-lists/{word_list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dictionary_word_list(
    word_list_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_dictionary_plus_db)],
) -> None:
    delete_word_list(db, current_user, word_list_id)
