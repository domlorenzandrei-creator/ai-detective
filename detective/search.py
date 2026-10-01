import math
import re
from collections import Counter, defaultdict


def tokenize(text: str) -> list:
    return re.findall(r"[a-z0-9]+", text.lower())


class SearchIndex:
    def __init__(self):
        self.docs = {}
        self.index = defaultdict(set)
        self.term_counts = {}

    def add(self, doc_id: str, text: str) -> None:
        if doc_id in self.docs:
            for token in self.term_counts[doc_id]:
                self.index[token].discard(doc_id)
        self.docs[doc_id] = text
        tokens = tokenize(text)
        self.term_counts[doc_id] = Counter(tokens)
        for token in tokens:
            self.index[token].add(doc_id)

    def idf(self, token: str) -> float:
        df = len(self.index.get(token, ()))
        return math.log((1 + len(self.docs)) / (1 + df)) + 1

    def rank(self, query: str, match_all: bool = False) -> list:
        terms = set(tokenize(query))
        if not terms:
            return []
        matches = [self.index.get(t, set()) for t in terms]
        hits = set.intersection(*matches) if match_all else set.union(*matches)
        scored = []
        for doc_id in hits:
            counts = self.term_counts[doc_id]
            length = sum(counts.values())
            score = sum((counts[t] / length) * self.idf(t) for t in terms)
            scored.append((doc_id, score))
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        return scored

    def search(self, query: str, match_all: bool = False) -> list:
        return [(doc_id, self.docs[doc_id]) for doc_id, _ in self.rank(query, match_all)]