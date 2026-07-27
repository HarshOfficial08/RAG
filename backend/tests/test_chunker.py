from app.ingestion.chunker import chunk_text


def test_empty_text_returns_no_chunks() -> None:
    assert chunk_text("") == []


def test_short_text_returns_single_chunk() -> None:
    assert chunk_text("hello world", chunk_size=500, overlap=50) == ["hello world"]


def test_long_text_splits_with_overlap() -> None:
    words = [f"word{i}" for i in range(120)]
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=50, overlap=10)

    assert len(chunks) == 3
    # the overlap window means the tail of one chunk reappears at the head of the next
    assert chunks[0].split()[-10:] == chunks[1].split()[:10]
    assert chunks[1].split()[-10:] == chunks[2].split()[:10]


def test_chunks_cover_every_word_at_least_once() -> None:
    words = [f"word{i}" for i in range(30)]
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=10, overlap=2)
    covered = set(" ".join(chunks).split())

    assert covered == set(words)
