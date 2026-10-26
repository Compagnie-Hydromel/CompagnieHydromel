import React from "react";
import { useEffect } from "react";
import { User } from "../models/user";
import GuildSelection from "../components/guild-selection";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
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
  const location = useLocation();
  const [menuOpen, setMenuOpen] = React.useState(false);
  useEffect(() => setMenuOpen(false), [location.pathname]);
  const [currentUser, setCurrentUser] = React.useState<User | null>(null);
  const [guilds, setGuilds] = React.useState<Guild[]>([]);
  const [selectedGuild, setSelectedGuild] = React.useState<Guild | null>(null);
  const [canAdmin, setCanAdmin] = React.useState(false);
  const [guildRevision, setGuildRevision] = React.useState(0);
  const items: MenuItem[] = [
    { label: "Dashboard", href: "/dashboard", icon: <></> },
    { label: "Profile", href: "/dashboard/profile", icon: <></> },
    ...(currentUser?.get("is_superadmin")
      ? [
          {
            label: t("superadmin.title"),
            href: "/dashboard/superadmin/users",
            icon: <></>,
          },
        ]
      : []),
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
      className="site-header sticky top-0 z-50 text-black"
      onKeyDown={(event) => {
        if (event.key === "Escape") setMenuOpen(false);
      }}
      style={
        {
          "--parchment-image": `url(${Images.MENU.MIDDLE})`,
        } as React.CSSProperties
      }
    >
      <img
        src={Images.MENU.LEFT}
        className="site-header-decoration site-header-decoration-left"
        alt=""
      />
      <img
        src={Images.MENU.RIGHT}
        className="site-header-decoration site-header-decoration-right"
        alt=""
      />
      <GuildSelection
        guilds={guilds}
        defaultSelectedGuild={selectedGuild ?? undefined}
        onSelect={selectGuild}
      />
      <button
        type="button"
        className="site-menu-toggle"
        aria-expanded={menuOpen}
        aria-controls="site-navigation"
        aria-label={t("generic.navigation")}
        onClick={() => setMenuOpen((open) => !open)}
      >
        <span aria-hidden="true">{menuOpen ? "✕" : "☰"}</span>
      </button>
      <nav
        id="site-navigation"
        className={`site-navigation${menuOpen ? " is-open" : ""}`}
        aria-label={t("generic.navigation")}
      >
        <ul>
          {items.map((item) => (
            <li key={item.label}>
              <NavLink
                to={item.href!}
                end={item.href === "/dashboard"}
                onClick={() => setMenuOpen(false)}
                className="text-gold-300 hover:text-gold-900 flex items-center gap-2"
              >
                {item.icon}
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <Profile currentUser={currentUser} />
    </header>
  );
};
