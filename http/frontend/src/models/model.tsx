/* eslint-disable @typescript-eslint/no-explicit-any */

export class Model {
    static primary_key = 'id';
    static api_base = '/api';
    static endpoint: string = '';
    attributes: Record<string, any> = {};
    modified_attributes: Record<string, any> = {};
    static modfiable_attributes: string[] = [];


    constructor(initialAttributes: Record<string, any> = {}) {
        this.attributes = {};
        this.modified_attributes = initialAttributes;
    }

    static async send_request(method: string, url: string, body?: unknown): Promise<Response> {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: body ? JSON.stringify(body) : undefined,
        });
        return response;
    }

    is_dirty(): boolean {
        return this.modified_attributes.length > 0;
    }

    static async find(id: string): Promise<any> {
        const url = `${this.api_base}/${this.endpoint}/${id}`;
        const response = await this.send_request('GET', url);
        if (response.ok) {
            const data = await response.json();
            const instance = new this();
            instance.attributes = data;
            instance.modified_attributes = {};
            return instance;
        } else {
            return null;
        }
    }

    static async all(): Promise<any[]> {
        const url = `${this.api_base}/${this.endpoint}`;
        const response = await this.send_request('GET', url);
        if (response.ok) {
            const data = await response.json();
            return data.map((item: any) => {
                const instance = new this();
                instance.attributes = item;
                instance.modified_attributes = {};
                return instance;
            });
        } else {
            return [];
        }
    }

    get(key: string): any {
        return this.modified_attributes[key] ?? this.attributes[key] ?? null;
    }

    set(key: string, value: any): void {
        if (!(this.constructor as typeof Model).modfiable_attributes.includes(key)) {
            throw new Error(`Attribute ${key} is not modifiable.`);
        }
        this.modified_attributes[key] = value;
    }

    async save(): Promise<Response> {
        if (!this.is_dirty()) {
            return Promise.resolve(new Response(null, { status: 204 }));
        }

        const url = `${(this.constructor as typeof Model).api_base}/${(this.constructor as typeof Model).endpoint}`;
        const body = this.modified_attributes;
        this.modified_attributes = {};
        const method = this.attributes[(this.constructor as typeof Model).primary_key] ? 'PATCH' : 'POST';
        return (this.constructor as typeof Model).send_request(method, url, body);
    }   
}