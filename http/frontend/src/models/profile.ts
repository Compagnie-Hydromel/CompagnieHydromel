import { Model } from "./model";

export interface ProfileLayout {
  id: number | null;
  name: string;
  profile_picture_x: number;
  profile_picture_y: number;
  name_x: number;
  name_y: number;
  username_x: number;
  username_y: number;
  level_x: number;
  level_y: number;
  badge_x: number;
  badge_y: number;
  level_bar_x: number;
  level_bar_y: number;
}

export interface Wallpaper {
  id: number;
  name: string;
  url: string;
  price: number;
  level: number;
  owned: boolean;
}

export interface ProfileChanges {
  name_color: string;
  bar_color: string;
  wallpaper_id: number | null;
  layout_id: number | null;
}

export interface ProfileData {
  user: {
    avatar_url: string;
    display_name: string;
    username: string;
    level: number;
    badges: string[];
    progress: number;
    name_color: string;
    bar_color: string;
    smartpoint: number;
  };
  wallpaper_id: number | null;
  layout_id: number | null;
  default_wallpaper: string;
  default_layout: ProfileLayout;
  layouts: ProfileLayout[];
  wallpapers: Wallpaper[];
}

export class Profile extends Model {
  static async requestProfile(
    guildId: number,
    method = "GET",
    changes?: ProfileChanges,
    suffix = "",
  ): Promise<ProfileData> {
    const response = await this.send_request(
      method,
      `/api/sessions/guilds/${guildId}/profile${suffix}`,
      changes,
    );
    if (!response.ok) {
      throw new Error(String(response.status));
    }
    return response.json();
  }
}
