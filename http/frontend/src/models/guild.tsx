import { Model } from "./model";

export class Guild extends Model {
  static endpoint = "guilds";

  static async myGuilds(): Promise<Guild[]> {
    const response = await Guild.send_request("GET", `/api/sessions/guilds`);
    if (response.status === 200) {
      const data = await response.json();
      const guilds: Guild[] = [];
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      data.forEach((guildData: any) => {
        const guild = new Guild();
        guild.attributes = guildData;
        guilds.push(guild);
      });
      return guilds;
    } else {
      return [];
    }
  }

  static async currentlySelectedGuild(): Promise<Guild | null> {
    const guilds = await this.myGuilds();
    const selectedGuildId = parseInt(
      localStorage.getItem("selectedGuild") ?? guilds[0]?.get("id") ?? "0",
    );
    return guilds.find((guild) => guild.get("id") === selectedGuildId) || null;
  }
}
