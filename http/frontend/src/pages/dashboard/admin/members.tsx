import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { GuildAdmin } from "../../../models/guild-admin";
import type { AdminMember, MembersPage } from "../../../models/guild-admin";
import { useGuildAdmin } from "./context";

function MemberRow({
  member,
  guildId,
  onUpdate,
}: {
  member: AdminMember;
  guildId: number;
  onUpdate: (member: AdminMember) => void;
}) {
  const { t } = useTranslation();
  const [smartpoint, setSmartpoint] = useState(String(member.smartpoint));
  const [level, setLevel] = useState(String(member.level));
  const [xp, setXp] = useState(String(member.xp));
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const submitting = useRef(false);
  const threshold = 200 * Math.min(Math.max(Number(level) || 1, 1), 15);
  const values = {
    smartpoint: Number(smartpoint),
    level: Number(level),
    xp: Number(xp),
  };
  const valid =
    [smartpoint, level, xp].every(
      (value) => value !== "" && Number.isInteger(Number(value)),
    ) &&
    values.smartpoint >= 0 &&
    values.smartpoint <= 2147483647 &&
    values.level >= 1 &&
    values.level <= 1000000 &&
    values.xp >= 0 &&
    values.xp < threshold;
  const dirty =
    values.smartpoint !== member.smartpoint ||
    values.level !== member.level ||
    values.xp !== member.xp;

  const save = async () => {
    if (!valid || !dirty || submitting.current) return;
    submitting.current = true;
    setBusy(true);
    setNotice("");
    try {
      const updated = await GuildAdmin.request<AdminMember>(
        guildId,
        `/members/${member.discord_id}`,
        values,
        "PATCH",
      );
      onUpdate(updated);
      setSmartpoint(String(updated.smartpoint));
      setLevel(String(updated.level));
      setXp(String(updated.xp));
      setNotice("admin.members.saved");
    } catch (error) {
      setNotice(
        error instanceof Error && ["401", "403"].includes(error.message)
          ? "admin.denied"
          : error instanceof Error && error.message === "404"
            ? "admin.members.departed"
            : "admin.members.saveError",
      );
    } finally {
      setBusy(false);
      submitting.current = false;
    }
  };

  return (
    <tr>
      <td>
        <div className="member-identity">
          <img src={member.avatar_url} alt="" loading="lazy" />
          <div>
            <strong>
              {member.display_name}{" "}
              {member.bot && <span className="member-bot">BOT</span>}
            </strong>
            <span>@{member.username}</span>
            <small>{member.discord_id}</small>
          </div>
        </div>
      </td>
      <td>
        <input
          className="member-number"
          aria-label={t("admin.members.smartpointsFor", {
            name: member.display_name,
          })}
          type="number"
          min={0}
          max={2147483647}
          step={1}
          value={smartpoint}
          disabled={busy}
          onChange={(event) => {
            setSmartpoint(event.target.value);
            setNotice("");
          }}
        />
      </td>
      <td>
        <input
          className="member-number"
          aria-label={t("admin.members.levelFor", {
            name: member.display_name,
          })}
          type="number"
          min={1}
          max={1000000}
          step={1}
          value={level}
          disabled={busy}
          onChange={(event) => {
            setLevel(event.target.value);
            setNotice("");
          }}
        />
      </td>
      <td>
        <input
          className="member-number"
          aria-label={t("admin.members.xpFor", { name: member.display_name })}
          type="number"
          min={0}
          max={threshold - 1}
          step={1}
          value={xp}
          disabled={busy}
          onChange={(event) => {
            setXp(event.target.value);
            setNotice("");
          }}
        />
        <small className="member-xp-limit">/ {threshold} XP</small>
        <div className="member-xp-track">
          <span
            style={{
              width: `${Math.max(0, Math.min(100, (Number(xp) / threshold) * 100))}%`,
            }}
          />
        </div>
        {!valid && dirty && (
          <small className="member-invalid">
            {t("admin.members.invalid", { max: threshold - 1 })}
          </small>
        )}
      </td>
      <td className="member-actions">
        <button
          type="button"
          className="admin-button primary"
          disabled={!valid || !dirty || busy}
          onClick={() => void save()}
        >
          {t(busy ? "profile.saving" : "admin.members.apply")}
        </button>
        {notice && (
          <small
            role={notice === "admin.members.saved" ? "status" : "alert"}
            className={
              notice === "admin.members.saved"
                ? "member-success"
                : "member-invalid"
            }
          >
            {t(notice)}
          </small>
        )}
      </td>
    </tr>
  );
}

