import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { GuildAdmin, GuildAdminError } from "../../../models/guild-admin";

interface RulesAcceptance {
  message_discord_id: string | null;
  emoji: string | null;
}

export default function RulesAcceptanceSettings({
  guildId,
}: {
  guildId: number;
}) {
  const { t } = useTranslation();
  const [settings, setSettings] = useState<RulesAcceptance | null>(null);
  const [message, setMessage] = useState("");
  const [emoji, setEmoji] = useState("✅");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const submitting = useRef(false);

  const apply = (result: RulesAcceptance) => {
    setSettings(result);
    setMessage(result.message_discord_id ?? "");
    setEmoji(result.emoji ?? "✅");
  };

  const failure = (reason: unknown) =>
    setError(
      reason instanceof GuildAdminError &&
        (reason.detail?.startsWith("admin.acceptance.") ||
          reason.detail?.startsWith("admin.roles."))
        ? reason.detail
        : reason instanceof Error && ["401", "403"].includes(reason.message)
          ? "admin.denied"
          : "admin.acceptance.error",
    );

  useEffect(() => {
    let cancelled = false;
    GuildAdmin.request<RulesAcceptance>(guildId, "/rules-acceptance")
      .then((result) => {
        if (!cancelled) apply(result);
      })
      .catch((reason) => {
        if (!cancelled) failure(reason);
      });
    return () => {
      cancelled = true;
    };
  }, [guildId]);

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      apply(
        await GuildAdmin.request<RulesAcceptance>(
          guildId,
          "/rules-acceptance",
          { message, emoji },
          "PATCH",
        ),
      );
      setNotice("admin.acceptance.saved");
    } catch (reason) {
      failure(reason);
    } finally {
      setBusy(false);
      submitting.current = false;
    }
  };

  const disable = async () => {
    if (
      submitting.current ||
      !window.confirm(t("admin.acceptance.confirmDisable"))
    )
      return;
    submitting.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      apply(
        await GuildAdmin.request<RulesAcceptance>(
          guildId,
          "/rules-acceptance",
          undefined,
          "DELETE",
        ),
      );
      setNotice("admin.acceptance.disabled");
    } catch (reason) {
      failure(reason);
    } finally {
      setBusy(false);
      submitting.current = false;
    }
  };

  return (
    <section className="admin-panel rules-acceptance-panel">
      <div className="admin-section-title">
        <div>
          <p className="admin-eyebrow">{t("admin.acceptance.eyebrow")}</p>
          <h2>{t("admin.acceptance.title")}</h2>
          <p>{t("admin.acceptance.description")}</p>
        </div>
        <span className="admin-count">
          {t(
            settings?.message_discord_id && settings.emoji
              ? "admin.acceptance.enabled"
              : "admin.acceptance.notConfigured",
          )}
        </span>
      </div>
      {error && (
        <p role="alert" className="admin-notice error">
          {t(error)}
        </p>
      )}
      {notice && (
        <p role="status" className="admin-notice success">
          {t(notice)}
        </p>
      )}
      {!settings && !error ? (
        <p role="status">{t("admin.loading")}</p>
      ) : (
        <form className="admin-form" onSubmit={(event) => void save(event)}>
          <fieldset disabled={busy} className="rules-acceptance-fields">
            <label>
              {t("admin.acceptance.message")}
              <input
                required
                maxLength={200}
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                placeholder="https://discord.com/channels/…/…/…"
              />
              <span className="admin-hint">
                {t("admin.acceptance.messageHelp")}
              </span>
            </label>
            <label>
              {t("admin.acceptance.emoji")}
              <input
                required
                maxLength={100}
                value={emoji}
                onChange={(event) => setEmoji(event.target.value)}
                placeholder="✅"
              />
            </label>
            <div className="wallpaper-edit-actions">
              <button
                className="admin-button primary"
                disabled={busy || !message.trim() || !emoji.trim()}
              >
                {t(busy ? "profile.saving" : "admin.saveChanges")}
              </button>
              {settings?.message_discord_id && (
                <button
                  className="admin-button secondary"
                  type="button"
                  disabled={busy}
                  onClick={() => void disable()}
                >
                  {t("admin.acceptance.disable")}
                </button>
              )}
            </div>
          </fieldset>
          <p className="admin-info">{t("admin.acceptance.behavior")}</p>
        </form>
      )}
    </section>
  );
}
