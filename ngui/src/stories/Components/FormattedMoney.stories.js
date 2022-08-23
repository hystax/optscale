import React from "react";
import { number, select } from "@storybook/addon-knobs";
import { useTheme } from "@mui/material/styles";
import Grid from "@mui/material/Grid";
import { KINDS } from "stories";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import FormattedMoney from "components/FormattedMoney";
import { v4 as uuidv4 } from "uuid";

export default {
  title: `${KINDS.COMPONENTS}/FormattedMoney`
};

const getMoneyString = (value, isNegative = false) => (isNegative ? `-$${value}` : `$${value}`);

const getLessThanZeroMoneyString = () => <>&asymp;{getMoneyString("0")}</>;

const getTestCases = (type) => [
  {
    key: uuidv4(),
    rawValue: -5675,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("5675", true),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("5.7k", true),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("5675", true)
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: -5.6756,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("5.68", true),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("5.68", true),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("5.6756", true)
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: -1,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("1", true),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("1", true),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("1", true)
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: -0.0065,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getLessThanZeroMoneyString(),
      [FORMATTED_MONEY_TYPES.COMPACT]: getLessThanZeroMoneyString(),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("0.0065", true)
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 0,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("0"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("0"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("0")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 0.001,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getLessThanZeroMoneyString(),
      [FORMATTED_MONEY_TYPES.COMPACT]: getLessThanZeroMoneyString(),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("0.001")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 7,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("7"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("7"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("7")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 7.0123,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("7.01"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("7.01"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("7.0123")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 12,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("12"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("12"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("12")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 856,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("856"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("856"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("856")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 999.94,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("999.94"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("999.94"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("999.94")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 999.95,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("999.95"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("999.95"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("999.95")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 1000,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("1000"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("1k"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("1k")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 5821,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("5821"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("5.8k"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("5.8k")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 10500,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("10500"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("10.5k"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("10.5k")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 101800,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("101800"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("101.8k"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("101.8k")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 999949.999,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("999,950"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("999.9k"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("999.9k")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 999950,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("999950"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("1M"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("1M")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 2000000,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("2000000"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("2M"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("2M")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 7800000,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("7800000"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("7.8M"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("7.8M")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 92150000,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("92150000"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("92.2M"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("92.2M")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 123200000,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("123200000"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("123.2M"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("123.2M")
    }[type]
  },
  {
    key: uuidv4(),
    rawValue: 9999999,
    expectedFormattedValue: {
      [FORMATTED_MONEY_TYPES.COMMON]: getMoneyString("9999999"),
      [FORMATTED_MONEY_TYPES.COMPACT]: getMoneyString("10M"),
      [FORMATTED_MONEY_TYPES.TINY]: getMoneyString("10M")
    }[type]
  }
];

const GridRow = ({ children }) => {
  const theme = useTheme();

  return (
    <Grid xs={12} container item style={{ borderBottom: `1px solid ${theme.palette.info.light}` }}>
      {children}
    </Grid>
  );
};

export const expectedValues = () => {
  const customNumber = number("Number", 5821);
  const type = select(
    "Purpose",
    [FORMATTED_MONEY_TYPES.COMMON, FORMATTED_MONEY_TYPES.COMPACT, FORMATTED_MONEY_TYPES.TINY],
    FORMATTED_MONEY_TYPES.COMMON
  );
  const Title = ({ text }) => <strong>{text}</strong>;
  return (
    <Grid container spacing={2}>
      <GridRow>
        <Grid xs={4} item>
          <Title text="Value" />
        </Grid>
        <Grid xs={4} item>
          <Title text="Expected output" />
        </Grid>
        <Grid xs={4} item>
          <Title text="FormattedMoney" />
        </Grid>
      </GridRow>
      <GridRow>
        <Grid xs={8} item>
          <span>
            <Title text={"Number:"}></Title> {customNumber}
          </span>
        </Grid>
        <Grid xs={4} item>
          <FormattedMoney value={customNumber} type={type} />
        </Grid>
      </GridRow>
      {getTestCases(type).map(({ key, rawValue, expectedFormattedValue }) => (
        <GridRow key={key}>
          <Grid xs={4} item>
            {rawValue}
          </Grid>
          <Grid xs={4} item>
            {expectedFormattedValue}
          </Grid>
          <Grid xs={4} item>
            <FormattedMoney value={rawValue} type={type} />
          </Grid>
        </GridRow>
      ))}
    </Grid>
  );
};
