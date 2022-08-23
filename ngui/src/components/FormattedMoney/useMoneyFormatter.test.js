import React from "react";
import { render } from "react-dom";
import { act } from "react-dom/test-utils";
import TestProvider from "tests/TestProvider";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { useMoneyFormatter } from "./useMoneyFormatter";

const TestComponent = ({ value, type }) => {
  const formatter = useMoneyFormatter();

  return formatter(type, value);
};

const renderMoney = ({ value, type }) => (
  <TestProvider>
    <TestComponent value={value} type={type} />
  </TestProvider>
);

it("Common renders without crashing", () => {
  const cases = [
    {
      value: undefined,
      expected: "$0"
    },
    {
      value: null,
      expected: "$0"
    },
    {
      value: -10000,
      expected: "-$10,000"
    },
    {
      value: -10.005,
      expected: "-$10.01"
    },
    {
      value: -0.001,
      expected: "\u2248$0"
    },
    {
      value: 0,
      expected: "$0"
    },
    {
      value: 0.001,
      expected: "\u2248$0"
    },
    {
      value: 10.005,
      expected: "$10.01"
    },
    {
      value: 10.05,
      expected: "$10.05"
    },
    {
      value: 10000,
      expected: "$10,000"
    }
  ];
  const div = document.createElement("div");
  cases.forEach(({ value, expected }) => {
    act(() => {
      render(renderMoney({ value, type: FORMATTED_MONEY_TYPES.COMMON }), div);
    });
    expect(div.textContent).toBe(expected);
  });
});

it("Compact renders without crashing", () => {
  const cases = [
    {
      value: undefined,
      expected: "$0"
    },
    {
      value: null,
      expected: "$0"
    },
    {
      value: -10000,
      expected: "-$10k"
    },
    {
      value: -10.005,
      expected: "-$10.01"
    },
    {
      value: -0.001,
      expected: "\u2248$0"
    },
    {
      value: 0,
      expected: "$0"
    },
    {
      value: 0.001,
      expected: "\u2248$0"
    },
    {
      value: 10.005,
      expected: "$10.01"
    },
    {
      value: 10.05,
      expected: "$10.05"
    },
    {
      value: 10000,
      expected: "$10k"
    }
  ];
  const div = document.createElement("div");
  cases.forEach(({ value, expected }) => {
    act(() => {
      render(renderMoney({ value, type: FORMATTED_MONEY_TYPES.COMPACT }), div);
    });
    expect(div.textContent).toBe(expected);
  });
});

it("Tiny renders without crashing", () => {
  const cases = [
    {
      value: undefined,
      expected: "$0"
    },
    {
      value: null,
      expected: "$0"
    },
    {
      value: -10000,
      expected: "-$10,000"
    },
    {
      value: -10.005,
      expected: "-$10.005"
    },
    {
      value: -0.001,
      expected: "-$0.001"
    },
    {
      value: 0,
      expected: "$0"
    },
    {
      value: 0.001,
      expected: "$0.001"
    },
    {
      value: 10.005,
      expected: "$10.005"
    },
    {
      value: 10.05,
      expected: "$10.05"
    },
    {
      value: 10000,
      expected: "$10,000"
    }
  ];
  const div = document.createElement("div");
  cases.forEach(({ value, expected }) => {
    act(() => {
      render(renderMoney({ value, type: FORMATTED_MONEY_TYPES.TINY }), div);
    });
    expect(div.textContent).toBe(expected);
  });
});

it("Tiny compact renders without crashing", () => {
  const cases = [
    {
      value: undefined,
      expected: "$0"
    },
    {
      value: null,
      expected: "$0"
    },
    {
      value: -10000,
      expected: "-$10k"
    },
    {
      value: -10.005,
      expected: "-$10.005"
    },
    {
      value: -0.001,
      expected: "-$0.001"
    },
    {
      value: 0,
      expected: "$0"
    },
    {
      value: 0.001,
      expected: "$0.001"
    },
    {
      value: 10.005,
      expected: "$10.005"
    },
    {
      value: 10.05,
      expected: "$10.05"
    },
    {
      value: 10000,
      expected: "$10k"
    }
  ];
  const div = document.createElement("div");
  cases.forEach(({ value, expected }) => {
    act(() => {
      render(renderMoney({ value, type: FORMATTED_MONEY_TYPES.TINY_COMPACT }), div);
    });
    expect(div.textContent).toBe(expected);
  });
});
