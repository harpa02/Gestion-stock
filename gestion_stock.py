import time
from datetime import datetime

# --- DONNÉES GLOBALES ---
STOCK = {
    "A1": [{"id": "A1", "date": "10:00:00"}, {"id": "A1", "date": "10:05:00"}],
    "B3": [{"id": "B3", "date": "09:30:00"}],
    "C4": [],  # Vide pour tester la rupture
    "C5": [{"id": "C5", "date": "08:00:00"}]  # Dispo pour tester la substitution
}
ALERT_LOG = [None] * 3
SEUIL_MIN = 2


# --- SERVICE : GESTION DES ALERTES (STRUCTURE STATIQUE) ---

def log_alerte(sku):
    """Ajoute une alerte dans le buffer de 3 places max."""
    global ALERT_LOG
    if None in ALERT_LOG:
        # On évite les doublons d'alertes pour le même produit
        message = f"{sku} (Stock Bas)"
        if message not in ALERT_LOG:
            index_libre = ALERT_LOG.index(None)
            ALERT_LOG[index_libre] = message
    else:
        print(f"⚠️ LOG PLEIN : Alerte sur {sku} ignorée !")


def print_alerte():
    """Affiche et acquitte (vide) les alertes."""
    print("\n--- JOURNAL DES ALERTES ---")
    for i in range(len(ALERT_LOG)):
        if ALERT_LOG[i]:
            print(f"Slot {i + 1}: {ALERT_LOG[i]}")
            ALERT_LOG[i] = None  # Libère la place


# --- SERVICE : STOCK ENGINE (ENTRÉE / CONTRÔLE) ---

def ajouter_produit(sku):
    """Service d'entrée en stock (Traçabilité FIFO)."""
    now = datetime.now().strftime("%H:%M:%S")
    if sku not in STOCK:
        STOCK[sku] = []
    STOCK[sku].append({"id": sku, "date": now})
    print(f"✅ Entrée Stock : {sku} à {now}")


def verifier_seuil(sku):
    """Vérifie si le stock passe sous le seuil critique."""
    if len(STOCK.get(sku, [])) < SEUIL_MIN:
        log_alerte(sku)


# --- SERVICE : RUPTURE (STRATÉGIES) ---

def appliquer_strategie_rupture(sku):
    """Gère les manques : tente Substitution, sinon Backorder."""
    # 1. Tentative de Substitution (Volume + 1)
    famille = sku[0]
    try:
        volume = int(sku[1:])
        substitut_id = f"{famille}{volume + 1}"

        if substitut_id in STOCK and STOCK[substitut_id]:
            produit = STOCK[substitut_id].pop(0)
            print(f"🔄 SUBSTITUTION : {sku} remplacé par {substitut_id}")
            return produit
    except ValueError:
        pass  # Cas où l'ID n'est pas standard (ex: "ID_TEST")

    # 2. Backorder (Par défaut)
    print(f"❌ RUPTURE : {sku} manquant (Backorder enregistré)")
    log_alerte(sku)
    return None


# --- SERVICE : LOGISTIQUE (PRÉPARATION COLIS) ---

def preparer_colis(commande_str):
    """Cœur du système : Tri LIFO + Sortie FIFO."""
    try:
        # Nettoyage et séparation de la saisie
        liste_skus = [x.strip() for x in commande_str.split(',')]

        # TRI PAR VOLUME (LIFO) : Le plus gros en premier
        # On utilise l'ID (ex: A5 > A1) pour simuler le volume
        skus_tries = sorted(liste_skus, key=lambda x: int(x[1:]), reverse=True)

        colis_final = []
        print("\n--- PRÉPARATION DU COLIS ---")

        for sku in skus_tries:
            if sku in STOCK and STOCK[sku]:
                # SORTIE FIFO : Le plus vieux en premier
                produit = STOCK[sku].pop(0)
                colis_final.append(produit)
                print(f"Sortie : {produit['id']} (Entré à {produit['date']})")
                verifier_seuil(sku)
            else:
                # GESTION RUPTURE
                res = appliquer_strategie_rupture(sku)
                if res:
                    colis_final.append(res)

        return colis_final
    except Exception as e:
        print(f"⚠️ Erreur de saisie : {e}")


# --- INTERFACE UTILISATEUR (MAIN) ---

if __name__ == "__main__":
    while True:
        choix = input("\n1.Ajout 2.Colis 3.Alertes 4.Stock 5.Exit : ")

        if choix == "1":
            saisie = input("Produits (ex: A1, B3) : ")
            for item in saisie.split(','):
                ajouter_produit(item.strip())

        elif choix == "2":
            saisie = input("Commande (ex: A1, B3, C4) : ")
            preparer_colis(saisie)

        elif choix == "3":
            print_alerte()

        elif choix == "4":
            print("\n--- ÉTAT DU STOCK ---")
            for sku, items in STOCK.items():
                dates = [p['date'] for p in items]
                print(f"{sku} ({len(items)} unités) : {dates}")

        elif choix == "5":
            print("Arrêt du système.")
            break