import React, { useEffect, useState } from "react";
import { Guild } from "../models/guild";

interface GuildSelectionProps {
  guilds: Guild[];
  onSelect?: (guild: Guild) => void;
  defaultSelectedGuild?: Guild;
}

const GuildSelection: React.FC<GuildSelectionProps> = ({
  guilds,
  onSelect = () => {},
  defaultSelectedGuild,
}) => {
  const [selectedGuild, setSelectedGuild] = useState<string | null>(null);

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const guildId = event.target.value;
    setSelectedGuild(guildId);
    const guild = guilds.find((g) => g.get("id") === guildId);
    if (guild) {
      onSelect(guild);
    }
  };

  useEffect(() => {
    if (guilds.length === 0) {
      setSelectedGuild(null);
      return;
    }
    if (defaultSelectedGuild) {
      setSelectedGuild(defaultSelectedGuild.get("id"));
      onSelect(defaultSelectedGuild);
    } else {
      const firstGuild = guilds[0];
      if (firstGuild) {
        setSelectedGuild(firstGuild.get("id"));
        onSelect(firstGuild);
      }
    }
  }, [defaultSelectedGuild, guilds, onSelect]);

  return (
    <div className="flex flex-row items-center">
      <select
        id="guild-select"
        value={selectedGuild || ""}
        onChange={handleChange}
        className="p-2 rounded"
        style={{
          appearance: "none",
          paddingLeft: "50px",
          backgroundPosition: "left center",
          backgroundSize: "40px 40px",
          backgroundRepeat: "no-repeat",
          backgroundImage: selectedGuild
            ? `url(${guilds.find((g) => g.get("id") === selectedGuild)?.get("icon_url")})`
            : "none",
        }}
      >
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
