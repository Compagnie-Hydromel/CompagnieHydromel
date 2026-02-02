import React from "react";
import { useEffect } from "react";
import { User } from "../models/user";
import GuildSelection from "../components/guild-selection";
import { useNavigate } from "react-router-dom";
import { Guild } from "../models/guild";
import { Images } from "../assets";
import { Profile } from "./profile";

interface MenuItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

export const Header: React.FC = () => {
  const items: MenuItem[] = [
    { label: "Dashboard", href: "/dashboard", icon: <></> },
    { label: "Profile", href: "/dashboard/profile", icon: <></> },
  ];
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = React.useState<User | null>(null);
  const [guilds, setGuilds] = React.useState<Guild[]>([]);

  useEffect(() => {
    const checkAuth = async () => {
      const user = await User.current();
      if (!user) {
        navigate("/");
      }
      setCurrentUser(user);
      setGuilds((await user?.guilds()) || []);
    };
    checkAuth();
  }, [navigate]);

  return (
    <header
      className="flex justify-between items-center text-black p-8 mx-8"
      style={{
        backgroundImage: "url(" + Images.MENU.MIDDLE + ")",
        backgroundSize: "contain",
        backgroundPosition: "center",
        backgroundRepeat: "repeat",
      }}
    >
      <img
        src={Images.MENU.LEFT}
        alt="Left Decoration"
        style={{
          height: "144px",
          width: "auto",
          position: "absolute",
          left: 0,
          top: 0,
        }}
      />
      <img
        src={Images.MENU.RIGHT}
        alt="Right Decoration"
        style={{
          height: "144px",
          width: "auto",
          position: "absolute",
          right: 0,
          top: 0,
        }}
      />
      <GuildSelection
        guilds={guilds}
        onSelect={(guild) => console.log(guild)}
      />
      <nav className="w-full">
        <ul className="flex flex-col md:flex-row gap-5">
          {items.map((item) => (
            <li key={item.label}>
              <a
                href={item.href}
                className="text-gold-300 hover:text-gold-900 flex items-center gap-2"
              >
                {item.icon}
                {item.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>
      <Profile currentUser={currentUser} />
    </header>
  );
};
