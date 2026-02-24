import { FormattedMessage } from "react-intl";
import CellCaption from "components/CellCaption";
import PoolLabel from "components/PoolLabel";
import TextWithDataTestId from "components/TextWithDataTestId";

const resourcePoolOwner = ({
  headerDataTestId = "lbl_pool_owner",
  id,
  accessorKey,
  accessorFn,
  columnSelector,
  getOwner,
  getPool,
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
    whiteSpace: "nowrap",
  },
  cell: ({ row: { original, id: rowId } }) => {
    const owner = getOwner(original);
    const pool = getPool(original);

    if (!pool && !owner) {
      return null;
    }

    const poolLabel = pool ? (
      <PoolLabel dataTestId={`resource_pool_${rowId}`} id={pool.id} name={pool.name} type={pool.purpose} />
    ) : null;

    const caption = owner ? owner.name : "";

    if (caption) {
      return (
        <>
          {poolLabel}
          <CellCaption text={caption} typographyProps={{ display: "block" }} />
        </>
      );
    }

    return poolLabel;
  },
});

export default resourcePoolOwner;
