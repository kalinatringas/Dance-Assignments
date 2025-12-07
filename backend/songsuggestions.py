import pandas as pd
import re
from collections import defaultdict
from rapidfuzz import process, fuzz


KNOWN_ARTISTS = set()
KNOWN_SONGS = set()

artists = pd.read_csv("CommonArtists.csv")

artists.columns = artists.columns.str.strip() # clean up white space


for artist in artists[0].dropna():
    KNOWN_ARTISTS.add(str(artist).strip().lower())

df = pd.read_csv("SongSuggestions.csv")

SONG_COLUMN = df.columns[2]# this is the column with all the suggestions

'''
map of the artist name - song name and then counter

if song name - artist name, need to switch the two around

each seperated by spaces, if not then by commas i believe. 

suggestions = {
    "artist name - song name" : num
    }

'''
suggestions = defaultdict()
for __, row in df.iterrows():
    song_suggestions = df.iloc[2] # right?? right???
    # then we need to process song suggestions because we have a chunk of text
    song_suggestions.split("") # split by spaces meow



def normalize(text):
    if not isinstance(text, str): # are u a string?
        return ""
    text = text.lower() # lowercase everything

    # get rid of weird deliminators 
    text = re.sub(r"[--:]","-",text)
    # get rid of number the lsit
    text = re.sub(r"^\s*\d+\.\s*", "", text)
    # get rid of white space    

    text = re.sub(r"\s+", " ", text).strip()

    return text

def fuzzy_match(term, choices):
    if not KNOWN_ARTISTS:
        return term, 0
    match, score, _ = process.extractOne(term, choices, scorer=fuzz.WRatio)
    return match, score

def parse_entry(entry):
    entry = normalize(entry)
    if "-" in entry:
        part1, part2 = [x.strip for x in entry.split(" - ", 1)]
    else: 
        parts = entry.split(" ", 1)
        if len(parts) == 2:
            part1, part2 = parts
        else:
            return None
    
    best_artist, score_art1 = fuzzy_match(part1, KNOWN_ARTISTS)
    best_song, score_art2 = fuzzy_match(part2, KNOWN_ARTISTS)

    if score_art1>= score_art2: #this decides which one is the artist
        artist = best_artist
        song = part2
    else:
        artist = best_song
        song = part1

    return {"artist": artist, "song": song}

def process_song_list(text):
    if not isinstance(text, str):
        return []
    
    raw_entries = re.split(r"[\n,;+]", text)
    results = []

    for r in raw_entries:
        cleaned = r.strip()
        if cleaned: 
            parsed = parse_entry(cleaned)
            if parsed:
                results.append(parsed)

clean_rows = []

for idx, row in df.iterrows():
    song_column = df.columns[2]
    songs = process_song_list(row[song_column])
    for s in songs:
        clean_rows.append({
             "timestamp": row["Timestamp"],
            "user": row["Your name?"],
            "artist": s["artist"],
            "song": s["song"],
        })
clean_df = pd.DataFrame(clean_rows)
clean_df.to_csv("cleaned_song_submissions.csv", index=False)