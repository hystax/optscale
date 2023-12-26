import { Fragment } from "react";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { makeStyles } from "tss-react/mui";
import CloudLabel from "components/CloudLabel";
import CopyText from "components/CopyText";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import MlRunsetTagForCreatedResourcesChip from "components/MlRunsetTagForCreatedResourcesChip";
import SummaryList from "components/SummaryList";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { intl } from "translations/react-intl-config";
import { getMlModelDetailsUrl } from "urls";
import { isEmpty as isEmptyArray, isLastItem } from "utils/arrays";
import { SPACING_1 } from "utils/layouts";
import { isEmpty as isEmptyObject } from "utils/objects";

const useStyles = makeStyles()(() => ({
  keyValueListItems: {
    display: "flex",
    flexWrap: "wrap"
  },
  tags: {
    rowGap: 2
  }
}));

const Details = ({
  dataSources,
  regions,
  instanceTypes,
  models,
  maximumRunsetBudget,
  resourceNamePrefix,
  tags,
  hyperparameters,
  isLoading
}) => {
  const { isDemo } = useOrganizationInfo();

  const { classes, cx } = useStyles();

  return (
    <Grid container spacing={SPACING_1}>
      <Grid item xs={12} sm={6} lg={4}>
        <SummaryList
          titleMessage={<FormattedMessage id="details" />}
          items={
            <>
              <KeyValueLabel
                messageId="tasks"
                isBoldValue
                value={
                  isEmptyArray(models) ? null : (
                    <div className={classes.keyValueListItems}>
                      {models.map(({ id, name, deleted = false }, index, array) => (
                        <Fragment key={id}>
                          {deleted ? (
                            name
                          ) : (
                            <Link key={id} to={getMlModelDetailsUrl(id)} component={RouterLink}>
                              {name}
                            </Link>
                          )}
                          {index < array.length - 1 ? <>&#44;&nbsp;</> : null}
                        </Fragment>
                      ))}
                    </div>
                  )
                }
              />
              <KeyValueLabel
                messageId="dataSources"
                value={
                  isEmptyArray(dataSources) ? null : (
                    <div className={classes.keyValueListItems}>
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
                    </div>
                  )
                }
              />
              <KeyValueLabel
                messageId="regions"
                value={
                  isEmptyArray(regions) ? null : (
                    <div className={classes.keyValueListItems}>
                      {regions.map(({ name: regionName, type: dataSourceType }, index, array) => (
                        <Fragment key={regionName}>
                          <CloudLabel id={regionName} name={regionName} type={dataSourceType} disableLink />
                          {isLastItem(index, array.length) ? null : <>&#44;&nbsp;</>}
                        </Fragment>
                      ))}
                    </div>
                  )
                }
              />
              <KeyValueLabel
                messageId="instanceTypes"
                value={
                  isEmptyArray(instanceTypes) ? null : (
                    <div className={classes.keyValueListItems}>
                      {instanceTypes.map(({ name: instanceTypeName, type: dataSourceType }, index, array) => (
                        <Fragment key={instanceTypeName}>
                          <CloudLabel id={instanceTypeName} name={instanceTypeName} type={dataSourceType} disableLink />
                          {isLastItem(index, array.length) ? null : <>&#44;&nbsp;</>}
                        </Fragment>
                      ))}
                    </div>
                  )
                }
              />
              <KeyValueLabel
                messageId="maximumRunsetBudget"
                value={maximumRunsetBudget === undefined ? null : <FormattedMoney value={maximumRunsetBudget} />}
              />
              <KeyValueLabel messageId="resourceNamePrefix" value={resourceNamePrefix} />
              <KeyValueLabel
                isBoldValue={false}
                messageId="tagForCreatedResources"
                value={
                  isEmptyObject(tags) ? null : (
                    <div className={cx(classes.keyValueListItems, classes.tags)}>
                      {Object.entries(tags).map(([tagKey, tagValue], index, array) => (
                        <Fragment key={tagKey}>
                          <MlRunsetTagForCreatedResourcesChip tagKey={tagKey} tagValue={tagValue} />
                          {isLastItem(index, array.length) ? null : <>&nbsp;</>}
                        </Fragment>
                      ))}
                    </div>
                  )
                }
              />
            </>
          }
          isLoading={isLoading}
        />
      </Grid>
      <Grid item xs={12} sm={6} lg={4}>
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
                <div key={hyperparameterName} style={{ display: "flex" }}>
                  <KeyValueLabel text={hyperparameterName} value={<code>{hyperparameterEnvironmentVariable}</code>} />
                  <CopyText text={hyperparameterEnvironmentVariable} />
                </div>
              ))
            )
          }
        />
      </Grid>
    </Grid>
  );
};

export default Details;
