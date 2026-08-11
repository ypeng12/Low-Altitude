"""Offset-preserving sentence and discourse-aware clause segmentation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

from .ids import stable_span_id


_TOKEN_RE = re.compile(r"\b[\w']+\b", re.UNICODE)
_ABBREVIATIONS = {
    "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "st.",
    "vs.", "etc.", "e.g.", "i.e.", "u.s.", "u.k.", "a.m.", "p.m.",
}
_MARKERS = (
    "even though",
    "nevertheless",
    "nonetheless",
    "although",
    "however",
    "despite",
    "whereas",
    "though",
    "while",
    "but",
    "yet",
    "then",
    "still",
)
_MARKER_RE = re.compile(
    r"\b(" + "|".join(re.escape(marker) for marker in _MARKERS) + r")\b",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class TextSpan:
    start: int
    end: int
    text: str
    marker_before: str = ""
    split_reason: str = ""


def token_count(text: str) -> int:
    return len(_TOKEN_RE.findall(text))


def _trimmed_span(text: str, start: int, end: int, **kwargs: str) -> Optional[TextSpan]:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    if start >= end:
        return None
    return TextSpan(start=start, end=end, text=text[start:end], **kwargs)


def _is_sentence_period(text: str, index: int) -> bool:
    if text[index] != ".":
        return True
    if 0 < index < len(text) - 1 and text[index - 1].isdigit() and text[index + 1].isdigit():
        return False
    left = text[: index + 1]
    match = re.search(r"([A-Za-z](?:[A-Za-z.]*)\.)$", left)
    token = match.group(1).casefold() if match else ""
    if token in _ABBREVIATIONS:
        return False
    if re.fullmatch(r"(?:[A-Za-z]\.){2,}", token):
        return False
    return True


def sentence_spans(text: str) -> List[TextSpan]:
    """Split text into sentences while retaining exact source offsets."""

    spans: List[TextSpan] = []
    start = 0
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        boundary_end: Optional[int] = None
        if char == "\n":
            boundary_end = index
            while index + 1 < length and text[index + 1] == "\n":
                index += 1
        elif char in ".!?" and _is_sentence_period(text, index):
            punctuation_end = index + 1
            while punctuation_end < length and text[punctuation_end] in ".!?\"')]}":
                punctuation_end += 1
            if punctuation_end == length or text[punctuation_end].isspace():
                boundary_end = punctuation_end
                index = punctuation_end - 1
        if boundary_end is not None:
            span = _trimmed_span(text, start, boundary_end)
            if span is not None:
                spans.append(span)
            start = index + 1
        index += 1
    tail = _trimmed_span(text, start, length)
    if tail is not None:
        spans.append(tail)
    return spans


def split_long_span(span: TextSpan, source_text: str, max_words: int) -> List[TextSpan]:
    """Split pathological run-on sentences without dropping source material."""

    matches = list(_TOKEN_RE.finditer(span.text))
    if max_words <= 0 or len(matches) <= max_words:
        return [span]

    pieces: List[TextSpan] = []
    local_start = 0
    while token_count(span.text[local_start:]) > max_words:
        local_matches = list(_TOKEN_RE.finditer(span.text, local_start))
        target = local_matches[max_words - 1].end()
        search_start = local_matches[max(max_words // 2, 1) - 1].end()
        break_positions = [
            match.end()
            for match in re.finditer(r"[;:,\u2014\u2013-]+\s+", span.text[search_start:target])
        ]
        if break_positions:
            local_end = search_start + break_positions[-1]
        else:
            local_end = target
        piece = _trimmed_span(
            source_text,
            span.start + local_start,
            span.start + local_end,
            split_reason="long_sentence",
        )
        if piece is not None:
            pieces.append(piece)
        local_start = local_end
        while local_start < len(span.text) and span.text[local_start].isspace():
            local_start += 1
    final = _trimmed_span(
        source_text,
        span.start + local_start,
        span.end,
        split_reason="long_sentence",
    )
    if final is not None:
        pieces.append(final)
    return pieces


def clause_spans(sentence: TextSpan, source_text: str, min_tokens: int) -> List[TextSpan]:
    """Split only when discourse markers or strong punctuation yield viable clauses."""

    local_text = sentence.text
    leading = _MARKER_RE.match(local_text)
    leading_marker = ""
    leading_cursor = 0
    if leading and leading.group(0).casefold() in {
        "although", "though", "even though", "despite", "while", "whereas"
    }:
        comma = local_text.find(",", leading.end())
        if comma >= 0:
            before_comma = local_text[leading.end() : comma]
            after_comma = local_text[comma + 1 :]
            if token_count(before_comma) >= min_tokens and token_count(after_comma) >= min_tokens:
                leading_marker = leading.group(0).casefold()
                leading_cursor = leading.end()
    candidates: List[Tuple[int, int, str]] = [
        (match.start(), match.end(), match.group(0).casefold())
        for match in _MARKER_RE.finditer(local_text)
        if match.start() >= leading_cursor and match is not leading
    ]
    if leading_cursor:
        comma = local_text.find(",", leading_cursor)
        candidates.append((comma, comma + 1, leading_marker))
    candidates.extend((match.start(), match.end(), match.group(0)) for match in re.finditer(r"[;\u2014]", local_text))
    candidates.sort(key=lambda item: item[0])
    if not candidates:
        return [sentence]

    clauses: List[TextSpan] = []
    cursor = leading_cursor
    marker_before = leading_marker
    for marker_start, marker_end, marker in candidates:
        if marker_start < cursor:
            continue
        before = local_text[cursor:marker_start]
        after = local_text[marker_end:]
        if token_count(before) < min_tokens or token_count(after) < min_tokens:
            continue
        piece = _trimmed_span(
            source_text,
            sentence.start + cursor,
            sentence.start + marker_start,
            marker_before=marker_before,
            split_reason="discourse_clause",
        )
        if piece is not None:
            clauses.append(piece)
        cursor = marker_end
        marker_before = marker

    final = _trimmed_span(
        source_text,
        sentence.start + cursor,
        sentence.end,
        marker_before=marker_before,
        split_reason="discourse_clause" if clauses else sentence.split_reason,
    )
    if final is not None:
        clauses.append(final)

    viable = [clause for clause in clauses if token_count(clause.text) >= min_tokens]
    if len(viable) < 2:
        return [sentence]
    return viable


def segment_review(
    review_id: str,
    text: str,
    min_sentence_tokens: int = 1,
    min_clause_tokens: int = 3,
    max_span_words: int = 120,
    split_long_sentences: bool = True,
    use_clauses_for_analysis: bool = True,
) -> Tuple[List[dict], List[dict], List[dict]]:
    """Return sentence rows, analysis-span rows, and explicit exclusions."""

    sentences: List[dict] = []
    analysis: List[dict] = []
    exclusions: List[dict] = []
    for sentence_index, raw_sentence in enumerate(sentence_spans(text)):
        sentence_id = stable_span_id(review_id, raw_sentence.start, raw_sentence.end, "sentence")
        sentence_tokens = token_count(raw_sentence.text)
        sentence_row = {
            "review_id": review_id,
            "sentence_id": sentence_id,
            "sentence_index": sentence_index,
            "sentence_start": raw_sentence.start,
            "sentence_end": raw_sentence.end,
            "sentence_text": raw_sentence.text,
            "token_count": sentence_tokens,
        }
        sentences.append(sentence_row)
        if sentence_tokens < min_sentence_tokens:
            exclusions.append({**sentence_row, "exclusion_reason": "below_min_sentence_tokens"})
            continue

        long_pieces = (
            split_long_span(raw_sentence, text, max_span_words)
            if split_long_sentences
            else [raw_sentence]
        )
        for piece_index, piece in enumerate(long_pieces):
            clauses = (
                clause_spans(piece, text, min_clause_tokens)
                if use_clauses_for_analysis
                else [piece]
            )
            unit_type = "clause" if len(clauses) > 1 else (
                "sentence_chunk" if len(long_pieces) > 1 else "sentence"
            )
            for clause_index, clause in enumerate(clauses):
                span_id = stable_span_id(
                    review_id,
                    clause.start,
                    clause.end,
                    unit_type,
                    occurrence=piece_index * 1000 + clause_index,
                )
                analysis.append(
                    {
                        "review_id": review_id,
                        "span_id": span_id,
                        "parent_sentence_id": sentence_id,
                        "sentence_index": sentence_index,
                        "span_index_within_sentence": piece_index * 1000 + clause_index,
                        "unit_type": unit_type,
                        "span_start": clause.start,
                        "span_end": clause.end,
                        "span_text": clause.text,
                        "token_count": token_count(clause.text),
                        "marker_before": clause.marker_before,
                        "split_reason": clause.split_reason,
                    }
                )
    if not sentences and text.strip():
        exclusions.append(
            {
                "review_id": review_id,
                "sentence_id": "",
                "sentence_index": -1,
                "sentence_start": 0,
                "sentence_end": len(text),
                "sentence_text": text,
                "token_count": token_count(text),
                "exclusion_reason": "segmentation_failure",
            }
        )
    return sentences, analysis, exclusions
