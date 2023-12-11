import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import PoolLabel from "components/PoolLabel";
import TextWithDataTestId from "components/TextWithDataTestId";

const resourcePoolOwner = ({
  headerDataTestId = "lbl_pool_owner",
  id,
  accessorKey,
  accessorFn,
  columnSelector,
  getOwner,
  getPool
}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="pool/owner" />
    </TextWithDataTestId>
  ),
  id,
  accessorKey,
  accessorFn,
  columnSelector,
  style: {
    whiteSpace: "nowrap"
  },
  cell: ({ row: { original, id: rowId } }) => {
    const owner = getOwner(original);
    const pool = getPool(original);

    return pool || owner ? (
      <CaptionedCell caption={owner ? owner.name : ""}>
        {pool && <PoolLabel dataTestId={`resource_pool_${rowId}`} id={pool.id} name={pool.name} type={pool.purpose} />}
      </CaptionedCell>
    ) : null;
  }
});

export default resourcePoolOwner;
