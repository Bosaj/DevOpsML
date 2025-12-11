def supprimer_doublons_consecutifs(liste):
    """
    Supprime les doublons consécutifs dans une liste.
    Conserve l'ordre initial.
    
    Exemples:
        [1, 1, 2, 2, 3, 1] → [1, 2, 3, 1]
        ['a', 'a', 'b', 'a'] → ['a', 'b', 'a']
    """
    if not liste:
        return []
    
    resultat = [liste[0]]
    for element in liste[1:]:
        if element != resultat[-1]:
            resultat.append(element)
    
    return resultat
