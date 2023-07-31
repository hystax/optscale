import React from "react";
import { createRoot } from "react-dom/client";
import { act } from "react-dom/test-utils";
import TestProvider from "tests/TestProvider";
import FormattedDigitalUnit, { IEC_UNITS, SI_UNITS } from "./FormattedDigitalUnit";

const renderFormattedDigitalUnit = ({ value, baseUnit }) => (
  <TestProvider>
    <FormattedDigitalUnit value={value} baseUnit={baseUnit} />
  </TestProvider>
);

it("Common format IEC byte unit without crashing", () => {
  const testCases = [
    { value: 0, expected: "0 B" },
    { value: 0.00001, expected: "≈0 B" },
    { value: 0.5, expected: "0.5 B" },
    { value: 1023, expected: "1,023 B" },
    { value: 1024, expected: "1 KiB" },
    { value: 312312312, expected: "297.844 MiB" }
  ];

  testCases.forEach(({ value, expected }) => {
    const div = document.createElement("div");
    const root = createRoot(div);
    act(() => {
      root.render(renderFormattedDigitalUnit({ value, baseUnit: IEC_UNITS.BYTE }));
    });
    expect(div.textContent).toBe(expected);
    root.unmount();
  });
});

it("Common format SI byte unit without crashing", () => {
  const testCases = [
    { value: 0, expected: "0 B" },
    { value: 0.00001, expected: "≈0 B" },
    { value: 0.5, expected: "0.5 B" },
    { value: 1023, expected: "1.023 KB" },
    { value: 1024, expected: "1.024 KB" },
    { value: 312312312, expected: "312.312 MB" }
  ];

  testCases.forEach(({ value, expected }) => {
    const div = document.createElement("div");
    const root = createRoot(div);
    act(() => {
      root.render(renderFormattedDigitalUnit({ value, baseUnit: SI_UNITS.BYTE }));
    });
    expect(div.textContent).toBe(expected);
    root.unmount();
  });
});
