import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { superError, superRequest } from "../../../models/superadmin";
import type { SuperUser } from "../../../models/superadmin";

export default function SuperadminUsers() {
  const { t } = useTranslation();
  const [result, setResult] = useState<{
    users: SuperUser[];
    total: number;
  } | null>(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");
    const timer = window.setTimeout(() => {
      superRequest<{ users: SuperUser[]; total: number }>(
        `/users?${new URLSearchParams({ search, page: String(page) })}`,
      )
        .then((data) => {
          if (!cancelled) setResult(data);
        })
        .catch((reason) => {
          if (!cancelled) setError(superError(reason));
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, 250);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [search, page]);
  return (
    <section className="admin-panel members-panel">
      <div className="admin-section-title">
        <h2>{t("superadmin.users.title")}</h2>
        <span className="admin-count">{result?.total ?? "—"}</span>
      </div>
      <label className="members-search">
        <input
          type="search"
          maxLength={100}
          value={search}
          onChange={(event) => {
            setSearch(event.target.value);
            setPage(1);
          }}
          placeholder={t("superadmin.users.search")}
          aria-label={t("superadmin.users.search")}
        />
      </label>
      {error ? (
        <p role="alert" className="admin-notice error">
          {t(error)}
        </p>
      ) : loading ? (
        <p role="status">{t("admin.loading")}</p>
      ) : (
        <>
          <div className="members-table-scroll">
            <table className="members-table">
              <thead>
                <tr>
                  <th>{t("admin.members.member")}</th>
                  <th>{t("superadmin.users.status")}</th>
                  <th>{t("admin.members.actions")}</th>
                </tr>
              </thead>
              <tbody>
                {result?.users.map((user) => (
                  <tr key={user.id}>
                    <td>
                      <div className="member-identity">
                        <img src={user.avatar_url} alt="" />
                        <div>
                          <strong>{user.display_name}</strong>
                          <span>
                            {user.username ? `@${user.username}` : "—"}
                          </span>
                          <small>{user.discord_id}</small>
                        </div>
                      </div>
                    </td>
                    <td>
                      {user.is_superadmin
                        ? "♛ Super admin"
                        : t("superadmin.users.member")}
                    </td>
                    <td>
                      <Link
                        className="admin-text-button"
                        to={`/dashboard/superadmin/users/${user.id}`}
                      >
                        {t("superadmin.users.details")} ↗
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {result?.users.length === 0 && (
              <p className="admin-empty">{t("superadmin.users.empty")}</p>
            )}
          </div>
          <div className="members-pagination">
            <button
              className="admin-button secondary"
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
            >
              {t("admin.members.previous")}
            </button>
            <span>
              {t("admin.members.page", {
                page,
                total: Math.max(1, Math.ceil((result?.total ?? 0) / 20)),
              })}
            </span>
            <button
              className="admin-button secondary"
              disabled={page * 20 >= (result?.total ?? 0)}
              onClick={() => setPage(page + 1)}
            >
              {t("admin.members.next")}
            </button>
          </div>
        </>
      )}
    </section>
  );
}
