import json
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from math import ceil
import copy
import requests
import pandas as pd

pd.set_option("display.max_rows", None)

GAF = 401
NY = 2
AGRES = ["Saut", "Barres asymétriques", "Poutre", "Sol"]
AGRES = [*AGRES, AGRES[0]]

def get_data_from_json(my_js_data):
    discipline = "GYM ARTISTIQUE FEMININE"
    my_data = {}
    for event in my_js_data:
        print(event["event"]["lieu"])
        categories = [c for c in event["categories"] if c["labelDiscipline"] == discipline]
        if len(categories) == 0:
            continue
        lieu = event["event"]["lieu"]
        date_debut = datetime.strptime(event["event"]["dateDebut"][:10], "%Y-%m-%d")
        date_fin = datetime.strptime(event["event"]["dateFin"][:10], "%Y-%m-%d")
        date_debut, date_fin = date_debut.strftime("%d/%m/%Y"), date_fin.strftime("%d/%m/%Y")
        title = (lieu, f"{date_debut} - {date_fin}")
        my_data[title] = {}
        for categorie in categories:
            all_gyms = {}
            cat = (categorie["label"], categorie["entityType"])
            my_data[title][cat] = {}
            if categorie["entityType"] == "EQU":
                for team in categorie["teams"]:
                    city_team = (team["city"], team["label"])
                    my_data[title][cat][city_team] = {"classement": team["markRank"], "gyms": {}}
                    for entity in team["entities"]:
                        if "mark" in entity:
                            my_data[title][cat][city_team]["gyms"][(entity["firstname"], entity["lastname"])] = {}
                            my_data[title][cat][city_team]["gyms"][(entity["firstname"], entity["lastname"])]["total"] = entity["mark"]["value"]
                            if (entity["firstname"], entity["lastname"]) in all_gyms:
                                raise Exception("pouet")
                            all_gyms[(entity["firstname"], entity["lastname"])] = float(entity["mark"]["value"])
                            for appm in entity["mark"]["appMarks"]:
                                my_data[title][cat][city_team]["gyms"][(entity["firstname"], entity["lastname"])][appm["labelApp"]] = appm["value"]
            else:
                for entity in categorie["entities"]:
                    if float(entity["mark"]["value"]) > 1e-6:
                        city_team = (entity["city"], "eq0")
                        if city_team not in my_data[title][cat]:
                            my_data[title][cat][city_team] = {"classement": -1, "gyms": {}}
                        my_data[title][cat][city_team]["gyms"][(entity["firstname"], entity["lastname"])] = {}
                        my_data[title][cat][city_team]["gyms"][(entity["firstname"], entity["lastname"])]["total"] = entity["mark"]["value"]
                        if (entity["firstname"], entity["lastname"]) in all_gyms:
                            raise Exception("pouet")
                        all_gyms[(entity["firstname"], entity["lastname"])] = float(entity["mark"]["value"])
                        for appm in entity["mark"]["appMarks"]:
                            my_data[title][cat][city_team]["gyms"][(entity["firstname"], entity["lastname"])][appm["labelApp"]] = appm["value"]
            dic_rank = {key: rank for rank, key in enumerate(sorted(all_gyms, key=all_gyms.get, reverse=True), 1)}
            for city, gyms in my_data[title][cat].items():
                for nom_gym, _ in gyms["gyms"].items():
                    my_data[title][cat][city]["gyms"][nom_gym]["rankCalc"] = dic_rank[nom_gym]

    return my_data


def filter_data_with(d, filter_str):
    filtered_dic = copy.deepcopy(d)

    for ne, event in d.items():
        for nc, cat in event.items():
            with_gif = False
            for (city, _), _ in cat.items():
                if city == filter_str:
                    with_gif = True
            if not with_gif:
                del filtered_dic[ne][nc]
        if len(filtered_dic[ne]) == 0:
            del filtered_dic[ne]

    return filtered_dic


def search_club_id(club_name, club_id=None):
    if club_id is not None:
        return club_id
    p = club_name.replace(" ", "%20")
    url_post = f"https://resultats.ffgym.fr/api/search/simple?season=2022&pattern={p}"
    results = json.loads(requests.get(url_post).text)
    print("possible ids :")
    for r in results:
        print(f"{r['label']:50} : {r['id']}")
    return input("Choisir le bon id : ")

