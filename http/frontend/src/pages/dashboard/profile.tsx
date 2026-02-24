import React, { useState, useEffect } from "react";
import ShowProfile from "../../components/profile-editor/show";
import { GuildUser } from "../../models/guilduser";
import Loading from "../../components/loading";
import { Guild } from "../../models/guild";

const Profile: React.FC = () => {
  const [user, setUser] = useState<GuildUser | null>(null);

  useEffect(() => {
    Guild.currentlySelectedGuild()
      .then((guild) => guild && GuildUser.current(guild.get("id") ?? 0))
      .then((currentUser) => currentUser && setUser(currentUser));
  }, []);

  if (!user) {
    return <Loading />;
  }

  return (
    <div className="h-[90vh] items-center justify-center flex">
      <ShowProfile
        background={
          user.get("wallpaper")["url"] ??
          "https://shkermit.ch/~ethann/compHydromel/wallpapers/default.png"
        }
        avatar={
          user.get("avatar_url") ??
          "https://cdn.discordapp.com/embed/avatars/0.png"
        }
        displayName={user.get("display_name") || "Unknown User"}
        username={user.get("username") ?? "unknown"}
        level={user.get("level") ?? 0}
        badges={user.get("badges") ?? []}
        progress={(user.get("progress") ?? 0) * 100}
        name_color={"#" + (user.get("name_color") ?? "0000FF")}
        bar_color={"#" + (user.get("bar_color") ?? "ADFF2F")}
      />
    </div>
  );
};

export default Profile;
