import { Model } from "./model";
import type { ProfileLayout } from "./profile";

export interface AdminWallpaper {
  id: number;
  name: string;
  url: string;
  price: number;
  level: number;
}

export interface AdminData {
  guild_name: string;
  default_layout: ProfileLayout;
  default_wallpaper: string;
  layouts: ProfileLayout[];
  wallpapers: AdminWallpaper[];
}

export interface AdminMember {
  discord_id: string;
  display_name: string;
  username: string;
  avatar_url: string;
  bot: boolean;
  smartpoint: number;
  level: number;
  xp: number;
  xp_required: number;
}

export interface MembersPage {
  members: AdminMember[];
  total: number;
  page: number;
  page_size: number;
}

export class GuildAdmin extends Model {
  static async uploadWallpaper(
    guildId: number,
    form: FormData,
  ): Promise<AdminWallpaper> {
    const response = await fetch(
      `/api/sessions/guilds/${guildId}/admin/wallpapers`,
      {
        method: "POST",
        credentials: "include",
        body: form,
      },
    );
    if (!response.ok) throw new Error(String(response.status));
    return response.json();
  }

  static async request<T>(
    guildId: number,
    suffix = "",
    body?: unknown,
    method?: "GET" | "POST" | "PATCH",
  ): Promise<T> {
    const response = await this.send_request(
      method ?? (body ? "POST" : "GET"),
      `/api/sessions/guilds/${guildId}/admin${suffix}`,
      body,
    );
    if (!response.ok) throw new Error(String(response.status));
    return response.json();
  }
}
