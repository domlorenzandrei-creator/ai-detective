from detective.search import SearchIndex


def make_index():
    idx = SearchIndex()
    idx.add("a", "the letter mentions blackmail")
    idx.add("b", "the letter the note the receipt")
    idx.add("c", "the the the")
    return idx


def test_rarer_match_ranks_first():
    ranked = make_index().rank("letter blackmail")
    assert [doc_id for doc_id, _ in ranked] == ["a", "b"]


def test_match_all_requires_every_word():
    ranked = make_index().rank("letter blackmail", match_all=True)
    assert [doc_id for doc_id, _ in ranked] == ["a"]


def test_unknown_word_returns_nothing():
    assert make_index().rank("zebra") == []


def test_readding_a_document_drops_old_words():
    idx = SearchIndex()
    idx.add("a", "old words")
    idx.add("a", "new words")
    assert idx.rank("old") == []
    assert [doc_id for doc_id, _ in idx.rank("new")] == ["a"]