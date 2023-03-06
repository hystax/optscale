import React from "react";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import IconLabel from "components/IconLabel";
import PoolTypeIcon from "components/PoolTypeIcon";
import SlicedText from "components/SlicedText";
import { getPoolUrl, isPoolIdWithSubPools } from "urls";
import { formQueryString } from "utils/network";

const SLICED_POOL_NAME_LENGTH = 25;

const getUrl = (poolId, organizationId) => {
  // TODO: remove this after https://datatrendstech.atlassian.net/browse/OS-4157
  const poolIdWithoutSubPoolMark = isPoolIdWithSubPools(poolId) ? poolId.slice(0, poolId.length - 1) : poolId;
  const baseUrl = getPoolUrl(poolIdWithoutSubPoolMark);
  return organizationId ? `${baseUrl}?${formQueryString({ organizationId })}` : baseUrl;
};

const SlicedPoolName = ({ name }) => <SlicedText limit={SLICED_POOL_NAME_LENGTH} text={name} />;

const PoolLink = ({ id, name, dataTestId, organizationId }) => (
  <Link data-test-id={dataTestId} color="primary" to={getUrl(id, organizationId)} component={RouterLink}>
    {name}
  </Link>
);

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
  withSubpools = false
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
              organizationId
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

PoolLink.propTypes = {
  name: PropTypes.node.isRequired,
  id: PropTypes.string.isRequired,
  dataTestId: PropTypes.string,
  disableLink: PropTypes.bool,
  organizationId: PropTypes.string
};

const labelOrNameValidator = (props, propName, componentName) => {
  if (!props.label && !props.name) {
    return new Error(`${componentName}: component must have label or name`);
  }
  if (props.label && props.name) {
    return new Error(`${componentName}: label and name properties should not be applied together`);
  }
  if (props.name && !(typeof props.name === "string" || props.name instanceof String)) {
    return new Error(`${componentName}: name should be a string`);
  }
  return null;
};

PoolLabel.propTypes = {
  type: PropTypes.string,
  name: labelOrNameValidator,
  id: PropTypes.string,
  label: labelOrNameValidator,
  endAdornment: PropTypes.node,
  disableLink: PropTypes.bool,
  dataTestId: PropTypes.string,
  organizationId: PropTypes.string,
  iconProps: PropTypes.object,
  withSubpools: PropTypes.bool
};

export default PoolLabel;
