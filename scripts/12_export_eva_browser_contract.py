"""Regenerate the offline contract, mission rules and Python/browser golden cases.

Run from the repository root: .venv/bin/python scripts/12_export_eva_browser_contract.py
The fixtures are synthetic software checks, not clinical observations.
"""
from pathlib import Path
import copy
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tinydcs.eva import available_mission_rule_profiles, load_mission_rules, simulate_eva
from tinydcs.eva_contract import EVAScenario
from tests.test_eva import eva_scenario


def main():
    output = Path(__file__).resolve().parents[1]/"frontend/src/data"
    schema = EVAScenario.model_json_schema()
    rules = {p: load_mission_rules(p) for p in available_mission_rule_profiles()}
    cases = []
    for profile in rules:
        for duration in [0, 83, 240, 360]:
            s = eva_scenario()
            s["suit"]["variablePressure"] = False
            s["evaDurationMin"], s["workload"] = duration, []
            if duration == 240:
                s["suit"]["pressurePsia"] = 4.3
                s["nasaAdynamicReference"] = True
            if duration == 83:
                s["suit"]["variablePressure"] = True
                s["pressureSegments"] = [dict(durationMin=20, pressurePsia=5.8, oxygenFraction=1), dict(durationMin=63, pressurePsia=4.3, oxygenFraction=.98)]
                s["workload"] = [dict(name="first", durationMin=20, vo2MlKgMin=5), dict(name="second", durationMin=63, vo2MlKgMin=25)]
            cases.append(dict(name=f"{profile}-{duration}", scenario=s, options=dict(missionRuleProfile=profile, telemetryNowSec=1000)))
    s = copy.deepcopy(cases[0]["scenario"])
    s["crew"]["symptomFlag"] = True
    s["prebreatheMin"] = 90
    s["prebreatheSegments"] = [dict(durationMin=30,pressurePsia=14.7,oxygenFraction=1,vo2MlKgMin=20), dict(durationMin=60,pressurePsia=8.2,oxygenFraction=.34,vo2MlKgMin=3.5)]
    telemetry = [dict(kind="habitat_pressure",value=8,unit="psia",timestampSec=990),
                 dict(kind="suit_pressure",value=4.3,unit="psia",timestampSec=700),
                 dict(kind="accelerometer",x=0,y=0,z=2,unit="g",timestampSec=990),
                 dict(kind="workload",value=25,unit="vo2",timestampSec=995),
                 dict(kind="skin_temperature",value=38,unit="c",timestampSec=990)]
    cases.append(dict(name="telemetry-stops-mixed-pb",scenario=s,options=dict(missionRuleProfile="default",telemetry=telemetry,telemetryNowSec=1000)))
    for case in cases:
        options = case["options"]
        case["expected"] = simulate_eva(case["scenario"], mission_rules=rules[options["missionRuleProfile"]], telemetry=options.get("telemetry"), telemetry_now_sec=options["telemetryNowSec"])
    for name, value in [("eva-schema.json",schema),("eva-rules.json",rules),("eva-golden.json",cases)]:
        (output/name).write_text(json.dumps(value,indent=2,allow_nan=False)+"\n")
        print(name)


if __name__ == "__main__":
    main()
