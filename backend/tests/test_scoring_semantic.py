import pytest

from app.domain.scoring.semantic import compute_semantic_score, normalize_vector


def test_normalize_vector_produces_unit_length() -> None:
    normalized = normalize_vector([3.0, 4.0])
    assert normalized == pytest.approx([0.6, 0.8])


def test_normalize_vector_returns_none_for_empty_or_zero_vector() -> None:
    assert normalize_vector([]) is None
    assert normalize_vector([0.0, 0.0]) is None


def test_identical_vectors_score_one() -> None:
    vector = [1.0, 2.0, 3.0]
    assert compute_semantic_score(vector, vector) == pytest.approx(1.0)


def test_similar_vectors_score_highly_but_not_perfectly() -> None:
    score = compute_semantic_score([1.0, 1.0, 0.0], [1.0, 0.9, 0.1])
    assert 0.9 < score < 1.0


def test_orthogonal_vectors_score_around_half() -> None:
    assert compute_semantic_score([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.5)


def test_opposite_vectors_score_zero() -> None:
    assert compute_semantic_score([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(0.0)


def test_missing_embeddings_return_zero() -> None:
    assert compute_semantic_score(None, [1.0, 0.0]) == 0.0
    assert compute_semantic_score([1.0, 0.0], None) == 0.0
    assert compute_semantic_score(None, None) == 0.0


def test_mismatched_dimensions_return_zero() -> None:
    assert compute_semantic_score([1.0, 0.0], [1.0, 0.0, 0.0]) == 0.0


def test_zero_vector_returns_zero() -> None:
    assert compute_semantic_score([0.0, 0.0], [1.0, 0.0]) == 0.0
