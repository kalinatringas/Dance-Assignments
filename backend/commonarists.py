import pandas as pd
import re
import json
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
import numpy as np

CSV_PATH = "CommonArtists.csv"   # Change if needed

df = pd.read_csv(CSV_PATH, header=None, names=["name"])
names = df["name"].dropna().tolist()

def normalize(name):
    name = name.lower()
    name = re.sub(r"[^a-z0-9]", "", name)
    return name

normalized = [normalize(n) for n in names]

print("Loading model and generating embeddings...")
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(names)

print("Clustering names...")
clustering = AgglomerativeClustering(
    n_clusters=None,
    distance_threshold=0.35,
    affinity='cosine',
    linkage='average'
).fit(embeddings)

clusters = {}
for label, name in zip(clustering.labels_, names):
    clusters.setdefault(label, []).append(name)


def choose_canonical(group):
    """
    Rule:
    1. Prefer the longest 'real' group name (since (G)I-DLE > gidle)
    2. Break ties by alphabetical order
    """
    return sorted(group, key=lambda x: (-len(x), x))[0]

canonical_dict = {}

for group in clusters.values():
    canonical = choose_canonical(group)
    for variant in group:
        canonical_dict[variant] = canonical

OUTPUT_PATH = "canonical_artists.json"
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(canonical_dict, f, ensure_ascii=False, indent=4)

print("Done! Canonical dictionary saved to", OUTPUT_PATH)

