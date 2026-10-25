import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { GuildAdmin, GuildAdminError } from "../../../models/guild-admin";
import { useGuildAdmin } from "./context";

interface AutomaticMessage {
  id: number;
  name: string;
  channel_id: string;
  channel_name: string;
  missing_channel: boolean;
  message: string;
  day: string;
  time: string;
  timezone: string;
  last_sent_date: string | null;
  attachment_name: string | null;
  has_attachment: boolean;
}
interface Catalog {
  messages: AutomaticMessage[];
  channels: { discord_id: string; name: string; available: boolean }[];
  timezones: string[];
}
const days = [
  "daily",
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];
const initial = {
  name: "",
  channel_id: "",
  message: "",
  day: "daily",
  time: "18:00",
  timezone: "Europe/Zurich",
};

export default function AdminMessages() {
  const { t } = useTranslation();
  const { guildId } = useGuildAdmin();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [draft, setDraft] = useState(initial);
  const [editing, setEditing] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const submitting = useRef(false);
  const selected = catalog?.messages.find((item) => item.id === editing);
  const failure = (reason: unknown) =>
    setError(
      reason instanceof GuildAdminError &&
        reason.detail?.startsWith("admin.messages.")
        ? reason.detail
        : reason instanceof Error && reason.message === "413"
          ? "admin.messages.tooLarge"
          : reason instanceof Error && ["401", "403"].includes(reason.message)
            ? "admin.denied"
            : "admin.messages.error",
    );

  useEffect(() => {
    let cancelled = false;
    GuildAdmin.request<Catalog>(guildId, "/messages")
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

  const replace = (result: AutomaticMessage) =>
    setCatalog(
      (current) =>
        current && {
          ...current,
          messages: current.messages.some((item) => item.id === result.id)
            ? current.messages.map((item) =>
                item.id === result.id ? result : item,
              )
            : [...current.messages, result],
        },
    );
  const reset = () => {
    setEditing(null);
    setDraft(initial);
  };
  const start = () => {
    if (submitting.current) return false;
    submitting.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    return true;
  };
  const finish = () => {
    submitting.current = false;
    setBusy(false);
  };

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!start()) return;
    try {
      const result = await GuildAdmin.request<AutomaticMessage>(
        guildId,
        editing === null ? "/messages" : `/messages/${editing}`,
        draft,
        editing === null ? "POST" : "PATCH",
      );
      replace(result);
      setEditing(result.id);
      setNotice("admin.messages.saved");
    } catch (reason) {
      failure(reason);
    } finally {
      finish();
    }
  };

  const remove = async (item: AutomaticMessage) => {
    if (
      !window.confirm(t("admin.messages.confirmDelete", { name: item.name })) ||
      !start()
    )
      return;
    try {
      await GuildAdmin.request(
        guildId,
        `/messages/${item.id}`,
        undefined,
        "DELETE",
      );
      setCatalog(
        (current) =>
          current && {
            ...current,
            messages: current.messages.filter(
              (message) => message.id !== item.id,
            ),
          },
      );
      if (editing === item.id) reset();
      setNotice("admin.messages.deleted");
    } catch (reason) {
      failure(reason);
    } finally {
      finish();
    }
  };

  const upload = async (file: File | undefined) => {
    if (!file || editing === null) return;
    if (file.size > 8 * 1024 * 1024) {
      setError("admin.messages.tooLarge");
      return;
    }
    if (!start()) return;
    try {
      const form = new FormData();
      form.append("attachment", file);
      const response = await fetch(
        `/api/sessions/guilds/${guildId}/admin/messages/${editing}/attachment`,
        { method: "POST", credentials: "include", body: form },
      );
      if (!response.ok) {
        const result = await response.json().catch(() => ({}));
        throw new GuildAdminError(
          response.status,
          typeof result.detail === "string" ? result.detail : undefined,
        );
      }
      replace(await response.json());
      setNotice("admin.messages.attachmentSaved");
    } catch (reason) {
      failure(reason);
    } finally {
      finish();
    }
  };

  const removeAttachment = async () => {
    if (editing === null || !start()) return;
    try {
      replace(
        await GuildAdmin.request<AutomaticMessage>(
          guildId,
          `/messages/${editing}/attachment`,
          undefined,
          "DELETE",
        ),
      );
      setNotice("admin.messages.attachmentRemoved");
    } catch (reason) {
      failure(reason);
    } finally {
      finish();
    }
  };

  if (!catalog)
    return (
      <div className="admin-panel" role={error ? "alert" : "status"}>
        {t(error || "admin.loading")}
      </div>
    );
  return (
    <div className="admin-content">
      <div className="admin-section-title">
        <div>
          <h2>{t("admin.messages.title")}</h2>
          <p>{t("admin.messages.description")}</p>
        </div>
        <span className="admin-count">{catalog.messages.length}</span>
      </div>
      {error && (
        <p role="alert" className="admin-panel admin-notice error">
          {t(error)}
        </p>
      )}
      {notice && (
        <p role="status" className="admin-panel admin-notice success">
          {t(notice)}
        </p>
      )}
      <div className="admin-editor-grid">
        <form
          className="admin-panel admin-form"
          onSubmit={(event) => void save(event)}
        >
          <h3>
            {t(editing === null ? "admin.messages.new" : "admin.messages.edit")}
          </h3>
          <fieldset disabled={busy} className="admin-form-fields">
            <label>
              {t("admin.name")}
              <input
                required
                maxLength={80}
                value={draft.name}
                onChange={(event) =>
                  setDraft({ ...draft, name: event.target.value })
                }
              />
            </label>
            <label>
              {t("admin.messages.channel")}
              <select
                required
                value={draft.channel_id}
                onChange={(event) =>
                  setDraft({ ...draft, channel_id: event.target.value })
                }
              >
                <option value="">{t("admin.messages.chooseChannel")}</option>
                {catalog.channels.map((channel) => (
                  <option
                    key={channel.discord_id}
                    value={channel.discord_id}
                    disabled={!channel.available}
                  >
                    #{channel.name}
                    {!channel.available
                      ? ` — ${t("admin.messages.channelPermission")}`
                      : ""}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("admin.messages.content")}
              <textarea
                className="automatic-message-content"
                required={!selected?.has_attachment}
                maxLength={2000}
                rows={6}
                value={draft.message}
                onChange={(event) =>
                  setDraft({ ...draft, message: event.target.value })
                }
              />
              <span className="admin-hint">{draft.message.length} / 2000</span>
            </label>
            <div className="banner-coordinates">
              <label>
                {t("admin.messages.day")}
                <select
                  value={draft.day}
                  onChange={(event) =>
                    setDraft({ ...draft, day: event.target.value })
                  }
                >
                  {days.map((day) => (
                    <option key={day} value={day}>
                      {t(`admin.messages.days.${day}`)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("admin.messages.time")}
                <input
                  type="time"
                  required
                  value={draft.time}
                  onChange={(event) =>
                    setDraft({ ...draft, time: event.target.value })
                  }
                />
              </label>
            </div>
            <label>
              {t("admin.messages.timezone")}
              <select
                required
                value={draft.timezone}
                onChange={(event) =>
                  setDraft({ ...draft, timezone: event.target.value })
                }
              >
                {catalog.timezones.map((zone) => (
                  <option key={zone} value={zone}>
                    {zone}
                  </option>
                ))}
              </select>
            </label>
            <button className="admin-button primary" disabled={busy}>
              {t(busy ? "profile.saving" : "admin.saveChanges")}
            </button>
            {editing !== null && (
              <button
                className="admin-button secondary"
                type="button"
                onClick={reset}
              >
                {t("admin.messages.new")}
              </button>
            )}
          </fieldset>
        </form>
        <div className="admin-panel admin-form">
          <p className="admin-eyebrow">{t("admin.messages.preview")}</p>
          <div className="automatic-message-preview">
            <strong>
              #
              {catalog.channels.find(
                (channel) => channel.discord_id === draft.channel_id,
              )?.name ?? "…"}
            </strong>
            <p>{draft.message || t("admin.messages.emptyPreview")}</p>
          </div>
          <p className="admin-info">{t("admin.messages.behavior")}</p>
          <h3>{t("admin.messages.attachment")}</h3>
          {editing === null ? (
            <p className="admin-hint">{t("admin.messages.saveFirst")}</p>
          ) : (
            <>
              <p className="admin-hint">
                {selected?.attachment_name ?? t("admin.messages.noAttachment")}
              </p>
              <label>
                {t("admin.messages.upload")}
                <input
                  key={`${editing}-${selected?.attachment_name ?? "none"}`}
                  type="file"
                  disabled={busy}
                  onChange={(event) => {
                    void upload(event.target.files?.[0]);
                    event.target.value = "";
                  }}
                />
                <span className="admin-hint">
                  {t("admin.messages.attachmentHelp")}
                </span>
              </label>
              {selected?.has_attachment && (
                <button
                  type="button"
                  className="admin-button secondary"
                  disabled={busy}
                  onClick={() => void removeAttachment()}
                >
                  {t("admin.messages.removeAttachment")}
                </button>
              )}
            </>
          )}
        </div>
      </div>
      <div className="admin-card-grid">
        {catalog.messages.length === 0 && (
          <div className="admin-panel admin-empty">
            {t("admin.messages.empty")}
          </div>
        )}
        {catalog.messages.map((item) => (
          <article className="admin-panel role-rule-card" key={item.id}>
            <div className="admin-panel-heading">
              <h3>{item.name}</h3>
              <span className="admin-count">#{item.channel_name}</span>
            </div>
            <p className="role-rule-condition">
              {t(`admin.messages.days.${item.day}`)} · {item.time} ·{" "}
              {item.timezone}
            </p>
            <p className="automatic-message-excerpt">{item.message}</p>
            {item.has_attachment && (
              <small className="admin-hint">▧ {item.attachment_name}</small>
            )}
            {item.missing_channel && (
              <p className="admin-notice error">
                {t("admin.messages.missingChannel")}
              </p>
            )}
            <small className="admin-hint">
              {t("admin.messages.lastSent", {
                date: item.last_sent_date ?? "—",
              })}
            </small>
            <div className="wallpaper-edit-actions">
              <button
                className="admin-text-button"
                disabled={busy}
                onClick={() => {
                  setEditing(item.id);
                  setDraft({
                    name: item.name,
                    channel_id: item.channel_id,
                    message: item.message,
                    day: item.day,
                    time: item.time,
                    timezone: item.timezone,
                  });
                  setError("");
                  setNotice("");
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
              >
                {t("admin.messages.edit")}
              </button>
              <button
                className="role-remove-button"
                disabled={busy}
                onClick={() => void remove(item)}
              >
                {t("admin.messages.delete")}
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
