import os
import sys
import types

# Dummy modules to satisfy analyse_palmares imports
matplotlib_dummy = types.ModuleType("matplotlib")
pyplot_dummy = types.ModuleType("pyplot")
setattr(matplotlib_dummy, "pyplot", pyplot_dummy)
sys.modules.setdefault("matplotlib", matplotlib_dummy)
sys.modules.setdefault("matplotlib.pyplot", pyplot_dummy)
sys.modules.setdefault("numpy", types.ModuleType("numpy"))
pd_dummy = types.ModuleType("pandas")
pd_dummy.set_option = lambda *a, **k: None
sys.modules.setdefault("pandas", pd_dummy)
sys.modules.setdefault("requests", types.ModuleType("requests"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from analyse_palmares import get_data_from_json


def test_get_data_from_json_computes_ranks():
    js = [
        {
            "event": {
                "lieu": "Paris",
                "dateDebut": "2023-04-01",
                "dateFin": "2023-04-02",
            },
            "categories": [
                {
                    "label": "Cat1",
                    "entityType": "EQU",
                    "labelDiscipline": "GYM ARTISTIQUE FEMININE",
                    "teams": [
                        {
                            "city": "GIF SUR YVETTE",
                            "label": "Team1",
                            "markRank": 1,
                            "entities": [
                                {
                                    "firstname": "Alice",
                                    "lastname": "Gym",
                                    "mark": {"value": "12", "appMarks": []},
                                }
                            ],
                        },
                        {
                            "city": "OTHER",
                            "label": "Team2",
                            "markRank": 2,
                            "entities": [
                                {
                                    "firstname": "Bob",
                                    "lastname": "Gym",
                                    "mark": {"value": "10", "appMarks": []},
                                }
                            ],
                        },
                    ],
                }
            ],
        }
    ]

    result = get_data_from_json(js)
    title = ("Paris", "01/04/2023 - 02/04/2023")
    assert title in result
    cat_key = ("Cat1", "EQU")
    cat = result[title][cat_key]
    assert cat[("GIF SUR YVETTE", "Team1")]["gyms"][("Alice", "Gym")]["rankCalc"] == 1
    assert cat[("OTHER", "Team2")]["gyms"][("Bob", "Gym")]["rankCalc"] == 2
