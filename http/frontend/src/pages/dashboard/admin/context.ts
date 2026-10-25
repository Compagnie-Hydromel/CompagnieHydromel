import { createContext, useContext } from "react";
import type { Dispatch, SetStateAction } from "react";
import type { AdminData } from "../../../models/guild-admin";

interface AdminContextValue {
  guildId: number;
  data: AdminData;
  setData: Dispatch<SetStateAction<AdminData | null>>;
}

export const AdminContext = createContext<AdminContextValue | null>(null);

export function useGuildAdmin() {
  const context = useContext(AdminContext);
  if (!context) throw new Error("Missing admin context");
  return context;
}
