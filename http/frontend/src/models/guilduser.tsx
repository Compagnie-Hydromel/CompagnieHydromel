import { Model } from "./model";

export class GuildUser extends Model {
  static endpoint = "guildsusers";

  static async current(guild_id: number): Promise<GuildUser | null> {
    const response = await this.send_request(
      "GET",
      `/api/sessions/guilds/${guild_id}/user`,
    );
    if (response.status === 200) {
      const data = await response.json();
      const instance = new GuildUser();

      instance.attributes = data;
      return instance;
    } else {
      return null;
    }
  }
}
