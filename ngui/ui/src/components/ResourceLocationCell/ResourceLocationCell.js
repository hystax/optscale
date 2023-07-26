import React from "react";
import PropTypes from "prop-types";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import { useApiData } from "hooks/useApiData";
import { DATA_SOURCE_TYPES } from "utils/constants";

const ResourceLocationCell = ({ dataSource, caption }) => {
  const {
    apiData: { cloudAccounts: dataSources = [] }
  } = useApiData(GET_DATA_SOURCES);

  return (
    <CaptionedCell caption={caption}>
      <CloudLabel
        disableLink={!dataSources.find(({ id }) => id === dataSource.id)}
        id={dataSource.id}
        name={dataSource.name}
        type={dataSource.type}
      />
    </CaptionedCell>
  );
};

ResourceLocationCell.propTypes = {
  dataSource: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    type: PropTypes.oneOf(DATA_SOURCE_TYPES)
  }).isRequired,
  caption: PropTypes.any
};

export default ResourceLocationCell;
