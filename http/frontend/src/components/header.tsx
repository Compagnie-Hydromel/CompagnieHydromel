import React from "react";
import { useEffect } from "react";
import { User } from "../models/user";
import GuildSelection from "../components/guild-selection";
import { useNavigate } from "react-router-dom";
import { Guild } from "../models/guild";
import { Images } from "../assets";
import { Profile } from "./profile";
import { GuildAdmin } from "../models/guild-admin";
import { useTranslation } from "react-i18next";

interface MenuItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

export const Header: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = React.useState<User | null>(null);
  const [guilds, setGuilds] = React.useState<Guild[]>([]);
  const [selectedGuild, setSelectedGuild] = React.useState<Guild | null>(null);
  const [canAdmin, setCanAdmin] = React.useState(false);
  const [guildRevision, setGuildRevision] = React.useState(0);
  const items: MenuItem[] = [
    { label: "Dashboard", href: "/dashboard", icon: <></> },
    { label: "Profile", href: "/dashboard/profile", icon: <></> },
    ...(canAdmin
      ? [
          {
            label: t("admin.title"),
            href: "/dashboard/admin/layouts",
            icon: <></>,
          },
        ]
      : []),
  ];
  const selectGuild = React.useCallback((guild: Guild) => {
    const id = String(guild.get("id"));
    if (localStorage.getItem("selectedGuild") !== id) {
      localStorage.setItem("selectedGuild", id);
      window.dispatchEvent(new Event("guild-changed"));
    }
  }, []);

  useEffect(() => {
    const changed = () => {
      setCanAdmin(false);
      setGuildRevision((value) => value + 1);
    };
    window.addEventListener("guild-changed", changed);
    return () => window.removeEventListener("guild-changed", changed);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      try {
        const guild = await Guild.currentlySelectedGuild();
        if (!guild) return;
        await GuildAdmin.request(guild.get("id"), "/access");
        if (!cancelled) setCanAdmin(true);
      } catch {
        if (!cancelled) setCanAdmin(false);
      }
    };
    void check();
    return () => {
      cancelled = true;
    };
  }, [guildRevision]);

  useEffect(() => {
    const checkAuth = async () => {
      const user = await User.current();
      if (!user) {
        navigate("/");
      }
      setCurrentUser(user);
      setGuilds((await Guild.myGuilds()) || []);
      const guild = await Guild.currentlySelectedGuild();
      setSelectedGuild(guild ?? null);
    };
    checkAuth();
  }, [navigate]);

  return (
    <header
      className="sticky top-0 z-50 flex justify-between items-center text-black p-8 mx-8"
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
        defaultSelectedGuild={selectedGuild ?? undefined}
        onSelect={selectGuild}
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
