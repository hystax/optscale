import { Fragment } from "react";
import { Box } from "@mui/material";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CloudLabel from "components/CloudLabel";
import CopyText from "components/CopyText";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import MlRunsetTagForCreatedResourcesChip from "components/MlRunsetTagForCreatedResourcesChip";
import SummaryList from "components/SummaryList";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { intl } from "translations/react-intl-config";
import { getMlTaskDetailsUrl } from "urls";
import { isEmpty as isEmptyArray, isLastItem } from "utils/arrays";
import { isEmpty as isEmptyObject } from "utils/objects";

const Details = ({
  dataSources,
  regions,
  instanceTypes,
  tasks,
  maximumRunsetBudget,
  resourceNamePrefix,
  tags,
  hyperparameters,
  isLoading
}) => {
  const { isDemo } = useOrganizationInfo();

  return (
    <Box display="flex" flexWrap="wrap" rowGap={1} columnGap={16}>
      <Box>
        <SummaryList
          titleMessage={<FormattedMessage id="details" />}
          items={
            <>
              <KeyValueLabel
                keyMessageId="tasks"
                value={
                  isEmptyArray(tasks) ? null : (
                    <span>
                      {tasks.map(({ id, name, deleted = false }, index, array) => (
                        <Fragment key={id}>
                          {deleted ? (
                            name
                          ) : (
                            <Link key={id} to={getMlTaskDetailsUrl(id)} component={RouterLink}>
                              {name}
                            </Link>
                          )}
                          {index < array.length - 1 ? <>&#44;&nbsp;</> : null}
                        </Fragment>
                      ))}
                    </span>
                  )
                }
              />
              <KeyValueLabel
                keyMessageId="dataSources"
                value={
                  isEmptyArray(dataSources) ? null : (
                    <Box display="flex" flexWrap="wrap">
                      {dataSources.map(
                        ({ id: dataSourceId, name: dataSourceName, type: dataSourceType, deleted = false }, index, array) => (
                          <Fragment key={dataSourceId}>
                            <CloudLabel
                              id={dataSourceId}
                              name={dataSourceName}
                              type={dataSourceType}
                              disableLink={isDemo || deleted}
                            />
                            {isLastItem(index, array.length) ? null : <>&#44;&nbsp;</>}
                          </Fragment>
                        )
                      )}
                    </Box>
                  )
                }
              />
              <KeyValueLabel
                keyMessageId="regions"
                value={
                  isEmptyArray(regions) ? null : (
                    <Box display="flex" flexWrap="wrap">
                      {regions.map(({ name: regionName, type: dataSourceType }, index, array) => (
                        <Fragment key={regionName}>
                          <CloudLabel id={regionName} name={regionName} type={dataSourceType} disableLink />
                          {isLastItem(index, array.length) ? null : <>&#44;&nbsp;</>}
                        </Fragment>
                      ))}
                    </Box>
                  )
                }
              />
              <KeyValueLabel
                keyMessageId="instanceTypes"
                value={
                  isEmptyArray(instanceTypes) ? null : (
                    <Box display="flex" flexWrap="wrap">
                      {instanceTypes.map(({ name: instanceTypeName, type: dataSourceType }, index, array) => (
                        <Fragment key={instanceTypeName}>
                          <CloudLabel id={instanceTypeName} name={instanceTypeName} type={dataSourceType} disableLink />
                          {isLastItem(index, array.length) ? null : <>&#44;&nbsp;</>}
                        </Fragment>
                      ))}
                    </Box>
                  )
                }
              />
              <KeyValueLabel
                keyMessageId="maximumRunsetBudget"
                value={maximumRunsetBudget === undefined ? null : <FormattedMoney value={maximumRunsetBudget} />}
              />
              <KeyValueLabel keyMessageId="resourceNamePrefix" value={resourceNamePrefix} />
              <KeyValueLabel
                keyMessageId="tagForCreatedResources"
                value={
                  isEmptyObject(tags) ? null : (
                    <Box display="flex" flexWrap="wrap" rowGap={2}>
                      {Object.entries(tags).map(([tagKey, tagValue], index, array) => (
                        <Fragment key={tagKey}>
                          <MlRunsetTagForCreatedResourcesChip tagKey={tagKey} tagValue={tagValue} />
                          {isLastItem(index, array.length) ? null : <>&nbsp;</>}
                        </Fragment>
                      ))}
                    </Box>
                  )
                }
              />
            </>
          }
          isLoading={isLoading}
        />
      </Box>
      <Box>
        <SummaryList
          titleMessage={
            <>
              <FormattedMessage id="hyperparameters" />
              &nbsp;
              <Typography variant="caption">
                <FormattedMessage
                  id="(value)"
                  values={{
                    value: (
                      <FormattedMessage
                        variant="caption"
                        id="{key}:{value}"
                        values={{
                          key: intl.formatMessage({ id: "name" }).toLowerCase(),
                          value: intl.formatMessage({ id: "environmentVariable" }).toLowerCase()
                        }}
                      />
                    )
                  }}
                />
              </Typography>
            </>
          }
          isLoading={isLoading}
          items={
            isEmptyObject(hyperparameters) ? (
              <FormattedMessage id="noHyperparameters" />
            ) : (
              Object.entries(hyperparameters).map(([hyperparameterName, hyperparameterEnvironmentVariable]) => (
                <KeyValueLabel
                  key={hyperparameterName}
                  keyText={hyperparameterName}
                  value={
                    <CopyText
                      sx={{
                        fontWeight: "inherit"
                      }}
                      text={hyperparameterEnvironmentVariable}
                    >
                      {hyperparameterEnvironmentVariable}
                    </CopyText>
                  }
                />
              ))
            )
          }
        />
      </Box>
    </Box>
  );
};

export default Details;
