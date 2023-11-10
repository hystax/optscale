import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import PoolLabel from "components/PoolLabel";
import TextWithDataTestId from "components/TextWithDataTestId";

const poolOwner = ({ headerDataTestId, id }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="pool/owner" />
    </TextWithDataTestId>
  ),
  id,
  style: {
    whiteSpace: "nowrap"
  },
  cell: ({ row: { original } }) =>
    original.owner || original.pool ? (
      <CaptionedCell caption={original.owner?.name}>
        {original.pool.id && <PoolLabel id={original.pool.id} name={original.pool.name} type={original.pool.purpose} />}
      </CaptionedCell>
    ) : null
});

export default poolOwner;
