import React, { useState } from 'react';
import { Guild } from '../models/guild';

interface GuildSelectionProps {
    guilds: Guild[];
    onSelect: (guild: Guild) => void;
}

const GuildSelection: React.FC<GuildSelectionProps> = ({ guilds, onSelect }) => {
    const [selectedGuild, setSelectedGuild] = useState<string | null>(null);

    const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const guildId = event.target.value;
        setSelectedGuild(guildId);
        const guild = guilds.find((g) => g.get("id") === guildId);
        if (guild) {
            onSelect(guild);
        }
    };

    React.useEffect(() => {
        const storedGuildId = localStorage.getItem('selectedGuild');
        if (guilds.length === 0) {
            setSelectedGuild(null);
            return;
        }
        if (storedGuildId) {
            setSelectedGuild(storedGuildId);
            const guild = guilds.find((g) => g.get("id") === storedGuildId);
            if (guild) {
            onSelect(guild);
            }
        } else {
            const firstGuild = guilds[0];
            if (firstGuild) {
            setSelectedGuild(firstGuild.get("id"));
            onSelect(firstGuild);
            }
        }
    }, [guilds, onSelect]);

    return (
        <div className='flex flex-row items-center'>
            {selectedGuild && (
                <img
                    src={guilds.find((g) => g.get("id") == selectedGuild)?.get("icon_url") || ''}
                    alt="Guild Icon"
                    style={{ width: '50px', height: '50px', marginTop: '10px' }}
                />
            )}
            <select id="guild-select" value={selectedGuild || ''} onChange={handleChange} className="ml-4 p-2 w-full rounded">
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