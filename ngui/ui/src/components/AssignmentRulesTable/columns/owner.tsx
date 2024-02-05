import { text } from "utils/columns";

const owner = () =>
  text({
    headerMessageId: "owner",
    headerDataTestId: "lbl_owner",
    accessorKey: "owner_name"
  });

export default owner;