export default function AdminMembers() {
  const { t } = useTranslation();
  const { guildId } = useGuildAdmin();
  const [result, setResult] = useState<MembersPage | null>(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");
    const timer = window.setTimeout(async () => {
      try {
        const query = new URLSearchParams({
          search,
          page: String(page),
          page_size: "20",
        });
        const data = await GuildAdmin.request<MembersPage>(
          guildId,
          `/members?${query}`,
        );
        if (!cancelled) setResult(data);
      } catch (failure) {
        if (!cancelled)
          setError(
            failure instanceof Error && ["401", "403"].includes(failure.message)
              ? "admin.denied"
              : "admin.members.loadError",
          );
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 250);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [guildId, search, page, revision]);

  return (
    <div className="admin-content">
      <div className="admin-section-title">
        <div>
          <h2>{t("admin.members.heading")}</h2>
          <p>{t("admin.members.description")}</p>
        </div>
        {result && (
          <span className="admin-count">
            {t("admin.members.count", { count: result.total })}
          </span>
        )}
      </div>
      <div className="admin-panel members-panel">
        <div className="members-toolbar">
          <label className="members-search">
            <span>⌕</span>
            <input
              type="search"
              value={search}
              maxLength={100}
              onChange={(event) => {
                setSearch(event.target.value);
                setPage(1);
              }}
              placeholder={t("admin.members.search")}
              aria-label={t("admin.members.search")}
            />
          </label>
          <button
            className="admin-button secondary"
            type="button"
            disabled={loading}
            onClick={() => setRevision((value) => value + 1)}
          >
            {t("admin.members.refresh")}
          </button>
        </div>
        <div className="admin-info">{t("admin.members.exactValues")}</div>
        {error ? (
          <p role="alert" className="admin-notice error">
            {t(error)}
          </p>
        ) : loading ? (
          <p role="status" className="admin-empty">
            {t("admin.loading")}
          </p>
        ) : result?.members.length ? (
          <div className="members-table-scroll">
            <table className="members-table">
              <thead>
                <tr>
                  <th scope="col">{t("admin.members.member")}</th>
                  <th scope="col">{t("admin.members.smartpoints")}</th>
                  <th scope="col">{t("admin.members.level")}</th>
                  <th scope="col">{t("admin.members.xp")}</th>
                  <th scope="col">{t("admin.members.actions")}</th>
                </tr>
              </thead>
              <tbody>
                {result.members.map((member) => (
                  <MemberRow
                    key={member.discord_id}
                    member={member}
                    guildId={guildId}
                    onUpdate={(updated) =>
                      setResult(
                        (current) =>
                          current && {
                            ...current,
                            members: current.members.map((item) =>
                              item.discord_id === updated.discord_id
                                ? updated
                                : item,
                            ),
                          },
                      )
                    }
                  />
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="admin-empty">
            <span>♙</span>
            <h3>{t("admin.members.empty")}</h3>
          </div>
        )}
        {result && !loading && !error && (
          <div className="members-pagination">
            <button
              className="admin-button secondary"
              disabled={page <= 1}
              onClick={() => setPage((value) => value - 1)}
            >
              {t("admin.members.previous")}
            </button>
            <span>
              {t("admin.members.page", {
                page,
                total: Math.max(1, Math.ceil(result.total / result.page_size)),
              })}
            </span>
            <button
              className="admin-button secondary"
              disabled={page * result.page_size >= result.total}
              onClick={() => setPage((value) => value + 1)}
            >
              {t("admin.members.next")}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
