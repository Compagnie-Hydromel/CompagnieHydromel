import React from "react";

interface ShowProfileProps {
  background?: string;
  avatar?: string;
  displayName?: string;
  username?: string;
  level?: number;
  badges?: string[];
  progress?: number;
  profile_picture_x?: number;
  profile_picture_y?: number;
  name_x?: number;
  name_y?: number;
  username_x?: number;
  username_y?: number;
  level_x?: number;
  level_y?: number;
  badge_x?: number;
  badge_y?: number;
  level_bar_x?: number;
  level_bar_y?: number;
  name_color?: string;
  bar_color?: string;
}

const ShowProfile: React.FC<ShowProfileProps> = ({
  background = "https://shkermit.ch/~ethann/compHydromel/wallpapers/default.png",
  avatar = "https://cdn.discordapp.com/embed/avatars/0.png",
  displayName = "DisplayName",
  username = "user#1234",
  level = 5,
  badges = [],
  progress = 50,
  profile_picture_x = 0,
  profile_picture_y = 0,
  name_x = 150,
  name_y = 20,
  username_x = 150,
  username_y = 65,
  level_x = 250,
  level_y = 220,
  badge_x = 150,
  badge_y = 90,
  level_bar_x = 0,
  level_bar_y = 254,
  name_color = "#0000FF",
  bar_color = "#ADFF2F",
}) => {
  return (
    <div
      id="profile-preview"
      className="relative h-[281px] w-[500px] overflow-hidden select-none"
      style={{ fontFamily: "Arial, sans-serif" }}
    >
      <img
        src={background}
        alt="Background"
        className="absolute h-[281px] w-[500px]"
      />
      <img
        src={avatar}
        alt="Profile"
        className="w-[128px] h-[128px] rounded-full absolute"
        style={{
          left: `${profile_picture_x}px`,
          top: `${profile_picture_y}px`,
        }}
      />
      <h2
        className="absolute whitespace-nowrap"
        style={{
          fontSize: `${Math.max(23, 40 - Math.floor(displayName.length / 2))}px`,
          left: `${name_x}px`,
          top: `${name_y}px`,
          color: name_color,
        }}
      >
        {displayName}
      </h2>
      <div className="overflow-hidden">
        {badges.map((badge, index) => (
          <img
            key={index}
            src={badge}
            alt={`Badge ${index + 1}`}
            className="w-[32px] h-[32px] absolute"
            style={{
              left: `${badge_x + index * 34}px`,
              top: `${badge_y}px`,
            }}
          />
        ))}
      </div>
      <p
        className="text-[20px] absolute"
        style={{
          left: `${username_x}px`,
          top: `${username_y}px`,
          color: name_color,
        }}
      >
        {username}
      </p>
      <p
        className="text-[30px] absolute"
        style={{ left: `${level_x}px`, top: `${level_y}px`, color: bar_color }}
      >
        {level}
      </p>
      <div
        className="rounded-full h-[25px] w-[500px] absolute"
        style={{ left: `${level_bar_x}px`, top: `${level_bar_y}px` }}
      >
        <div
          className="h-[25px] rounded-full"
          style={{
            width: `${Math.max(5, progress)}%`,
            backgroundColor: bar_color,
          }}
        />
      </div>
    </div>
  );
};

export default ShowProfile;
