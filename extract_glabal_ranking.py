import json
from datetime import datetime
import requests
import pandas as pd

pd.set_option('display.max_rows', None)

# Filtre de la catégorie souhaitée
CATEGORY_FILTER = 'Nationale 10 ans GAF'


def get_data_from_json(list_js_data):
    """
    Parcourt la liste des JSON d'événements et extrait les résultats individuels
    de la catégorie CATEGORY_FILTER pour les compétitions inter-départementales.
    On suppose que l'événement contient une clé 'type' indiquant 'inter-départementale'.
    """
    records = []
    for event_ in list_js_data:

        assert len(event_) == 1, "Erreur: plusieurs événements trouvés dans le JSON."
        event = event_[0]
        # On filtre les catégories sur le label et en ne gardant que les résultats individuels
        categories = [c for c in event['categories'] if c.get('label') == CATEGORY_FILTER and c.get('entityType') != 'EQU']
        if not categories:
            continue

        # Récupérer quelques infos sur l'événement
        # lieu = event['event'].get('lieu', 'Inconnu')
        # date_debut = datetime.strptime(event['event']['dateDebut'][:10], '%Y-%m-%d')
        # date_fin = datetime.strptime(event['event']['dateFin'][:10], '%Y-%m-%d')
        # event_title = f"{lieu} - {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}"

        # Parcourir les catégories retenues
        for categorie in categories:
            # Traiter les résultats individuels
            for entity in categorie.get('entities', []):
                try:
                    if float(entity['mark']['value']) <= 1e-6:
                        continue
                except (KeyError, ValueError):
                    continue

                # Construire un enregistrement pour chaque gymnaste
                record = {
                    # 'Event': event_title,
                    'City': entity.get('city', ''),
                    'Firstname': entity.get('firstname', ''),
                    'Lastname': entity.get('lastname', '')
                }
                record['Global'] = float(entity['mark'].get('value', 0))
                records.append(record)
    return records


def compute_average_scores(records):
    """
    Pour chaque gymnaste, cumule toutes les notes globales et calcule la moyenne globale.
    Si un gymnaste apparaît dans plusieurs compétitions, on agrège toutes ses notes.
    """
    # Dictionnaire pour accumuler les scores globaux et la ville du club de chaque gymnaste
    gymnast_scores = {}
    for record in records:
        key = (record.get('Firstname', ''), record.get('Lastname', ''))
        global_score = record.get('Global', 0)
        if global_score:
            if key in gymnast_scores:
                gymnast_scores[key]['scores'].append(global_score)
            else:
                gymnast_scores[key] = {
                    'scores': [global_score],
                    'City': record.get('City', '')
                }

    # Calculer la moyenne pour chaque gymnaste et construire le tableau final
    results = []
    for (firstname, lastname), data in gymnast_scores.items():
        scores = data['scores']
        city = data['City']
        avg_score = sum(scores) / len(scores) if scores else 0
        results.append({
            'Prénom': firstname,
            'Nom': lastname,
            'Ville': city,
            'Nombre de compétitions': len(scores),
            'Note moyenne': round(avg_score, 2)
        })
    df = pd.DataFrame(results)
    df = df.sort_values(by='Note moyenne', ascending=False)
    return df


def get_data_in_json(year, export=False):
    """
    Récupère la liste des événements via l'API FFGym.
    Le payload est adapté pour la saison et peut être complété si besoin pour filtrer
    les compétitions inter-départementales (si l'API le permet).
    """
    url_post = 'https://resultats.ffgym.fr/api/search/criteria'
    payload = {"season": year, "discipline": 401}  # Ajuster si nécessaire
    post_d = requests.post(url_post, json=payload)
    list_of_jsons = []
    for event_info in json.loads(post_d.text).get('listEvenement', []):
        event_id = event_info.get('id')
        if not event_id:
            continue
        print(f"Récupération de l'événement {event_id}...", end='')
        get_d = requests.get(f"https://resultats.ffgym.fr/api/palmares/evenement/{event_id}")
        try:
            event_json = json.loads(get_d.text)
        except Exception as e:
            print(f"Erreur lors du décodage de l'événement {event_id}: {e}")
            continue
        list_of_jsons.append(event_json)
        if export:
            with open(f"/tmp/event_{event_id}.json", 'w') as f:
                json.dump(get_d.text, f)
        print(" OK!")
    return list_of_jsons


if __name__ == '__main__':
    # Exemple d'utilisation pour l'année 2025
    year = '2025'
    list_jsons = get_data_in_json(year, export=True)
    records = get_data_from_json(list_jsons)
    if not records:
        print("Aucun résultat trouvé pour les compétitions inter-départementales en individuel de la catégorie Nationale 10 ans GAF.")
    else:
        df = compute_average_scores(records)
        print("\nTableau des moyennes pour chaque gymnaste :\n")
        print(df.to_string(index=False))
        # Exporter le DataFrame au format Excel
        df.to_csv("palmares.csv", index=False)
        df.to_excel("palmares.xlsx", index=False)
        print("\nLe fichier Excel a été exporté sous le nom 'palmares.xlsx'.")
