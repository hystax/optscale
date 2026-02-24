import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import IconLabel from "components/IconLabel";
import PoolTypeIcon from "components/PoolTypeIcon";
import SlicedText from "components/SlicedText";
import { useUpdateScope } from "hooks/useUpdateScope";
import { getPoolUrl, isPoolIdWithSubPools } from "urls";

const SLICED_POOL_NAME_LENGTH = 35;

const getUrl = (poolId: string) => {
  // TODO: remove this after https://datatrendstech.atlassian.net/browse/OS-4157
  const poolIdWithoutSubPoolMark = isPoolIdWithSubPools(poolId) ? poolId.slice(0, poolId.length - 1) : poolId;

  return getPoolUrl(poolIdWithoutSubPoolMark);
};

const SlicedPoolName = ({ name }) => <SlicedText limit={SLICED_POOL_NAME_LENGTH} text={name} />;

const PoolLink = ({ id, name, dataTestId, organizationId }) => {
  const updateScope = useUpdateScope();
  const navigate = useNavigate();

  return (
    <Link
      component="button"
      onClick={() => {
        const url = getUrl(id);
        if (organizationId) {
          updateScope({
            newScopeId: organizationId,
            redirectTo: url,
          });
        } else {
          navigate(url);
        }
      }}
      data-test-id={dataTestId}
    >
      {name}
    </Link>
  );
};

const renderLabel = ({ disableLink, name, id, dataTestId, organizationId }) => {
  const slicedName = <SlicedPoolName name={name} />;
  return disableLink ? (
    <span data-test-id={dataTestId}>{slicedName}</span>
  ) : (
    <PoolLink id={id} name={slicedName} dataTestId={dataTestId} organizationId={organizationId} />
  );
};

const PoolLabel = ({
  type,
  name,
  id,
  label,
  dataTestId,
  disableLink = false,
  organizationId,
  endAdornment = null,
  iconProps = {},
  withSubpools = false,
}) => (
  <>
    <IconLabel
      icon={<PoolTypeIcon type={type} hasRightMargin {...iconProps} />}
      label={
        <>
          {label ? (
            <span data-test-id={dataTestId}>{label}</span>
          ) : (
            renderLabel({
              disableLink,
              name,
              id,
              dataTestId,
              organizationId,
            })
          )}
          {withSubpools && (
            <>
              &nbsp;
              <FormattedMessage id="(withSubPools)" />
            </>
          )}
        </>
      }
    />
    {endAdornment}
  </>
);

export default PoolLabel;
