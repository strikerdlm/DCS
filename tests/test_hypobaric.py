"""Published worked examples and applicability checks for the separate endpoint."""
import pytest
from fastapi.testclient import TestClient
from tinydcs.api import app

client = TestClient(app)
url = "/api/v2/hypobaric/probability"
example = dict(plateauPressurePsia=4.3, elapsedPlateauHours=6, depressurizationMinutes=15,
               arrivalTissueN2Psia=4.3*1.23, singleConstantPlateau=True, ambulationAtPlateau=True,
               bmiKgM2=24, sourceRepressurizationProtocol=False)


def calculate(**changes):
    response = client.post(url, json=example | changes)
    assert response.status_code == 200
    return response.json()


def test_published_exploration_atmosphere():
    assert calculate()["pDcsPercent"] == pytest.approx(3.1, abs=.05)
    assert calculate(elapsedPlateauHours=4)["pDcsPercent"] == pytest.approx(1.8, abs=.06)


@pytest.mark.parametrize(("pressure", "tr"), [(5.3, 1.29), (6.5, 1.35), (7.5, 1.39)])
def test_table_5_rounded_tissue_ratios(pressure, tr):
    result = calculate(plateauPressurePsia=pressure, arrivalTissueN2Psia=pressure*tr,
                       elapsedPlateauHours=4, maleReferenceCohort=True)
    assert result["model"] == "Conkin-1996-Eq7"
    # The source rounds both TR and its 3.0% target in Table 5.
    assert result["pDcsPercent"] == pytest.approx(3.0, abs=.3)


@pytest.mark.parametrize("changes", [
    {"plateauPressurePsia": 10.907}, {"depressurizationMinutes": 1},
    {"elapsedPlateauHours": .025}, {"singleConstantPlateau": False},
    {"arrivalTissueN2Psia": None}, {"ambulationAtPlateau": None},
    {"arrivalTissueN2Psia": 4.3*.79}, {"bmiKgM2": None},
    {"sourceRepressurizationProtocol": None},
    {"plateauPressurePsia": 6.5, "arrivalTissueN2Psia": 6.5*1.35},
    {"plateauPressurePsia": 6.5, "arrivalTissueN2Psia": 6.5*1.35,
     "maleReferenceCohort": True, "elapsedPlateauHours": 6},
])
def test_abstains(changes):
    result = calculate(**changes)
    assert result["reason"] and result["model"] is None and result["pDcsPercent"] is None


def test_inputs_and_directions():
    assert client.post(url, json=example | {"spo2": 100}).status_code == 422
    assert client.post(url, json=example | {"ambulationAtPlateau": "false"}).status_code == 422
    assert calculate(ambulationAtPlateau=False)["pDcsPercent"] < calculate()["pDcsPercent"]
    assert calculate(sourceRepressurizationProtocol=True)["pDcsPercent"] < calculate()["pDcsPercent"]
