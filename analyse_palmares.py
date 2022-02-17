import json
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from math import ceil

def get_data_from_json(my_js_file):
    with open(my_js_file, "r") as f: parsed = json.load(f)
    my_data = {}
    for event in parsed:
        # titre : lieu - date_debut - date_fin
        lieu = event["event"]["lieu"]
        date_debut, date_fin = datetime.strptime(event["event"]["dateDebut"][:10], "%Y-%m-%d"), datetime.strptime(event["event"]["dateFin"][:10], "%Y-%m-%d")
        date_debut, date_fin = date_debut.strftime("%d/%m/%Y"), date_fin.strftime("%d/%m/%Y")
        title = (lieu, f"{date_debut} - {date_fin}")
        print(title)
        my_data[title] = {}
        for categorie in event["categories"]:
            all_gyms = {}
            cat = (categorie["label"], categorie["entityType"])
            print(cat)
            my_data[title][cat] = {}
            for team in categorie["teams"]:
                city_team = (team["city"], team["label"])
                my_data[title][cat][city_team] = {"classement" : team["markRank"], "gyms": {}}
                for entity in team["entities"]:
                    if "mark" in entity:
                        my_data[title][cat][city_team]["gyms"][(entity["firstname"], entity["lastname"])] = {}
                        # print(entity["firstname"], entity["mark"]["value"], entity["markRank"]) # markRank identique que l'equipe (en tout cas dans le cas equipe)
                        my_data[title][cat][city_team]["gyms"][(entity["firstname"], entity["lastname"])]["total"] = entity["mark"]["value"]
                        if (entity["firstname"], entity["lastname"]) in all_gyms: raise Exception("pouet")
                        all_gyms[(entity["firstname"], entity["lastname"])] = float(entity["mark"]["value"])
                        for appm in entity["mark"]["appMarks"]:
                            # print("    ", appm["labelApp"], appm["value"])
                            my_data[title][cat][city_team]["gyms"][(entity["firstname"], entity["lastname"])][appm["labelApp"]] = appm["value"]
                # print(my_data[title])
            dic_rank = {key: rank for rank, key in enumerate(sorted(all_gyms, key=all_gyms.get, reverse=True), 1)}
            for city, gyms in my_data[title][cat].items():
                for nom_gym, _ in gyms["gyms"].items():
                    my_data[title][cat][city]["gyms"][nom_gym]["rankCalc"] = dic_rank[nom_gym]
    return my_data

if __name__ == "__main__":
    # my_dic = get_data_from_json("2022_01_23_morsang.json")
    my_dic = get_data_from_json("2022_02_13_bretigny.json")
    agres = ["Saut", "Barres asymétriques", "Poutre", "Sol"]
    agres = [*agres, agres[0]]

    for (name_event, dates), event in my_dic.items():
        for (name_cat, entype), cat in event.items():
            label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(agres))
            fig = plt.figure(figsize=(8, 8))
            plt.subplot(polar=True)
            note_max = 0
            for (city, team), data_city in cat.items():
                for nom_gym, notes in data_city["gyms"].items():
                    # print(notes)
                    marks = [float(notes[a]) if a in notes else 0 for a in agres]
                    note_max = max(note_max, max(marks))
                    label = f"{nom_gym[0]} : total {float(notes['total'])}, rank {notes['rankCalc']}"
                    plt.plot(label_loc, marks, label=None if city != "GIF SUR YVETTE" else label, color="grey" if city != "GIF SUR YVETTE" else None)
            t = f"{name_event} - {dates}\n{name_cat} - " + ("équipes" if entype == "EQU" else "indiv")
            if ("GIF SUR YVETTE", "Equipe 1") in cat: t += (f"\nClassement : {cat[('GIF SUR YVETTE', 'Equipe 1')]['classement']}/{len(cat)}") if entype == "EQU" else ""
            else: continue
            t += "\n"
            plt.title(t, size=15)
            plt.yticks(list(range(ceil(note_max))))
            plt.subplots_adjust(left=0.01, right=0.99, top=0.8, bottom=0.1)
            lines, labels = plt.thetagrids(np.degrees(label_loc), labels=agres)
            plt.legend(loc="upper right", bbox_to_anchor=(1.1,1.))
            name_event_modif = "_".join(name_event.split())
            name_cat_modif = "_".join(name_cat.split())
            # short_name
            fig.savefig(f"{name_event_modif}_{name_cat_modif}.png")
            # plt.show()
