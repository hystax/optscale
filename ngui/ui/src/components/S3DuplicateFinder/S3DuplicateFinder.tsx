import SettingsIcon from "@mui/icons-material/Settings";
import { Link, Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import S3DuplicateFinderChecksTable from "components/S3DuplicateFinderChecksTable";
import { S3DuplicateFinderSettingsModal } from "components/SideModalManager/SideModals";
import TableLoader from "components/TableLoader";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { RECOMMENDATIONS } from "urls";
import { SPACING_2 } from "utils/layouts";

const S3DuplicateFinder = ({ geminis, isLoading = false }) => {
  const openSideModal = useOpenSideModal();

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={RECOMMENDATIONS} component={RouterLink}>
        <FormattedMessage id="recommendations" />
      </Link>
    ],
    title: {
      messageId: "s3DuplicateFinderTitle"
    },
    items: [
      {
        key: "settings",
        icon: <SettingsIcon fontSize="small" />,
        messageId: "settings",
        action: () => openSideModal(S3DuplicateFinderSettingsModal, { recommendationType: "type" }),
        type: "button",
        requiredActions: ["EDIT_PARTNER"]
      }
    ]
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <div>
            <Typography gutterBottom>
              <FormattedMessage id="s3DuplicatesDescription.intro" />
            </Typography>
            <Typography gutterBottom>
              <FormattedMessage id="s3DuplicatesDescription.buckets" />
            </Typography>
            <Typography gutterBottom>
              <FormattedMessage id="s3DuplicatesDescription.process" />
            </Typography>
            <Typography>
              <FormattedMessage id="s3DuplicatesDescription.ui" />
            </Typography>
          </div>
          <div>{isLoading ? <TableLoader showHeader /> : <S3DuplicateFinderChecksTable geminis={geminis} />}</div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default S3DuplicateFinder;
