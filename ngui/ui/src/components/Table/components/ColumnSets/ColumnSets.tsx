import CollectionsBookmarkIcon from "@mui/icons-material/CollectionsBookmark";
import IconButton from "components/IconButton";
import { ColumnSetsModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const ColumnSets = ({ tableContext }) => {
  const openSideModal = useOpenSideModal();

  return (
    <IconButton
      icon={<CollectionsBookmarkIcon />}
      onClick={() => {
        openSideModal(ColumnSetsModal, {
          tableContext
        });
      }}
    />
  );
};

export default ColumnSets;
