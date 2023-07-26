import React, { useState } from "react";
import Box from "@mui/material/Box";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import CopyTextField from "components/CopyTextField";
import QuestionMark from "components/QuestionMark";
import SubTitle from "components/SubTitle";
import TitleValue from "components/TitleValue";
import { formatUTC, getLastMonthRange, FORMAT_YYYY_MM_DD } from "utils/datetime";

const ShareSettings = ({ canEdit, currentLink, onChange, isLoading }) => {
  const intl = useIntl();

  const linkAvailable = currentLink !== "";

  const [switchPosition, setSwitchPosition] = useState(linkAvailable);
  const switchClickHandler = (value) => {
    setSwitchPosition(value);
    if (typeof onChange === "function") {
      onChange(value);
    }
  };

  const renderSwitch = () => (
    <FormControlLabel
      control={<Switch disabled={!canEdit} checked={switchPosition} onChange={(e) => switchClickHandler(e.target.checked)} />}
      label={
        <Box display="flex" alignItems="center">
          <Typography>
            <FormattedMessage id={linkAvailable ? "deleteLink" : "generateLink"} />
          </Typography>
          {!canEdit && <QuestionMark messageId="shareLinkBadPermissions" />}
        </Box>
      }
      labelPlacement="end"
    />
  );

  const renderWarning = () =>
    canEdit &&
    linkAvailable && (
      <Typography gutterBottom color="error">
        <FormattedMessage id="shareLinkRemoveTip" />
      </Typography>
    );

  const renderFormulas = () => {
    // current day example dates
    const lastMonthRange = getLastMonthRange(true);
    const firstDayOfLastMonth = formatUTC(lastMonthRange.start, FORMAT_YYYY_MM_DD);
    const lastDayOfLastMonth = formatUTC(lastMonthRange.end, FORMAT_YYYY_MM_DD);

    const linkPlaceholder = "<link>";

    const blockDefinition = [
      {
        blockHeader: "shareLinkGoogleExamplesHeader",
        formulas: [
          {
            header: "shareLinkGoogleAllTimeHeader",
            tip: "shareLinkGoogleAllTimeTip",
            formula: "shareLinkGoogleAllTimeFormula"
          },
          {
            header: "shareLinkGoogleDailyHeader",
            tip: "shareLinkGoogleDailyTip",
            formula: "shareLinkGoogleDailyFormula"
          },
          {
            header: "shareLinkGoogleSingleHeader",
            tip: "shareLinkGoogleSingleTip",
            formula: "shareLinkGoogleSingleFormula"
          }
        ]
      }
    ];

    return (
      <>
        <Box mb={2}>
          <Typography key="commonShareLinkDescription" gutterBottom>
            <FormattedMessage id="commonShareLinkDescription" />
          </Typography>
        </Box>
        {blockDefinition.map(({ blockHeader, formulas }) => (
          <div key={blockHeader}>
            <SubTitle gutterBottom>
              <FormattedMessage id={blockHeader} />
            </SubTitle>
            {formulas.map(({ header, tip, formula }) => (
              <Box key={`${header}${tip}${formula}`} mb={1}>
                <TitleValue>
                  <FormattedMessage id={header} />
                </TitleValue>
                <Typography>
                  <FormattedMessage id={tip} />
                </Typography>
                <CopyTextField
                  textToDisplay={intl.formatMessage(
                    { id: formula },
                    { value: currentLink || linkPlaceholder, lastDayOfLastMonth, firstDayOfLastMonth }
                  )}
                />
              </Box>
            ))}
          </div>
        ))}
      </>
    );
  };

  return (
    <ContentBackdropLoader isLoading={isLoading}>
      <Box display="flex" flexDirection="column" pl={2} pr={2} mb={2}>
        {linkAvailable && <CopyTextField textToDisplay={currentLink} />}
        {renderSwitch()}
        {renderWarning()}
        {renderFormulas()}
      </Box>
    </ContentBackdropLoader>
  );
};

ShareSettings.propTypes = {
  canEdit: PropTypes.bool,
  currentLink: PropTypes.string,
  onChange: PropTypes.func,
  isLoading: PropTypes.bool
};

export default ShareSettings;
