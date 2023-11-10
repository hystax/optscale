import { useMemo } from "react";
import PlayCircleOutlineIcon from "@mui/icons-material/PlayCircleOutline";
import { CreateS3DuplicateFinderCheckModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { useInScopeOfPageMockup } from "hooks/useInScopeOfPageMockup";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import buckets from "./columns/buckets";
import duplicates from "./columns/duplicates";
import progress from "./columns/progress";
import savings from "./columns/savings";

const S3DuplicateFinderChecksTable = ({ geminis, isLoading }) => {
  const openSideModal = useOpenSideModal();
  const inScopeOfPageMockup = useInScopeOfPageMockup();

  const data = useMemo(
    () =>
      geminis.map((gemini) => ({
        ...gemini,
        bucketsString: gemini.filters.buckets.map(({ name }) => name).join("")
      })),
    [geminis]
  );

  const columns = useMemo(() => [progress(), buckets(), duplicates(), savings()], []);

  return isLoading ? (
    <TableLoader showHeader />
  ) : (
    <>
      <Table
        data={data}
        columns={columns}
        withSearch
        actionBar={{
          show: true,
          definition: {
            items: [
              {
                key: "add",
                icon: <PlayCircleOutlineIcon fontSize="small" />,
                messageId: "runCheck",
                type: "button",
                variant: "contained",
                color: "success",
                action: () => openSideModal(CreateS3DuplicateFinderCheckModal),
                dataTestId: "btn_new_check",
                requiredActions: ["EDIT_PARTNER"],
                disabled: inScopeOfPageMockup
              }
            ]
          }
        }}
        dataTestIds={{
          searchInput: "input_search",
          searchButton: "btn_search",
          deleteSearchButton: "btn_delete_search"
        }}
        localization={{ emptyMessageId: "noDuplicateChecks" }}
        pageSize={50}
      />
    </>
  );
};

export default S3DuplicateFinderChecksTable;
