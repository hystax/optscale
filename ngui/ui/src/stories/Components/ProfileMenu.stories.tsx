import ProfileMenu from "components/ProfileMenu";

export default {
  component: ProfileMenu,
  argTypes: {
    email: { name: "Name", control: "text", defaultValue: "example@email.com" },
    name: { name: "Email", control: "text", defaultValue: "Some Name" }
  }
};

export const withKnobs = (args) => <ProfileMenu email={args.email} name={args.name} isLoading={false} />;
