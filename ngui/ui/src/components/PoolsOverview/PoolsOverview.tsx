import AssignmentOutlinedIcon from "@mui/icons-material/AssignmentOutlined";
import Grid from "@mui/material/Grid";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import PoolsTable from "components/PoolsTable";
import PoolTypeIcon from "components/PoolTypeIcon";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ASSIGNMENT_RULES } from "urls";
import { POOL_TYPE_BUSINESS_UNIT } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import Summary from "./Summary";

const PoolsOverview = ({ data, isLoading, isDataReady, isGetPoolAllowedActionsLoading }) => {
  const { name } = useOrganizationInfo();
  const actionBarDefinition = {
    title: {
      text: name,
      logo: {
        icon: <PoolTypeIcon fontSize="medium" type={POOL_TYPE_BUSINESS_UNIT} hasRightMargin dataTestId="img_type" />
      },
      dataTestId: "lbl_pool_name"
    },
    items: [
      {
        key: "configureAssignmentRules",
        icon: <AssignmentOutlinedIcon fontSize="small" />,
        messageId: "configureAssignmentRules",
        link: ASSIGNMENT_RULES,
        type: "button",
        dataTestId: "btn_configure_assignment_rules"
      }
    ]
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container spacing={SPACING_2}>
          <Grid item>
            <Summary data={data} isLoading={isLoading} />
          </Grid>
          <Grid item xs={12}>
            <PoolsTable
              rootPool={data}
              isLoadingProps={{ isGetPoolLoading: isLoading, isGetPoolDataReady: isDataReady, isGetPoolAllowedActionsLoading }}
            />
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

export default PoolsOverview;
