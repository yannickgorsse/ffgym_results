import pytest
import os
import sys
import types

# Create dummy modules to satisfy analyse_palmares imports without requiring
# the actual heavy dependencies.
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
from analyse_palmares import filter_data_with


def test_filter_data_removes_unmatched_categories_and_events():
    data = {
        ("Event1", "date"): {
            ("Cat1", "EQU"): {("GIF SUR YVETTE", "Team1"): {"classement": 1, "gyms": {}}},
            ("Cat2", "EQU"): {("OTHER", "TeamB"): {"classement": 1, "gyms": {}}},
        },
        ("Event2", "date"): {
            ("Cat3", "EQU"): {("OTHER", "TeamC"): {"classement": 1, "gyms": {}}}
        },
    }

    filtered = filter_data_with(data, "GIF SUR YVETTE")

    assert ("Event1", "date") in filtered
    assert ("Cat1", "EQU") in filtered[("Event1", "date")]
    assert ("Cat2", "EQU") not in filtered[("Event1", "date")]

    assert ("Event2", "date") not in filtered
