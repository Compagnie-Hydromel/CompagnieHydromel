import { Model } from "./model";

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
}