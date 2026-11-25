#!/usr/bin/env python3
"""Build vcards/pokemon.vcf from the word lists in this folder.

Run from anywhere:  python3 vcards/source/build_vcf.py

Each contact is named "Dictionary - Pokemon NN" and holds its words,
separated by commas, in the Company and Job Title fields. Field tests on
iOS showed:
- comma-separated words are all learned, but only up to about 250
  characters per field (iOS/iCloud's limit), so each field stays under
  FIELD_LIMIT characters as stored on the phone;
- Company part 2 (department), Nickname past ~218 characters, and the
  phonetic name fields didn't teach the keyboard reliably, so they're unused.
The contact list only shows the short name.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "pokemon.vcf"
FIELD_LIMIT = 236  # stored characters per field, including ", "
FIELDS_PER_CONTACT = 2  # Company, Job Title
SITE = "https://kalamazandy.github.io"


def read_words(name):
    words = []
    for line in (HERE / name).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            words.append(line)
    return words


def escape(text):
    return (text.replace("\\", "\\\\").replace(";", "\\;")
                .replace(",", "\\,").replace("\n", "\\n"))


def fold(line):
    """Fold a content line at 75 bytes without splitting a UTF-8 character."""
    out, current, size = [], "", 0
    for ch in line:
        n = len(ch.encode("utf-8"))
        if size + n > 75:
            out.append(current)
            current, size = " ", 1
        current += ch
        size += n
    out.append(current)
    return "\r\n".join(out)


def card(title, fields, note):
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        "PRODID:-//kalamazandy.github.io//Dictionary vCards//EN",
        f"N:{escape(title)};;;;",
        f"FN:{escape(title)}",
        f"ORG:{escape(', '.join(fields[0]))}",
        *([f"TITLE:{escape(', '.join(fields[1]))}"] if len(fields) > 1 else []),
        f"NOTE:{escape(note)}",
        f"URL:{SITE}",
        "END:VCARD",
    ]
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


def pack_fields(words):
    """Fill fields in order, each at most FIELD_LIMIT characters."""
    fields, current = [], []
    for w in words:
        if current and len(", ".join(current + [w])) > FIELD_LIMIT:
            fields.append(current)
            current = []
        current.append(w)
    if current:
        fields.append(current)
    return fields


def main():
    seen, names, terms = set(), [], []
    for src, dest in ((read_words("pokemon-names.txt"), names),
                      (read_words("pokemon-terms.txt"), terms)):
        for w in src:
            if w not in seen:
                seen.add(w)
                dest.append(w)

    fields = pack_fields(names + terms)
    chunks = [fields[i:i + FIELDS_PER_CONTACT]
              for i in range(0, len(fields), FIELDS_PER_CONTACT)]

    note = ("Autocorrect helper: iOS accepts the words in the Company and Job "
            f"Title fields as real words. Free from {SITE}. Safe to delete.")
    cards = [card(f"Dictionary - Pokemon {n:02d}", chunk, note)
             for n, chunk in enumerate(chunks, 1)]
    OUT.write_bytes("".join(cards).encode("utf-8"))
    print(f"Wrote {OUT} with {len(cards)} contacts, "
          f"{len(names)} name words and {len(terms)} terms.")


if __name__ == "__main__":
    main()
