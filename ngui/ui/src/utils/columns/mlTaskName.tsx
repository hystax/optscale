import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getMlTaskDetailsUrl } from "urls";

const mlTaskName = ({ accessorKey = "name", enableSorting = true, enableHiding = true } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_task_name">
      <FormattedMessage id="name" />
    </TextWithDataTestId>
  ),
  accessorKey,
  enableHiding,
  enableSorting,
  cell: ({
    row: {
      original: { id }
    },
    cell
  }) => (
    <Link to={getMlTaskDetailsUrl(id)} component={RouterLink}>
      {cell.getValue()}
    </Link>
  )
});

export default mlTaskName;
