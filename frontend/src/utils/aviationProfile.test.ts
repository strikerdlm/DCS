import { describe, expect, it } from "vitest";
import chamberFixture from "../../../docs/examples/aviation-table5.json";
import { buildProfile, exampleForm } from "./aviationProfile";

describe("simple aviation timeline sent to the API", () => {
  it("produces the source fixture evaluated by Python and excludes the plateau from preoxygenation", () => {
    const profile = buildProfile(exampleForm(true));
    expect(profile).toEqual(chamberFixture);
    expect(profile.segments.map(s => [s.start, s.end])).toEqual([[0, 115], [115, 145], [145, 385]]);
    expect(profile.prediction_request.horizon_minutes).toBe(240);
  });
  it("preserves unknown gas and the return rather than substituting a source projection", () => {
    const form = exampleForm();
    form.phases.plateau.oxygen = "";
    form.initialMethod = "unknown";
    form.priorAltitude = "unknown";
    const profile = buildProfile(form);
    expect(profile.segments.find(s => s.phase === "plateau")?.gas).toBeNull();
    expect(profile.history.previous_altitude_exposure).toBeNull();
    expect(profile.prediction_request).toMatchObject({ window: "complete_exposure", horizon_minutes: 60 });
    expect(profile.initial_state.method).toBe("unknown");
  });
  it("splits a late break without losing the resumption time or adding to the nominal period", () => {
    const form = exampleForm();
    form.breakStart = "27";
    form.phases.oxygen_break.minutes = "2";
    const segments = buildProfile(form).segments;
    expect(segments.slice(0, 3).map(s => [s.phase, s.start, s.end])).toEqual([
      ["prebreathe", 0, 27], ["oxygen_break", 27, 29], ["prebreathe", 29, 30],
    ]);
    expect(segments[1].gas?.nitrogen_fraction).toBe(0.79);
    expect(segments[2].gas?.nitrogen_fraction).toBe(0);
    form.breakStart = "29";
    expect(() => buildProfile(form)).toThrow("interruption");
  });
  it("keeps follow-up and complete exposure horizons distinct with the same planned trajectory", () => {
    const form = exampleForm();
    form.phases.post_exposure.minutes = "60";
    const complete = buildProfile(form);
    form.question = "followup";
    const followup = buildProfile(form);
    expect(complete.segments).toEqual(followup.segments);
    expect(complete.prediction_request.horizon_minutes).toBe(60);
    expect(followup.prediction_request.horizon_minutes).toBe(120);
    expect(followup.prediction_request).toMatchObject({ window: "through_follow_up", prediction_origin: "profile_start" });
  });
});
