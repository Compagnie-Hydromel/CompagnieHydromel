import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { GuildAdmin, GuildAdminError } from "../../../models/guild-admin";
import type { BannerChannel, BannerData } from "../../../models/guild-admin";
import { useGuildAdmin } from "./context";

export default function AdminBanner() {
  const { t } = useTranslation();
  const { guildId } = useGuildAdmin();
  const [data, setData] = useState<BannerData | null>(null);
  const [editing, setEditing] = useState<number | null>(null);
  const [channelId, setChannelId] = useState("");
  const [x, setX] = useState(0);
  const [y, setY] = useState(0);
  const [size, setSize] = useState({ width: 960, height: 540 });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const canvas = useRef<HTMLDivElement>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const submitting = useRef(false);
  const drag = useRef<{
    startX: number;
    startY: number;
    x: number;
    y: number;
  } | null>(null);

  const failure = (reason: unknown) =>
    setError(
      reason instanceof GuildAdminError &&
        reason.detail?.startsWith("admin.banner.")
        ? reason.detail
        : reason instanceof Error && ["401", "403"].includes(reason.message)
          ? "admin.denied"
          : reason instanceof Error && reason.message === "413"
            ? "admin.imageTooLarge"
            : "admin.banner.error",
    );

  useEffect(() => {
    let cancelled = false;
    GuildAdmin.request<BannerData>(guildId, "/banner")
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((reason) => {
        if (!cancelled) failure(reason);
      });
    return () => {
      cancelled = true;
    };
  }, [guildId]);

  const reset = () => {
    setEditing(null);
    setChannelId("");
    setX(0);
    setY(0);
  };
  const edit = (channel: BannerChannel) => {
    setEditing(channel.id);
    setChannelId(channel.discord_id);
    setX(channel.x);
    setY(channel.y);
    setNotice("");
  };

  const upload = async (file: File | undefined) => {
    if (!file || submitting.current) return;
    if (file.size > 8 * 1024 * 1024) {
      setError("admin.imageTooLarge");
      return;
    }
    submitting.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const form = new FormData();
      form.append("image", file);
      const result = await GuildAdmin.uploadBanner(guildId, form);
      setData(
        (current) => current && { ...current, image_url: result.image_url },
      );
      setNotice("admin.banner.saved");
    } catch (reason) {
      if (reason instanceof Error && reason.message === "422")
        setError("admin.invalidImage");
      else failure(reason);
    } finally {
      setBusy(false);
      submitting.current = false;
      if (fileInput.current) fileInput.current.value = "";
    }
  };

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const result = await GuildAdmin.request<BannerChannel>(
        guildId,
        editing === null ? "/banner/channels" : `/banner/channels/${editing}`,
        editing === null ? { discord_id: channelId, x, y } : { x, y },
        editing === null ? "POST" : "PATCH",
      );
      setData(
        (current) =>
          current && {
            ...current,
            channels:
              editing === null
                ? [...current.channels, result]
                : current.channels.map((item) =>
                    item.id === editing ? result : item,
                  ),
          },
      );
      reset();
      setNotice("admin.banner.saved");
    } catch (reason) {
      failure(reason);
    } finally {
      setBusy(false);
      submitting.current = false;
    }
  };

  const remove = async (channel: BannerChannel) => {
    if (
      submitting.current ||
      !window.confirm(t("admin.banner.confirmRemove", { name: channel.name }))
    )
      return;
    submitting.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await GuildAdmin.request(
        guildId,
        `/banner/channels/${channel.id}`,
        undefined,
        "DELETE",
      );
      setData(
        (current) =>
          current && {
            ...current,
            channels: current.channels.filter((item) => item.id !== channel.id),
          },
      );
      if (editing === channel.id) reset();
      setNotice("admin.banner.saved");
    } catch (reason) {
      failure(reason);
    } finally {
      setBusy(false);
      submitting.current = false;
    }
  };

  const disable = async () => {
    if (submitting.current || !window.confirm(t("admin.banner.confirmDisable")))
      return;
    submitting.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await GuildAdmin.request(guildId, "/banner/image", undefined, "DELETE");
      setData((current) => current && { ...current, image_url: null });
      setNotice("admin.banner.disabled");
    } catch (reason) {
      failure(reason);
    } finally {
      setBusy(false);
      submitting.current = false;
    }
  };

  if (!data)
    return (
      <div className="admin-panel" role={error ? "alert" : "status"}>
        {t(error || "admin.loading")}
      </div>
    );
  const selected = data.available_channels.find(
    (item) => item.discord_id === channelId,
  );
  const markers = data.channels.map((item) =>
    item.id === editing && selected ? { ...item, x, y } : item,
  );
  if (selected && editing === null)
    markers.push({
      id: -1,
      discord_id: channelId,
      name: selected.name,
      missing: false,
      x,
      y,
    });

  return (
    <div className="admin-content">
      <div className="admin-section-title">
        <div>
          <h2>{t("admin.banner.heading")}</h2>
          <p>{t("admin.banner.description")}</p>
        </div>
        <span className="admin-count">
          {data.channels.length} {t("admin.banner.channels")}
        </span>
      </div>
      {error && (
        <p className="admin-panel admin-notice error" role="alert">
          {t(error)}
        </p>
      )}
      {notice && (
        <p className="admin-panel admin-notice success" role="status">
          {t(notice)}
        </p>
      )}
      {!data.can_update_banner && (
        <p className="admin-panel admin-info">
          {t("admin.banner.requirements")}
        </p>
      )}
      <div className="admin-panel admin-form">
        <div className="admin-panel-heading">
          <span className="admin-eyebrow">{t("admin.livePreview")}</span>
          <span className="admin-dimensions">
            {size.width} × {size.height}
          </span>
        </div>
        <div
          ref={canvas}
          className="banner-canvas"
          style={{ aspectRatio: `${size.width} / ${size.height}` }}
        >
          {data.image_url ? (
            <img
              className="banner-background"
              src={data.image_url}
              alt={t("admin.banner.preview")}
              draggable={false}
              onLoad={(event) =>
                setSize({
                  width: event.currentTarget.naturalWidth,
                  height: event.currentTarget.naturalHeight,
                })
              }
              onError={() => setError("admin.banner.imageError")}
            />
          ) : (
            <div className="banner-placeholder">
              ▧ {t("admin.banner.uploadHint")}
            </div>
          )}
          {markers.map((channel) => (
            <button
              type="button"
              key={channel.id}
              className={`banner-channel-marker ${channel.discord_id === channelId ? "selected" : ""}`}
              style={{
                left: `${(channel.x / size.width) * 100}%`,
                top: `${(channel.y / size.height) * 100}%`,
                width: `${(64 / size.width) * 100}%`,
                height: `${(64 / size.height) * 100}%`,
              }}
              aria-label={t("admin.banner.moveChannel", { name: channel.name })}
              disabled={busy}
              onPointerDown={(event) => {
                if (event.button !== 0 || busy) return;
                event.preventDefault();
                event.currentTarget.setPointerCapture(event.pointerId);
                if (channel.id !== -1) edit(channel);
                drag.current = {
                  startX: event.clientX,
                  startY: event.clientY,
                  x: channel.x,
                  y: channel.y,
                };
              }}
              onPointerMove={(event) => {
                if (!drag.current || !canvas.current) return;
                const rect = canvas.current.getBoundingClientRect();
                setX(
                  Math.max(
                    0,
                    Math.min(
                      Math.max(0, size.width - 64),
                      Math.round(
                        drag.current.x +
                          ((event.clientX - drag.current.startX) * size.width) /
                            rect.width,
                      ),
                    ),
                  ),
                );
                setY(
                  Math.max(
                    0,
                    Math.min(
                      Math.max(0, size.height - 64),
                      Math.round(
                        drag.current.y +
                          ((event.clientY - drag.current.startY) *
                            size.height) /
                            rect.height,
                      ),
                    ),
                  ),
                );
              }}
              onPointerUp={() => {
                drag.current = null;
              }}
              onPointerCancel={() => {
                drag.current = null;
              }}
              onLostPointerCapture={() => {
                drag.current = null;
              }}
              onClick={() => {
                if (channel.id !== -1 && channel.discord_id !== channelId)
                  edit(channel);
              }}
              onKeyDown={(event) => {
                const movements: Record<string, [number, number]> = {
                  ArrowLeft: [-1, 0],
                  ArrowRight: [1, 0],
                  ArrowUp: [0, -1],
                  ArrowDown: [0, 1],
                };
                const delta = movements[event.key];
                if (!delta) return;
                event.preventDefault();
                if (channel.id !== -1) edit(channel);
                const step = event.shiftKey ? 10 : 1;
                setX(
                  Math.max(
                    0,
                    Math.min(
                      Math.max(0, size.width - 64),
                      channel.x + delta[0] * step,
                    ),
                  ),
                );
                setY(
                  Math.max(
                    0,
                    Math.min(
                      Math.max(0, size.height - 64),
                      channel.y + delta[1] * step,
                    ),
                  ),
                );
              }}
            >
              <img
                src={
                  data.available_channels.find(
                    (item) => item.discord_id === channel.discord_id,
                  )?.avatars[0] ??
                  "https://cdn.discordapp.com/embed/avatars/0.png"
                }
                alt=""
                draggable={false}
              />
              <span>{channel.name}</span>
            </button>
          ))}
        </div>
        <p className="admin-hint">{t("admin.banner.dragHint")}</p>
        <label>
          {t("admin.banner.image")}
          <input
            ref={fileInput}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            disabled={busy}
            onChange={(event) => void upload(event.target.files?.[0])}
          />
          <span className="admin-hint">{t("admin.banner.imageHelp")}</span>
        </label>
        {data.image_url && (
          <button
            className="admin-button secondary"
            type="button"
            disabled={busy}
            onClick={() => void disable()}
          >
            {t("admin.banner.disable")}
          </button>
        )}
      </div>
      <div className="admin-editor-grid">
        <form
          className="admin-panel admin-form"
          onSubmit={(event) => void save(event)}
        >
          <h3>
            {t(editing === null ? "admin.banner.add" : "admin.banner.edit")}
          </h3>
          <fieldset disabled={busy} className="admin-form-fields">
            <label>
              {t("admin.banner.channel")}
              <select
                required
                value={channelId}
                disabled={editing !== null}
                onChange={(event) => setChannelId(event.target.value)}
              >
                <option value="">{t("admin.banner.chooseChannel")}</option>
                {data.available_channels.map((channel) => (
                  <option
                    key={channel.discord_id}
                    value={channel.discord_id}
                    disabled={data.channels.some(
                      (item) =>
                        item.discord_id === channel.discord_id &&
                        item.id !== editing,
                    )}
                  >
                    {channel.name}
                  </option>
                ))}
              </select>
            </label>
            <div className="banner-coordinates">
              <label>
                X
                <input
                  type="number"
                  required
                  min={0}
                  max={16384}
                  step={1}
                  value={x}
                  onChange={(event) => setX(Number(event.target.value))}
                />
              </label>
              <label>
                Y
                <input
                  type="number"
                  required
                  min={0}
                  max={16384}
                  step={1}
                  value={y}
                  onChange={(event) => setY(Number(event.target.value))}
                />
              </label>
            </div>
            <button
              className="admin-button primary"
              disabled={busy || !channelId}
            >
              {t(busy ? "profile.saving" : "admin.saveChanges")}
            </button>
            {editing !== null && (
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
          <p className="admin-eyebrow">{t("admin.banner.automatic")}</p>
          <h3>{t("admin.banner.howTitle")}</h3>
          <p className="admin-info">{t("admin.banner.behavior")}</p>
        </div>
      </div>
      <div className="admin-card-grid">
        {data.channels.length === 0 && (
          <div className="admin-panel admin-empty">
            {t("admin.banner.empty")}
          </div>
        )}
        {data.channels.map((channel) => (
          <article className="admin-panel role-rule-card" key={channel.id}>
            <h3>♬ {channel.name}</h3>
            <span className="admin-dimensions">
              X: {channel.x} · Y: {channel.y}
            </span>
            {channel.missing && (
              <p className="admin-notice error">
                {t("admin.banner.missingChannel")}
              </p>
            )}
            <div className="wallpaper-edit-actions">
              <button
                className="admin-text-button"
                disabled={busy}
                onClick={() => edit(channel)}
              >
                {t("admin.banner.edit")}
              </button>
              <button
                className="role-remove-button"
                disabled={busy}
                onClick={() => void remove(channel)}
              >
                {t("admin.banner.remove")}
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
