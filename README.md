# Ratiss GI

**Là où le tissu s'est arrêté, et là où la bouche commence.**

Jonathan Evina · RATISS Labs · Yaoundé · MIT

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jonathansearch/Ratiss-GI/blob/main/colab/Entrainement_Bouche_RATISS_GI.ipynb)
[![License: MIT](https://img.shields.io/badge/Code-MIT-teal.svg)](LICENSE)

Ratiss GI n'est pas un nouveau transformeur.
Ce n'est pas non plus un remplacement de [RATISS-ONE](https://github.com/jonathansearch/RATISS-ONE) ni de [RATISS-FIRST](https://github.com/jonathansearch/RATISS-FIRST).

C'est la pièce qui manquait pour que le tissu **parle** au lieu de **résonner**.

| Ce qui existait déjà | Ce que ce dépôt ajoute |
|---|---|
| Un graphe scellé, 95 660 neurones, 428 471 liens | Une bouche qui n'a le droit de marcher que vers l'avant |
| La question « qui fréquente qui ? » | La question « quel mot a le droit de suivre ? » |
| Un `.ratiss` gelé | Un fichier à part, `.bouche`, qui n'a pas le droit de réécrire le gel |

---

## Pourquoi le modèle ne parlait pas

Il n'était pas trop petit. Il répondait à **une autre question**.

Le fichier `cerveau/RatissOne.ratiss` (6,03 Mo, empreinte SHA-256 `b032c239bc2650636058c572e9545a24b4e8ca59c5ec68a601836d98b343ab2c`) contient un vrai tissu :

- 95 660 neurones, presque tous préfixés `word_`, seuil 50
- 428 471 liens `[source, cible, force]`
- 428 471 paires gelées : le tissu publié n'apprend plus
- 0 lien inversé. `cle_lien` **trie** les deux bouts. `destin—devoir` et `devoir—destin` sont le même lien
- 4 textes de sanctuaire écrits à la main (`trou noir`, `fusion`, `paris`, `yaounde`), pas des phrases sorties du graphe

Conséquence, mesurée par `python3 ratiss_v3.py cerveau/RatissOne.ratiss --audit` :

> Après « il », le top du tissu est `a, abord, aborda, aborde, accepta`.
> Après « était », c'est `abattu, absente, absolument`.
> Sur 16 suites françaises ordinaires, le vrai mot suivant est dans ce top-5 **2 fois sur 16, soit 12 %**.

Ce n'est pas une suite. C'est l'alphabet des forces à 100. « La mer » résonne avec `noire, outre, gallienne`. Une nuée. Le décodeur de FIRST collait ensuite les deux plus forts dans une phrase écrite d'avance : *« Le sujet concerne principalement X en liaison avec Y »*. Le sanctuaire, lui, récitait un des 4 textes tapés. « Apprends que… » rangeait la chaîne de caractères et la relisait. Rien de tout cela ne **marchait** sur les 428 471 liens.

La loi Ratum, elle, fait exactement ce qui a été écrit, et elle le fait bien. Renforcer quand les deux bouts battent, délier sinon, ombre d'un demi à chaque saut, entiers, déterministe. Elle sculpte une **intrication**. Une intrication ne sait pas dans quel sens marcher. Le gel a en plus figé cette intrication : la bouche, si on la cherchait dedans, naissait morte.

Le mini-GPT à côté (`scalable_gpt_train.py`, le `.pt` de 3,6 Mo) est une autre créature. Nourrir un transformeur qui n'est pas branché sur Ratum ne pouvait pas faire parler Ratum.

## Ce que la v3 change

Elle ne jette pas le tissu. Elle ajoute une **deuxième famille de liens**, que le tri n'a pas le droit de toucher.

- `intriqué(mer, noire)` reste dans le `.ratiss`. C'est le thème.
- `suit(mer → noire)` est un autre objet. « la mer noire » renforce `mer → noire`. « la noire nuit » renforce `noire → nuit`. Aujourd'hui les deux s'écrasaient dans le même lien.

La bouche ne marche **que** sur `suit`. Le tissu continue de résonner. Deux mémoires, comme la charge et la force. Ici, le thème et l'ordre.

L'ordre, mesuré, n'est plus le bigramme seul. Quand la paire des deux derniers mots a été vue, elle prend 65 % du score et le bigramme du dernier mot garde 35 %. Sinon on retombe sur le bigramme : un trigramme absent ne fait pas taire la bouche. On ne recalcule pas les 95 660 neurones. Les candidats sont les successeurs déjà écrits sous cette paire.

Sur un texte tenu à l'écart où « noire » a deux avenirs (« la mer noire s'étend », « la nuit noire tombait »), décharge allumée, le top-1 passe de 33 % (bigramme) à 39 % (trigramme avec repli). La lumière sur 8 mots descend à 30 %. Le top-5, lui, reste à 67 % : la paire choisit mieux le premier mot, elle n'allonge pas la liste. Une troisième tête, le thème, monte un peu le top-5 en allongeant la liste, et elle n'améliore pas le mot choisi : on ne l'habille pas en attention.

Le sanctuaire reste le secteur figé. Il n'est pas versé dans les synapses plastiques. « explique la fusion » marche le chemin scellé et rend la phrase d'origine, accents compris. Un fait gravé (« la lune orbite… ») se lit depuis son ancre : « lune orbite autour de la terre », sans boucler sur le deuxième « la ».

Le chiffre, toujours le même : sur des phrases que la bouche **n'a pas** vues, le vrai mot suivant est-il dans les 5 meilleurs candidats ? C'est le `top-5`. Tant qu'on ne l'a pas, on juge au ressenti.

Sur le jouet du dépôt (8 phrases, aucun GPU) :

| Mesure | top-5 |
|---|---|
| Thème, fenêtre de 3, les deux sens | 89 % |
| Arcs dirigés, dernier mot seul | 100 % |
| Lumière sur les 8 derniers mots | 95 % |
| 2 phrases tenues à l'écart | 67 % |

La marche gloutonne depuis « un » donne : *jardin le petit prince aimait sa rose vivait sous un globe*. Français sur quelques mots de plus qu'avec le bigramme seul (il s'arrêtait avant « globe »), puis la boucle. C'est la naissance, pas un sommet. Le jouet n'a vu que huit phrases.

