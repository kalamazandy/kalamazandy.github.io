# Dictionary vCards

Contact packs that stop iPhone autocorrect from "fixing" words it doesn't know.

- `pokemon.vcf`: 14 contacts named "Dictionary - Pokemon 01" to "14". The words sit in each contact's Company field, which iOS treats as real words.

## Rebuilding

Edit the word lists in `source/`, then run:

    python3 vcards/source/build_vcf.py
