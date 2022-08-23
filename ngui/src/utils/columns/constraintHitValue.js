import React from "react";
import { FormattedMessage } from "react-intl";
import ConstraintValue from "components/ConstraintValue";
import TextWithDataTestId from "components/TextWithDataTestId";
import { POLICY_TYPE_COLUMN_NAMES } from "utils/constants";

const constraintHitValue = ({ type }) => ({
  Header: (
    <TextWithDataTestId dataTestId="lbl_value">
      <FormattedMessage id={POLICY_TYPE_COLUMN_NAMES[type] ?? "value"} />
    </TextWithDataTestId>
  ),
  accessor: "value",
  Cell: ({ row: { original: { constraint_limit: constraintLimit } = {} }, cell: { value } }) => (
    <ConstraintValue hitValue={value} constraintLimit={constraintLimit} type={type} />
  )
});

export default constraintHitValue;
