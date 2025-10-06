import React, { useState } from 'react';
import { Guild } from '../models/guild';

interface GuildSelectionProps {
    guilds: Guild[];
    onSelect: (guild: Guild) => void;
    defaultGuild?: Guild;
}

const GuildSelection: React.FC<GuildSelectionProps> = ({ guilds, onSelect, defaultGuild }) => {
    const [selectedGuild, setSelectedGuild] = useState<string | null>(defaultGuild ? defaultGuild.get("id") : null);

    const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const guildId = event.target.value;
        setSelectedGuild(guildId);
        const guild = guilds.find((g) => g.get("id") === guildId);
        if (guild) {
            onSelect(guild);
        }
    };

    return (
        <div>
            <select id="guild-select" value={selectedGuild || ''} onChange={handleChange}>
                <option value="" disabled>
                    -- Choose a Guild --
                </option>
                {guilds.map((guild) => (
                    <option key={guild.get("id")} value={guild.get("id")}>
                        {guild.get("name")}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default GuildSelection;