#!/usr/bin/env python3
"""Build vcards/pokemon.vcf from the word lists in this folder.

Run from anywhere:  python3 vcards/source/build_vcf.py

Each contact is named "Dictionary - Pokemon NN" and holds its words,
separated by spaces, in the Company field. iOS treats words in a contact's
First, Last and Company fields as real words, so autocorrect leaves them alone,
while the contact list only shows the short name.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "pokemon.vcf"
WORDS_PER_CONTACT = 90
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


def card(title, words, note):
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        "PRODID:-//kalamazandy.github.io//Dictionary vCards//EN",
        f"N:{escape(title)};;;;",
        f"FN:{escape(title)}",
        f"ORG:{escape(' '.join(words))}",
        f"NOTE:{escape(note)}",
        f"URL:{SITE}",
        "END:VCARD",
    ]
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


def split_evenly(words):
    """Split into chunks of at most WORDS_PER_CONTACT, sized evenly."""
    count = -(-len(words) // WORDS_PER_CONTACT)
    size = -(-len(words) // count)
    return [words[i:i + size] for i in range(0, len(words), size)]


def main():
    seen, names, terms = set(), [], []
    for src, dest in ((read_words("pokemon-names.txt"), names),
                      (read_words("pokemon-terms.txt"), terms)):
        for w in src:
            if w not in seen:
                seen.add(w)
                dest.append(w)

    chunks = split_evenly(names) + split_evenly(terms)

    note = ("Autocorrect helper: iOS accepts the words in the Company field as "
            f"real words. Free from {SITE}. Safe to delete.")
    cards = [card(f"Dictionary - Pokemon {n:02d}", chunk, note)
             for n, chunk in enumerate(chunks, 1)]
    OUT.write_bytes("".join(cards).encode("utf-8"))
    print(f"Wrote {OUT} with {len(cards)} contacts, "
          f"{len(names)} name words and {len(terms)} terms.")


if __name__ == "__main__":
    main()
