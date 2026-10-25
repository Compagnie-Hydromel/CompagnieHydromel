import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { Guild } from "../../../models/guild";
import { GuildAdmin } from "../../../models/guild-admin";
import type { AdminData } from "../../../models/guild-admin";
import { useTranslation } from "react-i18next";
import { AdminContext } from "./context";

export default function AdminLayout() {
  const { t } = useTranslation();
  const [data, setData] = useState<AdminData | null>(null);
  const [guildId, setGuildId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [revision, setRevision] = useState(0);
  const generation = useRef(0);
  const currentGeneration = generation.current;
  const location = useLocation();

  useEffect(() => {
    const changed = () => {
      generation.current += 1;
      setRevision((value) => value + 1);
    };
    window.addEventListener("guild-changed", changed);
    return () => window.removeEventListener("guild-changed", changed);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setData(null);
    setError("");
    const load = async () => {
      try {
        const guild = await Guild.currentlySelectedGuild();
        if (!guild) throw new Error("403");
        const id = Number(guild.get("id"));
        const result = await GuildAdmin.request<AdminData>(id);
        if (!cancelled) {
          setGuildId(id);
          setData(result);
        }
      } catch (failure) {
        if (!cancelled)
          setError(
            failure instanceof Error && ["401", "403"].includes(failure.message)
              ? "admin.denied"
              : "admin.loadError",
          );
      }
    };
    void load();
    return () => {
      cancelled = true;
      generation.current += 1;
    };
  }, [revision, location.pathname]);

  return (
    <section className="admin-shell">
      <div className="admin-heading">
        <div>
          <p className="admin-eyebrow">{t("admin.eyebrow")}</p>
          <h1>{t("admin.title")}</h1>
          <p className="admin-subtitle">
            {data?.guild_name ?? t("admin.subtitle")}
          </p>
        </div>
        <span className="admin-access-badge">♜ {t("admin.permission")}</span>
      </div>
      <nav className="admin-tabs" aria-label={t("admin.title")}>
        <NavLink
          to="/dashboard/admin/messages"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          ✉ {t("admin.messages.title")}
        </NavLink>
        <NavLink
          to="/dashboard/admin/banner"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          ▧ {t("admin.banner.title")}
        </NavLink>
        <NavLink
          to="/dashboard/admin/roles"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          ♜ {t("admin.roles.title")}
        </NavLink>
        <NavLink
          to="/dashboard/admin/members"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          ♙ {t("admin.members.title")}
        </NavLink>
        <NavLink
          to="/dashboard/admin/layouts"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          ▦ {t("admin.layouts")}
        </NavLink>
        <NavLink
          to="/dashboard/admin/wallpapers"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          ▧ {t("admin.wallpapers")}
        </NavLink>
      </nav>
      {error ? (
        <div role="alert" className="admin-panel admin-notice error">
          {t(error)}
        </div>
      ) : !data || guildId === null ? (
        <div role="status" className="admin-panel">
          {t("admin.loading")}
        </div>
      ) : (
        <AdminContext.Provider
          value={{
            guildId,
            data,
            setData: (update) => {
              if (generation.current === currentGeneration) setData(update);
            },
          }}
        >
          <Outlet key={`${guildId}-${revision}`} />
        </AdminContext.Provider>
      )}
    </section>
  );
}
