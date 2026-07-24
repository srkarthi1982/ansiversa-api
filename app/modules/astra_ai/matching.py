from __future__ import annotations

import re

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def normalize_text(value: str) -> str:
    return " ".join(value.lower().strip().split())


def tokenize(value: str) -> tuple[str, ...]:
    return tuple(TOKEN_PATTERN.findall(normalize_text(value)))


def matched_terms(message: str, terms: tuple[str, ...]) -> tuple[str, ...]:
    tokens = tokenize(message)
    token_set = set(tokens)
    matches: list[str] = []
    for term in terms:
        term_tokens = tokenize(term)
        if not term_tokens:
            continue
        if len(term_tokens) == 1 and term_tokens[0] in token_set:
            matches.append(term)
        elif len(term_tokens) > 1 and _contains_token_phrase(tokens, term_tokens):
            matches.append(term)
    return tuple(matches)


def has_any_term(message: str, terms: tuple[str, ...]) -> bool:
    return bool(matched_terms(message, terms))


def _contains_token_phrase(tokens: tuple[str, ...], phrase_tokens: tuple[str, ...]) -> bool:
    phrase_size = len(phrase_tokens)
    if phrase_size > len(tokens):
        return False
    return any(
        tokens[index : index + phrase_size] == phrase_tokens
        for index in range(len(tokens) - phrase_size + 1)
    )
