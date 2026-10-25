import { Model } from "./model";

export interface DashboardMember {
  discord_id: string;
  display_name: string;
  username: string;
  avatar_url: string;
  bot: boolean;
}

export interface VoiceMember extends DashboardMember {
  muted: boolean;
  deafened: boolean;
  streaming: boolean;
  video: boolean;
}

export interface LeaderboardMember extends DashboardMember {
  rank: number;
  in_guild: boolean;
  level: number;
  xp: number;
  xp_required: number;
  monthly_xp: number;
  progress: number;
}

export interface DashboardData {
  guild: { id: number; name: string; icon_url: string | null };
  voice_channels: {
    discord_id: string;
    name: string;
    kind: "voice" | "stage";
    category: string | null;
    members: VoiceMember[];
  }[];
  voice_member_count: number;
  active_voice_channel_count: number;
  monthly_top: LeaderboardMember[];
  level_top: LeaderboardMember[];
  updated_at: string;
}

export class Dashboard extends Model {
  static async forGuild(guildId: number): Promise<DashboardData> {
    const response = await this.send_request(
      "GET",
      `/api/sessions/guilds/${guildId}/dashboard`,
    );
    if (!response.ok) throw new Error(String(response.status));
    return response.json();
  }
}
