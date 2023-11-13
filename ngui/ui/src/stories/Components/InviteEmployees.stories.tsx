import InviteEmployees from "components/InviteEmployees";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/InviteEmployees`
};

export const basic = () => <InviteEmployees isLoading={false} onSubmit={(data) => console.log(data)} />;
