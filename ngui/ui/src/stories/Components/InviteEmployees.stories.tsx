import InviteEmployees from "components/InviteEmployees";

export default {
  component: InviteEmployees
};

export const basic = () => <InviteEmployees isLoading={false} onSubmit={(data) => console.log(data)} />;
