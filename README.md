# Description
Ce script permet de récupérer, pour le club de gymnastique artistique féminine de son choix, les résultats des compétitions de la saison 2022 sur le site de la Fédération Française de Gym (https://resultats.ffgym.fr/accueil) via leur api.
Après avoir téléchargé les résultats, un fichier png par compétition est sauvegardé, contenant les graphiques des résultats pour chaque catégorie.

# Utilisation
on doit dans un premier temps déterminer l'ID du club dont on souhaite obtenir les résultats. C'est possible en utilisant la méthode search_club_id(club_name), qui proposera une liste d'ID potentiels. Une fois le club identifié, il suffit de renseigner son ID dans la suite du script.


# Exemple de résultat
![HERBLAY](https://user-images.githubusercontent.com/46487340/159429159-57b1a003-2f1c-4ae0-b5d6-8a21565f4243.png)
Les gymnastes du club sont représentées en couleur, et leur note ainsi que leur classement est indiqué dans la légende. Les autres participantes sont représentées en gris.
