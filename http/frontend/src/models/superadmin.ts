export interface Badge {
  id: number;
  name: string;
  url: string;
}
export interface SuperUser {
  id: number;
  discord_id: string;
  display_name: string;
  username: string | null;
  avatar_url: string;
  is_superadmin: boolean;
}
export interface UserDetail extends SuperUser {
  badges: Badge[];
  guilds: {
    id: number;
    discord_id: string;
    name: string;
    icon_url: string | null;
    cached_member: boolean;
    level: number;
    xp: number;
    xp_required: number;
    monthly_xp: number;
    smartpoint: number;
    is_admin: boolean;
    has_accepted_rules: boolean;
  }[];
}

export async function superRequest<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const form = body instanceof FormData;
  const response = await fetch(`/api/superadmin${path}`, {
    method,
    credentials: "include",
    headers: body && !form ? { "Content-Type": "application/json" } : undefined,
    body: body ? (form ? (body as FormData) : JSON.stringify(body)) : undefined,
  });
  if (!response.ok) throw new Error(String(response.status));
  return response.json();
}

export function superError(reason: unknown) {
  return reason instanceof Error && ["401", "403"].includes(reason.message)
    ? "superadmin.badges.denied"
    : "superadmin.users.error";
}
