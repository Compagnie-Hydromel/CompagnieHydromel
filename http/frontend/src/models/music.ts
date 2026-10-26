import { Model } from "./model";

export interface Track {
  title: string;
  uri: string;
  author: string;
  length: number;
  source: string;
}

export interface MusicState {
  connected: boolean;
  paused: boolean;
  channel_id: string | null;
  channel_name: string | null;
  current: Track | null;
  queue: Track[];
  has_previous: boolean;
  error: string | null;
  radios: { id: string; name: string }[];
}

export class Music extends Model {
  static async request(
    guildId: number,
    command?: { action: string; query?: string; source?: string },
  ): Promise<MusicState> {
    const response = await this.send_request(
      command ? "POST" : "GET",
      `/api/sessions/guilds/${guildId}/music`,
      command,
    );
    const data = await response.json();
    if (!response.ok)
      throw new Error(
        typeof data.detail === "string"
          ? data.detail
          : "Commande musicale refusée.",
      );
    return data;
  }
}
