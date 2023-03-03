import React from "react";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import PoolLabel from "components/PoolLabel";
import TextWithDataTestId from "components/TextWithDataTestId";

const poolAndOwner = ({ headerDataTestId }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="pool/owner" />
    </TextWithDataTestId>
  ),
  id: "pool/owner",
  style: {
    whiteSpace: "nowrap"
  },
  cell: ({
    row: { original: { pool: { id: poolId, name: poolName, purpose: poolPurpose } = {}, owner: { name: ownerName } = {} } } = {}
  }) => (
    <CaptionedCell caption={ownerName}>
      <PoolLabel id={poolId} name={poolName} type={poolPurpose} />
    </CaptionedCell>
  )
});

export default poolAndOwner;
