import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { GuildAdmin, GuildAdminError } from "../../../models/guild-admin";
import type {
  RoleCatalog,
  RoleMutation,
  RoleRule,
  RoleSync,
} from "../../../models/guild-admin";
import { useGuildAdmin } from "./context";
import RulesAcceptanceSettings from "./rules-acceptance";

export default function AdminRoles() {
  const { t } = useTranslation();
  const { guildId } = useGuildAdmin();
  const [catalog, setCatalog] = useState<RoleCatalog | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [roleId, setRoleId] = useState("");
  const [mode, setMode] = useState<"level" | "reaction">("level");
  const [level, setLevel] = useState("1");
  const [emoji, setEmoji] = useState("");
  const [messageId, setMessageId] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState<{
    key: string;
    updated?: number;
    failed?: number;
  } | null>(null);
  const submitting = useRef(false);

  const failure = (reason: unknown) => {
    setError(
      reason instanceof GuildAdminError &&
        reason.detail?.startsWith("admin.roles.")
        ? reason.detail
        : reason instanceof Error && ["401", "403"].includes(reason.message)
          ? "admin.denied"
          : "admin.roles.error",
    );
  };

  useEffect(() => {
    let cancelled = false;
    GuildAdmin.request<RoleCatalog>(guildId, "/roles")
      .then((result) => {
        if (!cancelled) setCatalog(result);
      })
      .catch((reason) => {
        if (!cancelled) failure(reason);
      });
    return () => {
      cancelled = true;
    };
  }, [guildId]);

  const report = (sync: RoleSync | null, saved = true) =>
    setNotice({
      key: sync?.failed
        ? "admin.roles.partialSync"
        : saved
          ? "admin.roles.saved"
          : "admin.roles.synced",
      updated: sync?.updated ?? 0,
      failed: sync?.failed ?? 0,
    });

  const reset = () => {
    setEditingId(null);
    setRoleId("");
    setMode("level");
    setLevel("1");
    setEmoji("");
    setMessageId("");
  };

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setBusy(true);
    setError("");
    setNotice(null);
    try {
      const result = await GuildAdmin.request<RoleMutation>(
        guildId,
        editingId === null ? "/roles" : `/roles/${editingId}`,
        {
          discord_id: roleId,
          mode,
          level: mode === "level" ? Number(level) : null,
          emoji: mode === "reaction" ? emoji.trim() : null,
          message_discord_id: mode === "reaction" ? messageId.trim() : null,
        },
        editingId === null ? "POST" : "PATCH",
      );
      setCatalog(
        (current) =>
          current && {
            ...current,
            rules:
              editingId === null
                ? [...current.rules, result.rule]
                : current.rules.map((rule) =>
                    rule.id === editingId ? result.rule : rule,
                  ),
          },
      );
      report(result.sync);
      reset();
    } catch (reason) {
      failure(reason);
    } finally {
      setBusy(false);
      submitting.current = false;
    }
  };

  const remove = async (rule: RoleRule) => {
    if (
      submitting.current ||
      !window.confirm(t("admin.roles.confirmDelete", { name: rule.name }))
    )
      return;
    submitting.current = true;
    setBusy(true);
    setError("");
    setNotice(null);
    try {
      const result = await GuildAdmin.request<{ sync: RoleSync | null }>(
        guildId,
        `/roles/${rule.id}`,
        undefined,
        "DELETE",
      );
      setCatalog(
        (current) =>
          current && {
            ...current,
            rules: current.rules.filter((item) => item.id !== rule.id),
          },
      );
      if (editingId === rule.id) reset();
      report(result.sync);
    } catch (reason) {
      failure(reason);
    } finally {
      setBusy(false);
      submitting.current = false;
    }
  };

  const sync = async () => {
    if (submitting.current) return;
    submitting.current = true;
    setBusy(true);
    setError("");
    setNotice(null);
    try {
      report(
        await GuildAdmin.request<RoleSync>(
          guildId,
          "/roles/sync",
          undefined,
          "POST",
        ),
        false,
      );
    } catch (reason) {
      failure(reason);
    } finally {
      setBusy(false);
      submitting.current = false;
    }
  };

  if (!catalog)
    return (
      <div className="admin-panel" role={error ? "alert" : "status"}>
        {t(error || "admin.loading")}
      </div>
    );

  const selected = catalog.roles.find((role) => role.discord_id === roleId);
  const configured = new Set(
    catalog.rules
      .filter((rule) => rule.id !== editingId)
      .map((rule) => rule.discord_id),
  );

  return (
    <div className="admin-content">
      <RulesAcceptanceSettings guildId={guildId} />
      <div className="admin-section-title">
        <div>
          <h2>{t("admin.roles.heading")}</h2>
          <p>{t("admin.roles.description")}</p>
        </div>
        <span className="admin-count">
          {t("admin.roles.count", { count: catalog.rules.length })}
        </span>
      </div>
      {error && (
        <p role="alert" className="admin-panel admin-notice error">
          {t(error)}
        </p>
      )}
      {notice && (
        <p
          role="status"
          className={`admin-panel admin-notice ${notice.failed ? "error" : "success"}`}
        >
          {t(notice.key, { count: notice.updated, failed: notice.failed })}
        </p>
      )}
      <div className="admin-editor-grid roles-editor-grid">
        <form
          className="admin-panel admin-form"
          onSubmit={(event) => void save(event)}
        >
          <h3>
            {t(editingId === null ? "admin.roles.new" : "admin.roles.edit")}
          </h3>
          <fieldset className="admin-form-fields" disabled={busy}>
            <label>
              {t("admin.roles.discordRole")}
              <select
                required
                value={roleId}
                onChange={(event) => setRoleId(event.target.value)}
              >
                <option value="">{t("admin.roles.chooseRole")}</option>
                {catalog.roles.map((role) => (
                  <option
                    key={role.discord_id}
                    value={role.discord_id}
                    disabled={
                      Boolean(role.unavailable) ||
                      configured.has(role.discord_id)
                    }
                  >
                    {role.name}
                    {role.unavailable
                      ? ` — ${t(role.unavailable)}`
                      : configured.has(role.discord_id)
                        ? ` — ${t("admin.roles.configured")}`
                        : ""}
                  </option>
                ))}
              </select>
            </label>
            <div className="role-mode-picker">
              <button
                type="button"
                className={mode === "level" ? "selected" : ""}
                aria-pressed={mode === "level"}
                onClick={() => setMode("level")}
              >
                <span>✦</span>
                {t("admin.roles.levelMode")}
              </button>
              <button
                type="button"
                className={mode === "reaction" ? "selected" : ""}
                aria-pressed={mode === "reaction"}
                onClick={() => setMode("reaction")}
              >
                <span>☻</span>
                {t("admin.roles.reactionMode")}
              </button>
            </div>
            {mode === "level" ? (
              <>
                <label>
                  {t("admin.roles.requiredLevel")}
                  <input
                    type="number"
                    required
                    min={1}
                    max={1000000}
                    step={1}
                    value={level}
                    onChange={(event) => setLevel(event.target.value)}
                  />
                </label>
                <p className="admin-info">{t("admin.roles.levelHelp")}</p>
              </>
            ) : (
              <>
                <label>
                  {t("admin.roles.emoji")}
                  <input
                    required
                    maxLength={100}
                    value={emoji}
                    onChange={(event) => setEmoji(event.target.value)}
                    placeholder="🎮 / <:gaming:123456789012345678>"
                  />
                </label>
                <label>
                  {t("admin.roles.message")}
                  <input
                    required
                    inputMode="numeric"
                    pattern="[1-9][0-9]{0,21}"
                    maxLength={22}
                    value={messageId}
                    onChange={(event) => setMessageId(event.target.value)}
                    placeholder="123456789012345678"
                  />
                </label>
                <p className="admin-info">{t("admin.roles.reactionHelp")}</p>
              </>
            )}
            {selected?.unavailable && (
              <p className="admin-notice error">{t(selected.unavailable)}</p>
            )}
            <button
              className="admin-button primary"
              disabled={busy || !selected || Boolean(selected.unavailable)}
            >
              {t(
                busy
                  ? "profile.saving"
                  : editingId === null
                    ? "admin.roles.create"
                    : "admin.saveChanges",
              )}
            </button>
            {editingId !== null && (
              <button
                type="button"
                className="admin-button secondary"
                onClick={reset}
              >
                {t("admin.cancel")}
              </button>
            )}
          </fieldset>
        </form>
        <div className="admin-panel role-explainer">
          <p className="admin-eyebrow">{t("admin.roles.automation")}</p>
          <h3>{t("admin.roles.howTitle")}</h3>
          <div>
            <span>✦</span>
            <p>{t("admin.roles.levelHelp")}</p>
          </div>
          <div>
            <span>☻</span>
            <p>{t("admin.roles.reactionHelp")}</p>
          </div>
          <div className="admin-info">{t("admin.roles.permissionsHelp")}</div>
          <button
            type="button"
            className="admin-button secondary"
            disabled={busy}
            onClick={() => void sync()}
          >
            {t(busy ? "profile.saving" : "admin.roles.sync")}
          </button>
        </div>
      </div>
      <div className="admin-section-title">
        <h2>{t("admin.roles.rules")}</h2>
      </div>
      <div className="admin-card-grid">
        {catalog.rules.length === 0 && (
          <div className="admin-panel admin-empty">
            <span>♜</span>
            <h3>{t("admin.roles.empty")}</h3>
            <p>{t("admin.roles.emptyHelp")}</p>
          </div>
        )}
        {catalog.rules.map((rule) => (
          <article className="admin-panel role-rule-card" key={rule.id}>
            <div className="admin-panel-heading">
              <span
                className="role-discord-pill"
                style={{ borderColor: rule.color }}
              >
                <span style={{ backgroundColor: rule.color }} />
                {rule.name}
              </span>
              <span className="admin-count">
                {t(
                  rule.mode === "level"
                    ? "admin.roles.levelMode"
                    : "admin.roles.reactionMode",
                )}
              </span>
            </div>
            {rule.missing && (
              <p className="admin-notice error">
                {t("admin.roles.missingRole")}
              </p>
            )}
            <p className="role-rule-condition">
              {rule.mode === "level"
                ? t("admin.roles.unlockLevel", { count: rule.level ?? 1 })
                : `${rule.emoji} · ${t("admin.roles.messageShort")} ${rule.message_discord_id}`}
            </p>
            <div className="wallpaper-edit-actions">
              <button
                type="button"
                className="admin-text-button"
                disabled={busy}
                onClick={() => {
                  setEditingId(rule.id);
                  setRoleId(rule.discord_id);
                  setMode(rule.mode);
                  setLevel(String(rule.level ?? 1));
                  setEmoji(rule.emoji ?? "");
                  setMessageId(rule.message_discord_id ?? "");
                  setError("");
                  setNotice(null);
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
              >
                {t("admin.roles.edit")}
              </button>
              <button
                type="button"
                className="role-remove-button"
                disabled={busy}
                onClick={() => void remove(rule)}
              >
                {t("admin.roles.remove")}
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
