import React from "react";
import HeaderHelperCell from "components/HeaderHelperCell";

const biExportExportedDays = () => ({
  header: (
    <HeaderHelperCell
      titleMessageId="exportedDays"
      titleDataTestId="lbl_exported_days"
      helperMessageId="exportedDaysDescription"
    />
  ),
  accessorKey: "days",
  enableSorting: false
});

export default biExportExportedDays;
