import React from "react";
import SummaryGrid from "components/SummaryGrid";
import { KINDS } from "stories";
import { SUMMARY_VALUE_COMPONENT_TYPES, SUMMARY_CARD_TYPES } from "utils/constants";

export default {
  title: `${KINDS.COMPONENTS}/SummaryGrid`,
  argTypes: {
    value: { name: "Value", control: "number", defaultValue: 100 }
  }
};

const basicCardsSummaryData = [
  {
    key: 1,
    value: "String value",
    captionMessageId: "name"
  },
  {
    key: 2,
    value: 11223.112331,
    captionMessageId: "pool"
  },
  {
    key: 3,
    valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
    valueComponentProps: {
      value: 1042
    },
    captionMessageId: "amount"
  },
  {
    key: 53,
    valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
    valueComponentProps: {
      value: 43124124
    },
    captionMessageId: "amount"
  },
  {
    key: 4,
    valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMessage,
    valueComponentProps: {
      id: "never"
    },
    captionMessageId: "lastCheckTime"
  },
  {
    key: 5,
    valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMessage,
    valueComponentProps: {
      id: "never"
    },
    captionMessageId: "lastCheckTime",
    color: "error"
  },
  {
    key: 6,
    valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
    valueComponentProps: {
      value: 0.0031
    },
    captionMessageId: "forecast",
    color: "success",
    help: {
      show: true,
      messageId: "thisMonthForecast"
    }
  },
  {
    key: 7,
    valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
    CustomValueComponent: () => "Custom value render",
    captionMessageId: "pool"
  },
  {
    key: 8,
    value: "String value",
    captionMessageId: "name",
    isLoading: true
  }
];

const extendedCardsSummaryData = [
  {
    key: 1,
    type: SUMMARY_CARD_TYPES.EXTENDED,
    value: "Number relative value",
    captionMessageId: "name",
    relativeValue: 14,
    relativeValueCaptionMessageId: "amount"
  },
  {
    key: 2,
    type: SUMMARY_CARD_TYPES.EXTENDED,
    value: "String relative value",
    captionMessageId: "name",
    relativeValue: "Value",
    relativeValueCaptionMessageId: "success"
  },
  {
    key: 3,
    value: "My name is...",
    type: SUMMARY_CARD_TYPES.EXTENDED,
    captionMessageId: "organization",
    relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMessage,
    relativeValueComponentProps: {
      id: "hystax"
    },
    relativeValueCaptionMessageId: "name",
    color: "success",
    help: {
      show: true,
      messageId: "hystax"
    }
  }
];

export const commonCards = () => <SummaryGrid summaryData={basicCardsSummaryData} />;

export const cardsWithFormattedMoney = (args) => (
  <SummaryGrid
    summaryData={[
      {
        key: 1,
        captionMessageId: "totalExpensesMonthToDate",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
        valueComponentProps: {
          value: args.value
        }
      },
      {
        key: 2,
        type: SUMMARY_CARD_TYPES.EXTENDED,
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
        valueComponentProps: {
          value: args.value
        },
        captionMessageId: "totalExpensesMonthToDate",
        relativeValue: 12,
        relativeValueCaptionMessageId: "lessThanForPreviousMonth"
      }
    ]}
  />
);

export const extendedCards = () => <SummaryGrid summaryData={extendedCardsSummaryData} />;
