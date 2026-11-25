# Dictionary vCards

Contact packs that stop iPhone autocorrect from "fixing" words it doesn't know.

- `pokemon.vcf`: 24 contacts named "Dictionary - Pokemon 01" to "24". The words sit, comma-separated, in each contact's Company and Job Title fields, which iOS treats as real words. Each field stays under 236 characters, because iOS ignores words past about 250.

## Rebuilding

Edit the word lists in `source/`, then run:

    python3 vcards/source/build_vcf.py
