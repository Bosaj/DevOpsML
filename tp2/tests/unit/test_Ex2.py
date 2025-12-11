from src.Ex2 import supprimer_doublons_consecutifs

def test_liste_avec_doublons_entiers():
    assert supprimer_doublons_consecutifs([1, 1, 2, 2, 3, 1]) == [1, 2, 3, 1]

def test_liste_avec_doublons_strings():
    assert supprimer_doublons_consecutifs(['a', 'a', 'b', 'a']) == ['a', 'b', 'a']

def test_liste_sans_doublons():
    assert supprimer_doublons_consecutifs([1, 2, 3, 4]) == [1, 2, 3, 4]

def test_liste_tous_identiques():
    assert supprimer_doublons_consecutifs([5, 5, 5, 5]) == [5]

def test_liste_vide():
    assert supprimer_doublons_consecutifs([]) == []

def test_liste_un_element():
    assert supprimer_doublons_consecutifs([1]) == [1]

def test_liste_doublons_multiples():
    assert supprimer_doublons_consecutifs([1, 1, 1, 2, 2, 3, 3, 3, 3]) == [1, 2, 3]
