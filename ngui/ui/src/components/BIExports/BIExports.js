import React from "react";
import { Link } from "@mui/material";
import { Stack } from "@mui/system";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import BIExportsTable from "components/BIExportsTable";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PageContentWrapper from "components/PageContentWrapper";
import TableLoader from "components/TableLoader";
import { INTEGRATIONS } from "urls";
import { SPACING_2 } from "utils/layouts";

const BIExports = ({ biExports, isLoading }) => (
  <>
    <ActionBar
      data={{
        breadcrumbs: [
          <Link key={1} to={INTEGRATIONS} component={RouterLink}>
            <FormattedMessage id="integrations" />
          </Link>
        ],
        title: {
          text: <FormattedMessage id="biExportTitle" />,
          dataTestId: "lbl_bi_exports"
        }
      }}
    />
    <PageContentWrapper>
      <Stack spacing={SPACING_2}>
        <div>{isLoading ? <TableLoader /> : <BIExportsTable exports={biExports} />}</div>
        <div>
          <InlineSeverityAlert messageId="biExportsDescription" />
        </div>
      </Stack>
    </PageContentWrapper>
  </>
);

BIExports.propTypes = {
  biExports: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default BIExports;
