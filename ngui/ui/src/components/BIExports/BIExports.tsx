import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import BIExportsTable from "components/BIExportsTable";
import PageContentDescription from "components/PageContentDescription";
import PageContentWrapper from "components/PageContentWrapper";
import TableLoader from "components/TableLoader";
import { INTEGRATIONS } from "urls";

const BIExports = ({ biExports, isLoading = false }) => (
  <>
    <ActionBar
      data={{
        breadcrumbs: [
          <Link key={1} to={INTEGRATIONS} component={RouterLink}>
            <FormattedMessage id="integrations" />
          </Link>,
        ],
        title: {
          text: <FormattedMessage id="biExportTitle" />,
          dataTestId: "lbl_bi_exports",
        },
      }}
    />
    <PageContentWrapper>
      {isLoading ? <TableLoader /> : <BIExportsTable exports={biExports} />}
      <PageContentDescription
        position="bottom"
        alertProps={{
          messageId: "biExportsDescription",
        }}
      />
    </PageContentWrapper>
  </>
);

export default BIExports;
