import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { superError, superRequest } from "../../../models/superadmin";
import type { Badge, UserDetail } from "../../../models/superadmin";

export default function SuperadminUserDetail() {
  const { t } = useTranslation();
  const { userId } = useParams();
  const [user, setUser] = useState<UserDetail | null>(null);
  const [badges, setBadges] = useState<Badge[]>([]);
  const [selected, setSelected] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);
  const submitting = useRef(false);
  const generation = useRef(0);
  useEffect(() => {
    let cancelled = false;
    setUser(null);
    setError("");
    setSaved(false);
    setSelected("");
    Promise.all([
      superRequest<UserDetail>(`/users/${userId}`),
      superRequest<Badge[]>("/badges"),
    ])
      .then(([data, catalog]) => {
        if (!cancelled) {
          setUser(data);
          setBadges(catalog);
        }
      })
      .catch((reason) => {
        if (!cancelled)
          setError(
            reason instanceof Error && reason.message === "404"
              ? "superadmin.badges.missingUser"
              : superError(reason),
          );
      });
    return () => {
      cancelled = true;
      generation.current += 1;
    };
  }, [userId]);

  const changeBadge = async (badgeId: number, assign: boolean) => {
    if (!user || submitting.current) return;
    const version = generation.current;
    submitting.current = true;
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      await superRequest(
        `/badges/${badgeId}/users/${user.id}`,
        assign ? "POST" : "DELETE",
      );
      const updated = await superRequest<UserDetail>(`/users/${user.id}`);
      if (version === generation.current) {
        setUser(updated);
        setSelected("");
        setSaved(true);
      }
    } catch (reason) {
      if (version === generation.current) setError(superError(reason));
    } finally {
      submitting.current = false;
      setBusy(false);
    }
  };

  return (
    <div className="admin-content">
      <Link className="admin-text-button" to="/dashboard/superadmin/users">
        ← {t("superadmin.users.back")}
      </Link>
      {error && (
        <p role="alert" className="admin-panel admin-notice error">
          {t(error)}
        </p>
      )}
      {!user ? (
        !error && (
          <p role="status" className="admin-panel">
            {t("admin.loading")}
          </p>
        )
      ) : (
        <>
          <section className="admin-panel">
            <div className="member-identity">
              <img src={user.avatar_url} alt="" />
              <div>
                <h2>{user.display_name}</h2>
                <span>{user.username ? `@${user.username}` : "—"}</span>
                <small>
                  Discord : {user.discord_id} · ID : {user.id}
                </small>
              </div>
              {user.is_superadmin && (
                <span className="admin-count">♛ Super admin</span>
              )}
            </div>
          </section>
          <section className="admin-panel admin-form">
            <div className="admin-section-title">
              <h2>{t("superadmin.badges.title")}</h2>
              <Link
                className="admin-text-button"
                to="/dashboard/superadmin/badges"
              >
                {t("superadmin.users.catalog")} ↗
              </Link>
            </div>
            <p className="admin-info">{t("superadmin.badges.global")}</p>
            {saved && (
              <p role="status" className="admin-notice success">
                {t("superadmin.badges.saved")}
              </p>
            )}
            <div className="badge-user-list">
              {user.badges.map((badge, index) => (
                <button
                  key={`${badge.id}-${index}`}
                  disabled={busy}
                  title={t("superadmin.badges.revoke", { name: badge.name })}
                  aria-label={t("superadmin.badges.revoke", {
                    name: badge.name,
                  })}
                  onClick={() => void changeBadge(badge.id, false)}
                >
                  <img src={badge.url} alt="" />
                  {badge.name} ×
                </button>
              ))}
              {user.badges.length === 0 && (
                <p className="admin-hint">{t("superadmin.users.noBadges")}</p>
              )}
            </div>
            <div className="wallpaper-edit-actions">
              <select
                aria-label={t("superadmin.badges.choose")}
                disabled={busy}
                value={selected}
                onChange={(event) => setSelected(event.target.value)}
              >
                <option value="">{t("superadmin.badges.choose")}</option>
                {badges
                  .filter(
                    (badge) =>
                      !user.badges.some((item) => item.id === badge.id),
                  )
                  .map((badge) => (
                    <option key={badge.id} value={badge.id}>
                      {badge.name}
                    </option>
                  ))}
              </select>
              <button
                className="admin-button primary"
                disabled={busy || !selected}
                onClick={() => void changeBadge(Number(selected), true)}
              >
                {t("superadmin.badges.assign")}
              </button>
            </div>
          </section>
          <section className="admin-content">
            <div className="admin-section-title">
              <h2>{t("superadmin.users.guilds")}</h2>
              <span className="admin-count">{user.guilds.length}</span>
            </div>
            <p className="admin-info">{t("superadmin.users.guildHelp")}</p>
            <div className="admin-card-grid">
              {user.guilds.length === 0 && (
                <p className="admin-panel admin-empty">
                  {t("superadmin.users.noGuilds")}
                </p>
              )}
              {user.guilds.map((guild) => (
                <article className="admin-panel role-rule-card" key={guild.id}>
                  <div className="member-identity">
                    {guild.icon_url && <img src={guild.icon_url} alt="" />}
                    <div>
                      <h3>{guild.name}</h3>
                      <small>{guild.discord_id}</small>
                    </div>
                  </div>
                  <span className="admin-count">
                    {t(
                      guild.cached_member
                        ? "superadmin.users.cachedMember"
                        : "superadmin.users.unknownMember",
                    )}
                  </span>
                  <dl className="superuser-stats">
                    <div>
                      <dt>{t("admin.members.level")}</dt>
                      <dd>{guild.level}</dd>
                    </div>
                    <div>
                      <dt>XP</dt>
                      <dd>
                        {guild.xp} / {guild.xp_required}
                      </dd>
                    </div>
                    <div>
                      <dt>{t("dashboard.monthlyXP")}</dt>
                      <dd>{guild.monthly_xp}</dd>
                    </div>
                    <div>
                      <dt>{t("admin.members.smartpoints")}</dt>
                      <dd>{guild.smartpoint}</dd>
                    </div>
                    <div>
                      <dt>{t("superadmin.users.adminFlag")}</dt>
                      <dd>
                        {t(
                          guild.is_admin
                            ? "superadmin.users.yes"
                            : "superadmin.users.no",
                        )}
                      </dd>
                    </div>
                    <div>
                      <dt>{t("superadmin.users.acceptedRules")}</dt>
                      <dd>
                        {t(
                          guild.has_accepted_rules
                            ? "superadmin.users.yes"
                            : "superadmin.users.no",
                        )}
                      </dd>
                    </div>
                  </dl>
                </article>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
