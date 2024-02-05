import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import PoolLabel from "components/PoolLabel";
import TextWithDataTestId from "components/TextWithDataTestId";

const poolOwner = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_assign">
      <FormattedMessage id="assignTo" />
    </TextWithDataTestId>
  ),
  accessorKey: "pool/owner",
  cell: ({ row: { original } }) => (
    <CaptionedCell caption={original.owner_name}>
      <PoolLabel id={original.pool_id} name={original.pool_name} type={original.pool_purpose} />
    </CaptionedCell>
  )
});

export default poolOwner;
