import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getMlModelUrl } from "urls";

const model = ({ id, getName, getId, headerMessageId, headerDataTestId, defaultSort, enableSorting = true }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  id,
  accessorFn: getName,
  enableSorting,
  defaultSort,
  cell: ({ row: { original } }) => (
    <Link to={getMlModelUrl(getId(original))} component={RouterLink}>
      {getName(original)}
    </Link>
  )
});

export default model;
