import React from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { boolean } from "@storybook/addon-knobs";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import PropTypes from "prop-types";
import TableUseMemoWrapper from "stories/Other/TableUseMemoWrapper";
import FormattedMoney from "components/FormattedMoney";
import { v4 as uuidv4 } from "uuid";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Table`
};

const defaultColumns = [
  {
    Header: "String",
    accessor: "string"
  },
  {
    Header: "Type",
    accessor: "type"
  },
  {
    Header: "Number",
    accessor: "number"
  },
  {
    Header: "Formatted Number",
    id: "formattedNumber",
    Cell: ({ row: { original } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={original.number} />
  }
];

const data = [
  {
    string: "String 1",
    number: 1.526,
    type: "Type A"
  },
  {
    string: "String 2",
    number: 2.123,
    type: "Type A"
  },
  {
    string: "String 3",
    number: 3,
    type: "Type B"
  },
  {
    string: "String 4",
    number: 4,
    type: "Type B"
  },
  {
    string: "String 5",
    number: 5,
    type: "Type B"
  },
  {
    string: "String 6",
    number: 6,
    type: "Type A"
  },
  {
    string: "String 7",
    number: 7,
    type: "Type B"
  }
];

const actionBarDefinition = {
  items: [
    {
      key: "bu-add",
      icon: <AddOutlinedIcon fontSize="small" />,
      messageId: "add",
      type: "button",
      action: () => console.log("action add"),
      dataTestId: "btn_add"
    }
  ]
};

export const basic = () => (
  <TableUseMemoWrapper
    localization={{
      emptyMessageId: "notFound"
    }}
    data={data}
    columns={defaultColumns}
  />
);

export const withSearch = () => (
  <TableUseMemoWrapper
    localization={{
      emptyMessageId: "notFound"
    }}
    data={data}
    columns={defaultColumns}
    withSearch
  />
);

export const withSelection = () => (
  <TableUseMemoWrapper
    localization={{
      emptyMessageId: "notFound"
    }}
    data={data}
    columns={defaultColumns}
    addSelectionColumn
  />
);

export const withCounters = () => (
  <TableUseMemoWrapper
    localization={{
      emptyMessageId: "notFound"
    }}
    data={data}
    columns={defaultColumns}
    addSelectionColumn
    counters={{ showCounters: true, hideTotal: false }}
  />
);

const TableWithKnobs = ({ showSearch, showSelection, showCounters, showActionBar, ...rest }) => {
  return (
    <TableUseMemoWrapper
      {...rest}
      withSearch={showSearch}
      addSelectionColumn={showSelection}
      counters={{ showCounters: showCounters, hideTotal: false }}
      actionBar={{
        show: showActionBar,
        definition: actionBarDefinition //  todo: action bar does not working
      }}
      key={uuidv4()} // each time updating key to completely remount table (to avoid hooks length difference error)
    />
  );
};

export const WithKnobs = () => {
  return (
    <TableWithKnobs
      showSearch={boolean("show search:", true)}
      showSelection={boolean("selection:", true)}
      showCounters={boolean("show counters:", true)}
      showActionBar={boolean("show action bar:", true)}
      localization={{
        emptyMessageId: "notFound"
      }}
      data={data}
      columns={defaultColumns}
    />
  );
};

export const empty = () => (
  <TableUseMemoWrapper
    localization={{
      emptyMessageId: "notFound"
    }}
    data={[]}
    columns={[]}
  />
);

TableWithKnobs.propTypes = {
  showSearch: PropTypes.bool.isRequired,
  showSelection: PropTypes.bool.isRequired,
  showCounters: PropTypes.bool.isRequired,
  showActionBar: PropTypes.bool.isRequired
};
