import ListAltOutlinedIcon from "@mui/icons-material/ListAltOutlined";
import { FormattedMessage } from "react-intl";
import IconButton from "components/IconButton";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getConstraintHitResourcesLink } from "utils/organizationConstraints/getConstraintHitResourcesLink";

const constraintHitActions = ({ navigate, constraint }) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_actions">
      <FormattedMessage id="actions" />
    </TextWithDataTestId>
  ),
  enableSorting: false,
  id: "actions",
  cell: ({
    row: {
      original: { created_at: createdAt },
      index
    }
  }) => (
    <IconButton
      dataTestId={`actions_column_link_${index}`}
      icon={<ListAltOutlinedIcon />}
      onClick={() => {
        const link = getConstraintHitResourcesLink(createdAt, constraint);
        navigate(link);
      }}
      tooltip={{
        show: true,
        value: <FormattedMessage id="showResources" />
      }}
    />
  )
});

export default constraintHitActions;
