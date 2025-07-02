# Description
Ce script permet de récupérer, pour le club de gymnastique artistique féminine de son choix, les résultats des compétitions de la saison 2022 sur le site de la Fédération Française de Gym (https://resultats.ffgym.fr/accueil) via leur API.
Après avoir téléchargé les résultats, un fichier png par compétition est sauvegardé, contenant les graphiques des résultats pour chaque catégorie.

# Utilisation
On réalise en premier lieu une recherche à partir du nom du club, des IDs de club seront alors proposés. Il suffit d'entrer l'ID de son choix et le script va générer une image par compétition en mettant en évidence les gymnastes du club d'intérêt.


# Exemple de résultat
![HERBLAY](https://user-images.githubusercontent.com/46487340/159429159-57b1a003-2f1c-4ae0-b5d6-8a21565f4243.png)
Les gymnastes du club sont représentées en couleur, et leur note ainsi que leur classement est indiqué dans la légende. Les autres participantes sont représentées en gris.

## Tests
Les tests unitaires utilisent `pytest`. Pour lancer la suite de tests, installez les dépendances nécessaires puis exécutez la commande `pytest` à la racine du projet.
