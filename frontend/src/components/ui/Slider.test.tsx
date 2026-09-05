import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { Slider } from "./Slider";

it("renders both independently named bounds for a range filter", () => {
  const html = renderToStaticMarkup(<Slider label="Altitude range" value={[18000, 40000]} unit="ft" />);
  expect(html).toContain('aria-label="Altitude range minimum"');
  expect(html).toContain('aria-label="Altitude range maximum"');
  expect(html).toContain("18000 – 40000");
});

it("keeps the existing name and formatting for a scalar control", () => {
  const html = renderToStaticMarkup(<Slider label="Pressure" value={[4.3]} formatValue={v => v.toFixed(2)} unit="psia" />);
  expect(html).toContain('aria-label="Pressure"');
  expect(html).toContain("4.30");
});
