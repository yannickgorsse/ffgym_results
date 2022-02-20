import json
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from math import ceil
import copy
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

def get_data_from_json(my_js_file):
    with open(my_js_file, "r") as f:
        parsed = json.load(f)
    my_data = {}
    for event in parsed:
        lieu = event["event"]["lieu"]
        date_debut, date_fin = datetime.strptime(event["event"]["dateDebut"][:10], "%Y-%m-%d"), datetime.strptime(
            event["event"]["dateFin"][:10], "%Y-%m-%d"
        )
        date_debut, date_fin = date_debut.strftime("%d/%m/%Y"), date_fin.strftime("%d/%m/%Y")
        title = (lieu, f"{date_debut} - {date_fin}")
        logging.info(title)
        my_data[title] = {}
        for categorie in event["categories"]:
            all_gyms = {}
            cat = (categorie["label"], categorie["entityType"])
            logging.info(cat)
            my_data[title][cat] = {}
            for team in categorie["teams"]:
                city_team = (team["city"], team["label"])
                my_data[title][cat][city_team] = {"classement": team["markRank"], "gyms": {}}
                for entity in team["entities"]:
                    if "mark" in entity:
                        my_data[title][cat][city_team]["gyms"][(entity["firstname"], entity["lastname"])] = {}
                        logging.info(f"{entity['firstname']} {entity['mark']['value']} {entity['markRank']}") # markRank identique que l'equipe (en tout cas dans le cas equipe)
                        my_data[title][cat][city_team]["gyms"][(entity["firstname"], entity["lastname"])]["total"] = entity["mark"]["value"]
                        if (entity["firstname"], entity["lastname"]) in all_gyms:
                            raise Exception("pouet")
                        all_gyms[(entity["firstname"], entity["lastname"])] = float(entity["mark"]["value"])
                        for appm in entity["mark"]["appMarks"]:
                            logging.info(f"    {appm['labelApp']} {appm['value']}")
                            my_data[title][cat][city_team]["gyms"][(entity["firstname"], entity["lastname"])][appm["labelApp"]] = appm["value"]
                logging.debug(my_data[title])
            dic_rank = {key: rank for rank, key in enumerate(sorted(all_gyms, key=all_gyms.get, reverse=True), 1)}
            for city, gyms in my_data[title][cat].items():
                for nom_gym, _ in gyms["gyms"].items():
                    my_data[title][cat][city]["gyms"][nom_gym]["rankCalc"] = dic_rank[nom_gym]
    return my_data

def filter_data_with(d, filter_str):
    filtered_dic = copy.deepcopy(d)

    for ne, event in my_dic.items():
        for nc, cat in event.items():
            with_gif = False
            for (city, _), _ in cat.items():
                if city == filter_str:
                    with_gif = True
            if not with_gif: del filtered_dic[ne][nc]

    return filtered_dic


if __name__ == "__main__":
    for json_file in ["2022_01_23_morsang.json", "2022_02_13_bretigny.json"]:
        my_dic = get_data_from_json(json_file)
        gif = "GIF SUR YVETTE"
        my_dic = filter_data_with(my_dic, gif)
        agres = ["Saut", "Barres asymétriques", "Poutre", "Sol"]
        agres = [*agres, agres[0]]

        for (name_event, dates), event in my_dic.items():
            ny = 2
            nx = ceil(len(event) / ny)
            fig, axs = plt.subplots(nx, ny, subplot_kw={'projection': 'polar'}, figsize=(8 * ny, 8 * nx))
            fig.suptitle(f"{name_event} - {dates}\n", fontsize=20)
            for i, ((name_cat, entype), cat) in enumerate(event.items()):
                label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(agres))
                note_max = 0
                teams = []
                for (city, team), data_city in cat.items():
                    if city == gif:
                        teams.append(team)
                for (city, team), data_city in cat.items():
                    for nom_gym, notes in data_city["gyms"].items():
                        marks = [float(notes[a]) if a in notes else 0 for a in agres]
                        note_max = max(note_max, max(marks))
                        shor_team_name = team[:2] + team[-1]
                        eq = f" {shor_team_name} " if len(teams) > 1 else " "
                        label = f"{nom_gym[0]}{eq}: total {float(notes['total'])}, {notes['rankCalc']}$^e$"
                        (axs[i // ny, i % ny] if nx > 1 else axs[i % ny]).plot(
                            label_loc,
                            marks,
                            label=None if city != gif else label,
                            color="grey" if city != gif else None,
                            zorder=100 if city == gif else 1,
                            linewidth=2.5 if city == gif else 0.75,
                        )
                t = name_cat # - " + ("équipes" if entype == "EQU" else "indiv")
                for team in teams:
                    t_ = "\nClassement " + (team if len(teams) > 1 else "")
                    t += (f"{t_} : {cat[(gif, team)]['classement']}/{len(cat)}") if entype == "EQU" else ""
                t += "\n"
                (axs[i // ny, i % ny] if nx > 1 else axs[i % ny]).set_title(t, size=15)
                (axs[i // ny, i % ny] if nx > 1 else axs[i % ny]).set_yticks(list(range(ceil(note_max))))
                lines, labels = (axs[i // ny, i % ny] if nx > 1 else axs[i % ny]).set_thetagrids(np.degrees(label_loc), labels=agres, zorder=50)
                (axs[i // ny, i % ny] if nx > 1 else axs[i % ny]).legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))
            name_event_modif = "_".join(name_event.split())
            plt.tight_layout()
            plt.subplots_adjust(bottom=0.05 / nx)
            fig.savefig(f"{name_event_modif}.png")
            # plt.show()
            plt.close(fig)
