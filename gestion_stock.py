import time
from datetime import datetime

# --- CONFIGURATION ET DONNÉES GLOBALES ---
# VA: Centralisation des constantes pour la maintenabilité
SEUIL_MIN = 2
ALERT_LOG = [None] * 3

STOCK = {
    "A1": [{"id": "A1", "date": "10:00:00"}, {"id": "A1", "date": "10:05:00"}],
    "B3": [{"id": "B3", "date": "09:30:00"}],
    "C4": [],
    "C5": [{"id": "C5", "date": "08:00:00"}]
}


# --- SERVICE : GESTION DES ALERTES (STRUCTURE STATIQUE) ---

def log_alerte(sku):
    """
    Inscrit une alerte dans le buffer de 3 places max.
    Contrainte: Structure statique à taille fixe.
    """
    global ALERT_LOG
    message_alerte = f"{sku} (Stock Bas)"

    # Évite les doublons dans le registre
    if message_alerte in ALERT_LOG:
        return

    if None in ALERT_LOG:
        index_libre = ALERT_LOG.index(None)
        ALERT_LOG[index_libre] = message_alerte
    else:
        print(f"ALERTE : LOG PLEIN - Signal sur {sku} ignore")


def print_alerte():
    """Affiche les alertes et libère les emplacements (acquittement)."""
    print("\n--- JOURNAL DES ALERTES ---")
    for i in range(len(ALERT_LOG)):
        if ALERT_LOG[i]:
            print(f"Slot {i + 1}: {ALERT_LOG[i]}")
            ALERT_LOG[i] = None

        # --- SERVICE : STOCK ENGINE ---


def ajouter_produit(sku):
    """
    Service d'entrée en stock avec traçabilité temporelle.
    VA: Assure la rotation FIFO.
    """
    horodatage = datetime.now().strftime("%H:%M:%S")
    if sku not in STOCK:
        STOCK[sku] = []

    STOCK[sku].append({"id": sku, "date": horodatage})
    print(f"Entree Stock : {sku} a {horodatage}")


def verifier_seuil(sku):
    """Vérifie si le niveau de stock est inférieur au seuil critique."""
    if len(STOCK.get(sku, [])) < SEUIL_MIN:
        log_alerte(sku)


# --- SERVICE : RUPTURE ET LOGISTIQUE ---

def appliquer_strategie_rupture(sku):
    """
    Gère les ruptures via substitution (Volume +1) ou backorder.
    VA: Résilience du flux logistique.
    """
    famille = sku[0]
    try:
        volume_origine = int(sku[1:])
        substitut_id = f"{famille}{volume_origine + 1}"

        if substitut_id in STOCK and STOCK[substitut_id]:
            produit_substitut = STOCK[substitut_id].pop(0)
            print(f"SUBSTITUTION : {sku} remplace par {substitut_id}")
            return produit_substitut
    except (ValueError, IndexError):
        pass

    print(f"RUPTURE : {sku} manquant (Backorder enregistre)")
    log_alerte(sku)
    return None


def preparer_colis(commande_str):
    """
    Cœur logistique : Tri LIFO (Volume) et sortie FIFO (Date).
    """
    try:
        liste_skus = [s.strip() for s in commande_str.split(',')]

        # Tri par volume décroissant (LIFO)
        skus_ordonnes = sorted(liste_skus, key=lambda x: int(x[1:]), reverse=True)

        print("\n--- PREPARATION DU COLIS ---")
        for sku in skus_ordonnes:
            if sku in STOCK and STOCK[sku]:
                produit = STOCK[sku].pop(0)
                print(f"Sortie : {produit['id']} (Entre a {produit['date']})")
                verifier_seuil(sku)
            else:
                resultat_rupture = appliquer_strategie_rupture(sku)
                # Si substitution réussie, le produit est ajouté au colis
    except Exception as erreur:
        print(f"Erreur de saisie : {erreur}")


# --- INTERFACE UTILISATEUR ---

if __name__ == "__main__":
    while True:
        choix = input("\n1.Ajout 2.Colis 3.Alertes 4.Stock 5.Sortie : ")
        if choix == "1":
            saisie = input("Produits (ex: A1, B3) : ")
            for item in saisie.split(','):
                ajouter_produit(item.strip())
        elif choix == "2":
            preparer_colis(input("Commande : "))
        elif choix == "3":
            print_alerte()
        elif choix == "4":
            print("\n--- ETAT DU STOCK ---")
            for sku, items in STOCK.items():
                print(f"{sku} : {[p['date'] for p in items]}")
        elif choix == "5":
            break