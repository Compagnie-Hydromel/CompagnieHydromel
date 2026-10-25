import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { GuildAdmin } from "../../../models/guild-admin";
import type { AdminWallpaper } from "../../../models/guild-admin";

export default function WallpaperCard({
  item,
  guildId,
  onUpdate,
}: {
  item: AdminWallpaper;
  guildId: number;
  onUpdate: (wallpaper: AdminWallpaper) => void;
}) {
  const { t } = useTranslation();
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(item.name);
  const [price, setPrice] = useState(String(item.price));
  const [level, setLevel] = useState(String(item.level));
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const submitting = useRef(false);

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setBusy(true);
    setNotice("");
    try {
      const result = await GuildAdmin.request<AdminWallpaper>(
        guildId,
        `/wallpapers/${item.id}`,
        { name, price: Number(price), level: Number(level) },
        "PATCH",
      );
      onUpdate(result);
      setEditing(false);
      setNotice("admin.wallpaperSaved");
    } catch (error) {
      setNotice(
        error instanceof Error && error.message === "409"
          ? "admin.duplicate"
          : "admin.createError",
      );
    } finally {
      setBusy(false);
      submitting.current = false;
    }
  };

  return (
    <article className="admin-asset-card">
      <img
        src={item.url}
        alt={item.name}
        loading="lazy"
        className="admin-wallpaper-thumbnail"
      />
      {editing ? (
        <form
          className="admin-form wallpaper-edit-form"
          onSubmit={(event) => void save(event)}
        >
          <fieldset disabled={busy} className="admin-form-fields">
            <label>
              {t("admin.name")}
              <input
                required
                maxLength={80}
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </label>
            <label>
              {t("admin.price")}
              <input
                type="number"
                required
                min={0}
                max={1000000000}
                step={1}
                value={price}
                onChange={(event) => setPrice(event.target.value)}
              />
            </label>
            <label>
              {t("admin.level")}
              <input
                type="number"
                required
                min={0}
                max={1000000}
                step={1}
                value={level}
                onChange={(event) => setLevel(event.target.value)}
              />
            </label>
            <p className="admin-hint">{t("admin.wallpaperEditHint")}</p>
            {notice && (
              <p role="alert" className="admin-notice error">
                {t(notice)}
              </p>
            )}
            <div className="wallpaper-edit-actions">
              <button
                className="admin-button primary"
                disabled={busy || !name.trim()}
              >
                {t(busy ? "profile.saving" : "admin.saveChanges")}
              </button>
              <button
                type="button"
                className="admin-button secondary"
                disabled={busy}
                onClick={() => {
                  setEditing(false);
                  setNotice("");
                }}
              >
                {t("admin.cancel")}
              </button>
            </div>
          </fieldset>
        </form>
      ) : (
        <div className="admin-card-body">
          <h3>{item.name}</h3>
          <span className="admin-count">
            {item.price > 0
              ? t("profile.price", { count: item.price })
              : item.level > 0
                ? t("profile.unlockLevel", { count: item.level })
                : t("admin.exclusive")}
          </span>
          {item.price > 0 && item.level > 0 && (
            <span className="admin-count">
              {t("profile.unlockLevel", { count: item.level })}
            </span>
          )}
          <button
            type="button"
            className="admin-text-button"
            onClick={() => {
              setName(item.name);
              setPrice(String(item.price));
              setLevel(String(item.level));
              setNotice("");
              setEditing(true);
            }}
          >
            {t("admin.editWallpaper")} ↗
          </button>
          {notice && (
            <p role="status" className="admin-notice success">
              {t(notice)}
            </p>
          )}
        </div>
      )}
    </article>
  );
}
