import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import CreateEnvironmentProperties from "components/CreateEnvironmentProperties";
import EnvironmentProperty from "components/EnvironmentProperty";
import SubTitle from "components/SubTitle";
import DownloadHistoryDropdownContainer from "containers/DonwloadHistoryDropdownContainer";
import { useIsAllowedToCUDEnvironmentProperties } from "hooks/useIsAllowedToCUDEnvironmentProperties";
import { useIsUpMediaQuery } from "hooks/useMediaQueries";
import { isEmpty as isEmptyObject } from "utils/objects";

const EnvironmentProperties = ({ environmentId, properties }) => {
  const isUpLg = useIsUpMediaQuery("lg");

  const isAllowedToCUDEnvironmentProperties = useIsAllowedToCUDEnvironmentProperties();

  return (
    <div
      style={{
        marginBottom: "1rem",
        width: isUpLg ? "50%" : "100%"
      }}
    >
      <div
        style={{
          alignItems: "center",
          display: "flex"
        }}
      >
        <SubTitle>
          <FormattedMessage id="environmentProperties" />
        </SubTitle>
        <DownloadHistoryDropdownContainer environmentId={environmentId} />
      </div>
      {isEmptyObject(properties) ? (
        <Typography gutterBottom>
          <FormattedMessage id="noProperties" />
        </Typography>
      ) : (
        Object.entries(properties).map(([propertyName, propertyValue], index, array) => (
          <div
            key={propertyName}
            style={{
              marginBottom: index === array.length - 1 ? 0 : "1rem"
            }}
          >
            <EnvironmentProperty
              environmentId={environmentId}
              propertyName={propertyName}
              propertyValue={propertyValue}
              existingProperties={properties}
            />
          </div>
        ))
      )}

      {isAllowedToCUDEnvironmentProperties && (
        <CreateEnvironmentProperties environmentId={environmentId} existingProperties={properties} />
      )}
    </div>
  );
};

export default EnvironmentProperties;
