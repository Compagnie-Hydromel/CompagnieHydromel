import { Model } from "./model";
import { Guild } from "./guild";

export class User extends Model {
    static endpoint = 'users';
    static modfiable_attributes = ['is_superadmin'];

    static async current(): Promise<User | null> {
        const response = await this.send_request('GET', '/api/sessions');
        if (response.status === 200) {
            const data = await response.json();
            const instance =  new User();

            instance.attributes = data.user;
            return instance;
        } else {
            return null;
        }
    }

    static async logout(): Promise<void> {
        await this.send_request('DELETE', '/api/sessions');
    };

    async guilds(): Promise<Guild[]> {
        const response = await User.send_request('GET', `/api/users/${this.get((this.constructor as typeof User).primary_key)}/guilds`);
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
}