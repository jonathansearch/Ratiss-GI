# Corpus

Les fichiers ici sont des **jouets**. Ils servent à vérifier que le pipeline tourne. Ils ne font pas une bouche.

| Fichier | Rôle |
|---|---|
| `prince_jouet.txt` | 8 phrases, registre `conte`. C'est le `--demo` |
| `tenu_a_lecart.txt` | phrases cousines, **non** données à l'éducation du jouet. C'est le juge |
| `faits_jouet.txt` | vérités courtes, pour `--faits` |
| `dialogue_jouet.jsonl` | trois tours, pour tester l'organiseur |

Le vrai texte reste chez toi. Voir `docs/ENTRAINEMENT.md` pour Gutenberg, Wikipédia, OpenAssistant, et ce qu'il ne faut pas mélanger.

```bash
python3 entrainement/organiser_corpus.py \
  --entree corpus/dialogue_jouet.jsonl \
  --sortie corpus/dialogue_jouet.txt \
  --registre dialogue
```