À retenir, parce que c'est le contraire d'une promesse marketing : **allumer les 8 derniers mots ne gagne pas tout seul**. Sur ce jouet, la lumière fait 95 % et le dernier mot seul fait 100 %. La lumière est une hypothèse. On la garde si, sur un vrai texte tenu à l'écart, elle fait monter le top-5. Sinon on ne l'habille pas en transformeur.

Sans texte d'éducation, la bouche dit qu'elle est vide. Elle ne fabrique plus de phrase-gabarit. « explique la fusion » récite le sanctuaire. « Apprends que la lune orbite autour de la terre » grave la chaîne `la → lune → orbite → autour → de → la → terre`, et « parle moi de la lune » l'emprunte.

Le `.ratiss` n'est pas ouvert en écriture. La bouche se sauve à côté.

## En une minute

```bash
python3 ratiss_v3.py --demo

python3 ratiss_v3.py cerveau/RatissOne.ratiss --audit

python3 ratiss_v3.py cerveau/RatissOne.ratiss \
  --eduquer corpus/prince_jouet.txt --tours 3 --sauver bouche.json

python3 ratiss_v3.py cerveau/RatissOne.ratiss \
  --charger bouche.json --evaluer corpus/tenu_a_lecart.txt

python3 ratiss_v3.py cerveau/RatissOne.ratiss \
  --charger bouche.json --lam 0.75 --memoire 8 "il etait une fois"
```

`--lam 1` c'est l'ordre seul. `--lam 0` c'est le thème seul. `--memoire 8` allume les 8 derniers mots (lumière 1, ½, ¼…). `--sans-contraste` coupe la décharge, pour comparer.

Stdlib seulement. Pas de PyTorch. Pas de GPU. Python 3.10+.

## Carte du dépôt

```
ratiss_v3.py                 l'architecture. L'analogue du model.py, pas un transformeur
config/config.ratiss.json    le plan, avant toute donnée. Zéro savoir
config/bouche_etape0.json    la bouche vide. Zéro arc. L'analogue de l'étape 0
pipeline/01_oreille.py       le texte devient des mots
pipeline/02_init_vide.py     écrit l'étape 0
pipeline/03_entrainer.py     compte les arcs dirigés
pipeline/04_evaluer.py       le top-5, sur un texte non vu
pipeline/05_exporter.py      écrit le .bouche
entrainement/organiser_corpus.py
colab/Entrainement_Bouche_RATISS_GI.ipynb
cerveau/RatissOne.ratiss     le tissu scellé, copié tel quel depuis RATISS-ONE
corpus/                      jouets + la façon d'organiser un vrai corpus
docs/RATISS-VS-GPT.md
docs/ENTRAINEMENT.md
docs/BOUCHE.md
docs/QUATRE_PILIERS.md
docs/ORGANISATION_LANGUE.md
piliers/                      synapse O(1), audit, épisode vif, résonance
entrainement/entrainer_langue.py   les dix pas, prose puis faits, épisodes, retouches
```

Lire ensuite [pourquoi ce n'est pas un GPT](docs/RATISS-VS-GPT.md), [comment entraîner, sur quoi, et sur quelle machine](docs/ENTRAINEMENT.md), [l'organisation des dix pas](docs/ORGANISATION_LANGUE.md), [comment la parole est représentée sans transformeur](docs/BOUCHE.md), [les quatre opérations mesurées](docs/QUATRE_PILIERS.md).

Le tissu scellé ne contient pas l'arc `soleil—lune`. La résonance sur ce fichier met `de` devant `lune`. Le chiffre, et pourquoi on ne l'habille pas, est dans [le rapport](RAPPORT_EXPLORATION_4PILIERS.md).

## Ce qu'on arrête

- Plus de T4 tant que le top-5 d'un texte **non vu** n'a pas été lu.
- Plus de phrases ajoutées au sanctuaire pour « qu'il ait l'air de savoir ». Ça masque le trou.
- Plus de sceau, de synchrotron, de prosodie, tant que la phrase n'existe pas.
- Le gel global reste pour l'intrication déjà apprise. Il ne s'applique pas aux arcs `suit`.

## Auteur

Jonathan Evina, RATISS Labs, Yaoundé. Le concept, le tissu, les secteurs, la nuit, le marbre, c'est le sien. Ratiss GI est la bouche dirigée posée dessus, au point exact où le travail s'était arrêté.
