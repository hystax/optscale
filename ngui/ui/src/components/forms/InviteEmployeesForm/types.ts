import { INVITABLE_ROLE_PURPOSES, POOL_TYPES, SCOPE_TYPES } from "utils/constants";

type Pool = {
  id: string;
  name: string;
  parent_id: string | null;
  pool_purpose: keyof typeof POOL_TYPES;
};

export type PoolTreeNode = Pool & {
  level: number;
  children: PoolTreeNode[];
};

export type Invitation = {
  scope_id: string;
  scope_type: (typeof SCOPE_TYPES)[keyof typeof SCOPE_TYPES];
  purpose: string | null;
};

export type EmailInvitations = Record<string, Invitation[]>;

export type InviteEmployeesFormProps = {
  availablePools: Pool[];
  onSubmit: (invitations: EmailInvitations, successCallback: () => void) => void;
  onCancel: () => void;
  isLoadingProps?: {
    isCreateInvitationsLoading?: boolean;
    isGetAvailablePoolsLoading?: boolean;
  };
};

export type FormValues = {
  additionalRoles: { role: keyof typeof INVITABLE_ROLE_PURPOSES | ""; poolId: string }[];
};
