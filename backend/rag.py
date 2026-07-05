from __future__ import annotations

import math
import re
from functools import lru_cache
from pathlib import Path


KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"


def _tokenize(text: str):
    text = text.lower()
    words = re.findall(r"[a-zA-Z0-9]+|[\u4e00-\u9fff]", text)
    chinese_chars = [item for item in words if re.fullmatch(r"[\u4e00-\u9fff]", item)]
    bigrams = ["".join(chinese_chars[index : index + 2]) for index in range(len(chinese_chars) - 1)]
    return words + bigrams


def _read_chunks():
    chunks = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8-sig")
        source = path.stem
        current_title = path.stem
        buffer = []
        for line in text.splitlines():
            if line.startswith("#"):
                if buffer:
                    chunks.append({"source": source, "title": current_title, "content": "\n".join(buffer).strip()})
                    buffer = []
                current_title = line.lstrip("#").strip() or path.stem
            else:
                buffer.append(line)
        if buffer:
            chunks.append({"source": source, "title": current_title, "content": "\n".join(buffer).strip()})
    return [chunk for chunk in chunks if chunk["content"]]


@lru_cache(maxsize=1)
def _index():
    chunks = _read_chunks()
    tokenized = [_tokenize(chunk["title"] + "\n" + chunk["content"]) for chunk in chunks]
    doc_count = len(chunks) or 1
    df = {}
    for tokens in tokenized:
        for token in set(tokens):
            df[token] = df.get(token, 0) + 1
    return chunks, tokenized, df, doc_count


def search_fitness_knowledge(query: str, top_k: int = 3):
    query = (query or "").strip()
    if not query:
        return {"success": True, "query": query, "items": [], "count": 0}

    chunks, tokenized, df, doc_count = _index()
    query_tokens = _tokenize(query)
    scores = []
    for index, tokens in enumerate(tokenized):
        if not tokens:
            continue
        score = 0.0
        length_norm = 1 + math.log(len(tokens) + 1)
        for token in query_tokens:
            tf = tokens.count(token)
            if tf == 0:
                continue
            idf = math.log((doc_count + 1) / (df.get(token, 0) + 1)) + 1
            score += (tf * idf) / length_norm
        if score > 0:
            chunk = chunks[index]
            snippet = re.sub(r"\s+", " ", chunk["content"]).strip()
            scores.append(
                {
                    "source": chunk["source"],
                    "title": chunk["title"],
                    "snippet": snippet[:420],
                    "score": round(score, 4),
                }
            )

    items = sorted(scores, key=lambda item: item["score"], reverse=True)[: max(1, min(top_k, 8))]
    return {"success": True, "query": query, "items": items, "count": len(items)}


def build_plan_knowledge_query(goal=None, experience_level=None, injury_notes=None):
    parts = ["训练计划 科学 原则 渐进超负荷 恢复 安全"]
    if goal:
        parts.append(str(goal))
    if experience_level:
        parts.append(str(experience_level))
    if injury_notes:
        parts.append("疼痛 伤病 风险 " + str(injury_notes))
    return " ".join(parts)
