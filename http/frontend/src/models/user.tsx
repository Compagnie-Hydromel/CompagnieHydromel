export class User {
    id: number;
    discord_id: string;
    is_superadmin: boolean;

    constructor(id: number, discord_id: string, is_superadmin: boolean) {
        this.id = id;
        this.discord_id = discord_id;
        this.is_superadmin = is_superadmin;
    }

    static async current(): Promise<User | null> {
        const response = await fetch('/api/sessions', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
        });
        if (response.status === 200) {
            const data = await response.json();
            return new User(data.id, data.discord_id, data.is_superadmin);
        } else {
            return null;
        }
    }

    static async logout(): Promise<void> {
        await fetch('/api/sessions', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
        });
    };
}