import re
from collections import defaultdict


def tokenize(text: str) -> list:
    return re.findall(r"[a-z0-9]+", text.lower())


class SearchIndex:
    def __init__(self):
        self.docs = {}
        self.index = defaultdict(set)

    def add(self, doc_id: str, text: str) -> None:
        self.docs[doc_id] = text
        for token in tokenize(text):
            self.index[token].add(doc_id)

    def search(self, query: str) -> list:
        tokens = tokenize(query)
        if not tokens:
            return []
        matches = [self.index.get(t, set()) for t in tokens]
        hits = set.intersection(*matches)
        return [(doc_id, self.docs[doc_id]) for doc_id in sorted(hits)]