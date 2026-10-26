import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { superError, superRequest } from "../../../models/superadmin";

export default function SuperadminLayout() {
  const { t } = useTranslation();
  const [access, setAccess] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let cancelled = false;
    superRequest("/users?page=1")
      .then(() => {
        if (!cancelled) setAccess(true);
      })
      .catch((reason) => {
        if (!cancelled) setError(superError(reason));
      });
    return () => {
      cancelled = true;
    };
  }, []);
  return (
    <div className="admin-shell">
      <header className="admin-heading">
        <div>
          <p className="admin-eyebrow">{t("superadmin.users.eyebrow")}</p>
          <h1>{t("superadmin.title")}</h1>
          <p className="admin-subtitle">{t("superadmin.users.subtitle")}</p>
        </div>
        <span className="admin-access-badge">♛ Super admin</span>
      </header>
      <nav className="admin-tabs" aria-label={t("superadmin.title")}>
        <NavLink
          to="/dashboard/superadmin/users"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          ♙ {t("superadmin.users.title")}
        </NavLink>
        <NavLink
          to="/dashboard/superadmin/badges"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          ✦ {t("superadmin.badges.title")}
        </NavLink>
        <NavLink
          to="/dashboard/superadmin/radios"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          ♬ Radios
        </NavLink>
      </nav>
      {error ? (
        <p role="alert" className="admin-panel admin-notice error">
          {t(error)}
        </p>
      ) : access ? (
        <Outlet />
      ) : (
        <p role="status" className="admin-panel">
          {t("admin.loading")}
        </p>
      )}
    </div>
  );
}