def get_data_in_json(club_id, year, export=False):
    url_post = f"https://resultats.ffgym.fr/api/search/criteria"
    post_d = requests.post(url_post, json={"season": year,"discipline": GAF,"idEntity":club_id, "type":"CLUB"})
    list_of_jsons = []
    for id in [x["id"] for x in json.loads(post_d.text)["listEvenement"]]:
        print(f"get event {id}...", end="")
        get_d = requests.get(f"https://resultats.ffgym.fr/api/palmares/evenement/{id}")
        list_of_jsons.append(json.loads(get_d.text))
        if export:
            with open(f"/tmp/event_{id}.json", "w") as f: json.dump(get_d.text, f)
        print(f" OK!")
    return list_of_jsons

def get_total_number_of_gym(cat):
    nb_gym = 0
    for _, data_city in cat.items():
        nb_gym += len(data_city["gyms"])
    return nb_gym

def get_teams_of(club_name, cat):
    teams = []
    for (city, team), _ in cat.items():
        if city == club_name:
            teams.append(team)
    return teams

def plot_cat_data(cat, axs, nx, i, label_loc, nb_gym, teams):
    note_max = 0
    for (city, team), data_city in cat.items():
        for nom_gym, notes in data_city["gyms"].items():
            marks = [float(notes[a]) if a in notes else 0 for a in AGRES]
            note_max = max(note_max, max(marks))
            shor_team_name = team[:2] + team[-1]
            eq = f" {shor_team_name} " if len(teams) > 1 else " "
            label = f"{nom_gym[0]}{eq}: total {float(notes['total']):.1f}, {notes['rankCalc']}$^e$/{nb_gym}"
            (axs[i // NY, i % NY] if nx > 1 else axs[i % NY]).plot(
                label_loc,
                marks,
                label=None if city != club_name else label,
                color="grey" if city != club_name else None,
                zorder=100 if city == club_name else 1,
                linewidth=2.5 if city == club_name else 0.75,
            )
    return note_max

def get_title_of(name_cat, teams, cat, entype):
    t = name_cat
    for team in teams:
        t_ = "\nClassement " + (team if len(teams) > 1 else "")
        t += (f"{t_} : {cat[(club_name, team)]['classement']}/{len(cat)}") if entype == "EQU" else ""
    t += "\n"
    return t

def plot_event_data(event, axs, nx):
    for i, ((name_cat, entype), cat) in enumerate(event.items()):
        nb_gym = get_total_number_of_gym(cat)
        label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(AGRES))
        teams = get_teams_of(club_name, cat)
        note_max = plot_cat_data(cat, axs, nx, i, label_loc, nb_gym, teams)
        t = get_title_of(name_cat, teams, cat, entype)

        (axs[i // NY, i % NY] if nx > 1 else axs[i % NY]).set_title(t, size=15)
        (axs[i // NY, i % NY] if nx > 1 else axs[i % NY]).set_yticks(list(range(ceil(note_max))))
        _, _ = (axs[i // NY, i % NY] if nx > 1 else axs[i % NY]).set_thetagrids(np.degrees(label_loc), labels=AGRES, zorder=50)
        (axs[i // NY, i % NY] if nx > 1 else axs[i % NY]).legend(loc="upper right", bbox_to_anchor=(1.2 if entype == "EQU" else 1.0, 1.1))

def plot_json_data(my_dic):
    for (name_event, dates), event in my_dic.items():
        nx = ceil(len(event) / NY)
        fig, axs = plt.subplots(nx, NY, subplot_kw={"projection": "polar"}, figsize=(8 * NY, 8 * nx))
        fig.suptitle(f"{name_event} - {dates}\n", fontsize=20)
        plot_event_data(event, axs, nx)

        if len(event) % 2:
            if nx > 1:
                axs[-1, -1].axis("off")
            else:
                axs[-1].axis("off")
        name_event_modif = "_".join(name_event.split())
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.05 / nx)
        fig.savefig(f"{name_event_modif}.png")
        plt.close(fig)

def plot_data(list_of_jsons, club_name):
    for json_data in list_of_jsons:
        try: my_dic = get_data_from_json(json_data)
        except: my_dic = dict()
        my_dic = filter_data_with(my_dic, club_name)
        plot_json_data(my_dic)

if __name__ == "__main__":

    club_name = "GIF SUR YVETTE"
    club_id = search_club_id(club_name)
    # club_id = "2862"
    list_of_jsons = get_data_in_json(club_id, "2023", export=True)
    plot_data(list_of_jsons, club_name)
