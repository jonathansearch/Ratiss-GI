# -*- coding: utf-8 -*-
"""Résonance : une onde par concept, la même ombre d'un demi à chaque saut.

Ce n'est pas une attention. On ne lit pas une phrase pour justifier le carrefour.
L'énergie reçue en un nœud est la somme des ondes qui l'atteignent.
Le carrefour est le nœud, hors sources, touché par au moins deux ondes,
dont l'énergie dépasse le seuil et dont le total est maximal.

Loi, sur l'arc le plus fort d'un nœud : le voisin reçoit la moitié.
Un arc plus faible reçoit moitié × (poids / poids_max des arcs sortants).
On n'additionne pas les degrés : ce serait une autre loi, pas celle du tissu.
"""

from __future__ import annotations

from collections import defaultdict


def _voisins_du_graphe(graphe: dict):
    adj: dict[str, list[tuple[str, float]]] = {}
    for src, dest in graphe.items():
        arcs = []
        if isinstance(dest, dict):
            items = dest.items()
        else:
            items = dest
        for cible, poids in items:
            p = float(poids)
            if p > 0:
                arcs.append((cible, p))
        adj[src] = arcs

    def voisins(noeud: str):
        return adj.get(noeud, [])

    return voisins


def raisonner_par_resonance(
    concepts_sources,
    seuil_energie: float = 0.1,
    max_sauts: int = 3,
    *,
    graphe: dict | None = None,
    voisins=None,
    budget_expansions: int = 50000,
    tracer: set | None = None,
) -> dict:
    """`concepts_sources` seulement. Le graphe est déjà là. Pas de prompt."""
    from ratiss_v3 import LUMIERE, norm

    if voisins is None:
        if graphe is None:
            raise ValueError("résonance : fournir le graphe, ou appeler la méthode du tissu")
        voisins = _voisins_du_graphe(graphe)

    sources = []
    for s in concepts_sources:
        n = norm(s) if not isinstance(s, str) else norm(s)
        if n and n not in sources:
            sources.append(n)
    if not sources:
        raise ValueError("au moins un concept source")

    seuil = float(seuil_energie)
    sauts = max(0, int(max_sauts))
    energie: dict[str, float] = defaultdict(float)
    provenance: dict[str, set[str]] = defaultdict(set)
    premier_saut: dict[str, int] = {}
    tronque = False
    expansions = 0

    for src in sources:
        # Ce que ce front a encore le droit d'émettre. La source émet 1.0.
        # Elle ne compte pas dans l'énergie reçue : une antenne n'est pas un carrefour.
        front: dict[str, float] = {src: 1.0}
        deja_emis = {src}
        for hop in range(1, sauts + 1):
            if not front or tronque:
                break
            arrivée: dict[str, float] = defaultdict(float)
            for noeud, emis in front.items():
                expansions += 1
                if expansions > budget_expansions:
                    tronque = True
                    break
                arcs = [(c, p) for c, p in voisins(noeud) if p > 0 and c != noeud]
                if not arcs:
                    continue
                pmax = max(p for _, p in arcs)
                if pmax <= 0:
                    continue
                for cible, poids in arcs:
                    apport = emis * LUMIERE * (poids / pmax)
                    if apport > 0:
                        arrivée[cible] += apport
            if tronque:
                break
            suivant: dict[str, float] = {}
            for cible, apport in arrivée.items():
                energie[cible] += apport
                provenance[cible].add(src)
                if cible not in premier_saut:
                    premier_saut[cible] = hop
                if cible not in deja_emis:
                    suivant[cible] = suivant.get(cible, 0.0) + apport
            for cible in suivant:
                deja_emis.add(cible)
            front = suivant

    carrefours = []
    for noeud, total in energie.items():
        origines = provenance.get(noeud, set())
        if noeud in sources:
            continue
        if len(origines) < 2 or total < seuil:
            continue
        carrefours.append(
            {
                "noeud": noeud,
                "energie": total,
                "sources": sorted(origines),
                "sauts": premier_saut.get(noeud, sauts),
            }
        )
    carrefours.sort(key=lambda r: (-r["energie"], r["noeud"]))

    plus_actifs = sorted(
        (
            {
                "noeud": n,
                "energie": e,
                "sources": sorted(provenance.get(n, ())),
                "sauts": premier_saut.get(n, sauts),
            }
            for n, e in energie.items()
            if e >= seuil and n not in sources
        ),
        key=lambda r: (-r["energie"], r["noeud"]),
    )[:15]

    return {
        "sources": sources,
        "seuil_energie": seuil,
        "max_sauts": sauts,
        "carrefour": carrefours[0]["noeud"] if carrefours else None,
        "carrefours": carrefours,
        "plus_actifs": plus_actifs,
        "energie": {
            n: e
            for n, e in energie.items()
            if e >= seuil or (tracer is not None and n in tracer)
        },
        "tronque": tronque,
        "expansions": expansions,
    }
