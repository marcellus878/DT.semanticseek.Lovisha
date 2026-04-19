import numpy as np
import json
from sentence_transformers import SentenceTransformer

# 🔥 Load model ONCE
model = SentenceTransformer("all-mpnet-base-v2")


# 🔹 Get embedding (normalized)
def get_embedding(text):
    emb = model.encode(text)
    emb = emb / np.linalg.norm(emb)
    return emb.tolist()


# 🔹 Safe cosine similarity
def cosine_similarity(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    if len(v1) != len(v2):
        return 0

    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denom == 0:
        return 0

    return float(np.dot(v1, v2) / denom)


# 🔹 Better keyword overlap (F1 score)
def keyword_overlap(text1, text2):
    w1 = set(text1.lower().split())
    w2 = set(text2.lower().split())

    if not w1 or not w2:
        return 0

    common = len(w1.intersection(w2))
    precision = common / len(w1)
    recall = common / len(w2)

    if precision + recall == 0:
        return 0

    return 2 * (precision * recall) / (precision + recall)


# 🔹 Explanation
def generate_explanation(text1, text2):
    common = set(text1.lower().split()).intersection(text2.lower().split())

    if not common:
        return "Matched using AI semantic similarity."

    return "Matched based on: " + ", ".join(list(common)[:3])


# 🔥 IMAGE SIMILARITY (normalized)
def image_similarity_from_db(new_item, item):
    try:
        if len(new_item) > 9 and len(item) > 9:
            if new_item[9] and item[9]:

                emb1 = np.array(json.loads(new_item[9]))
                emb2 = np.array(json.loads(item[9]))

                emb1 = emb1 / np.linalg.norm(emb1)
                emb2 = emb2 / np.linalg.norm(emb2)

                return float(np.dot(emb1, emb2))
    except:
        pass

    return 0.0


# 🔥 TITLE SIMILARITY (lightweight boost)
def title_similarity(title1, title2):
    return keyword_overlap(title1, title2)


# 🔥 COMBINED SCORE (HIGH ACCURACY)
def combined_score(new_item, item):

    # 🔹 TEXT
    new_vec = json.loads(new_item[7])
    item_vec = json.loads(item[7])
    text_score = cosine_similarity(new_vec, item_vec)

    # 🔹 TEXT CONTENT
    text1 = new_item[2] + " " + new_item[3]
    text2 = item[2] + " " + item[3]

    keyword_score = keyword_overlap(text1, text2)

    # 🔹 TITLE BOOST
    title_score = title_similarity(new_item[2], item[2])

    # 🔹 IMAGE
    img_score = image_similarity_from_db(new_item, item)

    # 🔹 CATEGORY
    cat_bonus = 0.0
    cat_penalty = 0.0

    try:
        if new_item[8] == item[8]:
            cat_bonus = 0.12
        else:
            cat_penalty = 0.08
    except:
        pass

    # 🔥 EXACT MATCH BOOST (CRITICAL)
    exact_bonus = 0.0

    if new_item[2].strip().lower() == item[2].strip().lower():
        exact_bonus += 0.1

    if new_item[3].strip().lower() == item[3].strip().lower():
        exact_bonus += 0.1

    # 🔥 FINAL SCORE (TUNED FOR ACCURACY)
    final = (
        0.5 * text_score
        + 0.2 * img_score
        + 0.15 * keyword_score
        + 0.1 * title_score
        + cat_bonus
        - cat_penalty
        + exact_bonus
    )

    return max(0, min(final, 1))


# 🔥 MAIN MATCH FUNCTION
def find_matches_ai(new_item, all_items):
    results = []

    if not new_item[7]:
        return []

    for item in all_items:

        # ✅ Lost ↔ Found only
        if new_item[4] == "Lost" and item[4] != "Found":
            continue

        if new_item[4] == "Found" and item[4] != "Lost":
            continue

        # ❌ Ignore completed
        if item[4] in ["Claimed", "Returned"]:
            continue

        if not item[7]:
            continue

        score = combined_score(new_item, item)

        # 🔥 dynamic threshold
        if score > 0.5:

            text1 = new_item[2] + " " + new_item[3]
            text2 = item[2] + " " + item[3]

            explanation = generate_explanation(text1, text2)

            results.append((item, round(score * 100, 2), explanation))

    return sorted(results, key=lambda x: x[1], reverse=True)[:5]
