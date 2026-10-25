import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useGuildAdmin } from "./context";
import { GuildAdmin } from "../../../models/guild-admin";
import WallpaperCard from "./wallpaper-card";

export default function AdminWallpapers() {
  const { t } = useTranslation();
  const { guildId, data, setData } = useGuildAdmin();
  const [name, setName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState("");
  const [dragging, setDragging] = useState(false);
  const [price, setPrice] = useState(100);
  const [level, setLevel] = useState(1);
  const [unlock, setUnlock] = useState("price");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [failedUrl, setFailedUrl] = useState("");
  const submitting = useRef(false);
  const fileInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!file) {
      setImageUrl("");
      return;
    }
    const preview = URL.createObjectURL(file);
    setImageUrl(preview);
    return () => URL.revokeObjectURL(preview);
  }, [file]);

  const chooseImage = (selected: File | undefined) => {
    if (busy || !selected) return;
    setNotice("");
    setFailedUrl("");
    if (selected.size > 8 * 1024 * 1024) {
      setNotice("admin.imageTooLarge");
      setFile(null);
    } else if (
      selected.type &&
      !["image/png", "image/jpeg", "image/webp"].includes(selected.type)
    ) {
      setNotice("admin.invalidImage");
      setFile(null);
    } else {
      setFile(selected);
    }
  };

  const create = async (event: React.FormEvent) => {
    event.preventDefault();
    if (submitting.current || !file) return;
    submitting.current = true;
    setBusy(true);
    setNotice("");
    try {
      const form = new FormData();
      form.append("name", name);
      form.append("price", String(unlock === "price" ? price : 0));
      form.append("level", String(unlock === "level" ? level : 0));
      form.append("image", file);
      const wallpaper = await GuildAdmin.uploadWallpaper(guildId, form);
      setData(
        (current) =>
          current && {
            ...current,
            wallpapers: [...current.wallpapers, wallpaper],
          },
      );
      setName("");
      setFile(null);
      if (fileInput.current) fileInput.current.value = "";
      setNotice("admin.created");
    } catch (error) {
      setNotice(
        error instanceof Error && error.message === "409"
          ? "admin.duplicate"
          : error instanceof Error && error.message === "413"
            ? "admin.imageTooLarge"
            : error instanceof Error && error.message === "422"
              ? "admin.invalidImage"
              : "admin.createError",
      );
    } finally {
      setBusy(false);
      submitting.current = false;
    }
  };

  return (
    <div className="admin-content">
      <div className="admin-section-title">
        <div>
          <h2>{t("admin.wallpaperTitle")}</h2>
          <p>{t("admin.wallpaperDescription")}</p>
        </div>
        <span className="admin-count">
          {data.wallpapers.length} {t("admin.wallpapers")}
        </span>
      </div>
      <div className="admin-editor-grid">
        <div className="admin-panel admin-canvas-panel">
          <div className="admin-panel-heading">
            <span className="admin-eyebrow">{t("admin.livePreview")}</span>
            <span className="admin-dimensions">500 × 281</span>
          </div>
          <label
            htmlFor="wallpaper-image"
            className={`wallpaper-upload-preview wallpaper-dropzone ${dragging ? "dragging" : ""}`}
            role="button"
            tabIndex={busy ? -1 : 0}
            aria-label={t("admin.imageFile")}
            aria-disabled={busy}
            onKeyDown={(event) => {
              if (!busy && (event.key === "Enter" || event.key === " ")) {
                event.preventDefault();
                fileInput.current?.click();
              }
            }}
            onDragOver={(event) => {
              event.preventDefault();
              if (!busy) setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(event) => {
              event.preventDefault();
              setDragging(false);
              chooseImage(event.dataTransfer.files[0]);
            }}
          >
            {imageUrl && failedUrl !== imageUrl ? (
              <img
                src={imageUrl}
                alt={name || t("admin.wallpaperPreview")}
                onError={() => setFailedUrl(imageUrl)}
                draggable={false}
              />
            ) : (
              <div className="admin-empty">
                <span>▧</span>
                <h3>
                  {t(imageUrl ? "admin.imageError" : "admin.imagePlaceholder")}
                </h3>
                <p>{t("admin.imageHint")}</p>
              </div>
            )}
          </label>
          {file && (
            <p className="admin-hint">
              {file.name} · {(file.size / (1024 * 1024)).toFixed(2)} MiB
            </p>
          )}
          <p className="admin-hint">✦ {t("admin.imageDimensions")}</p>
        </div>
        <form
          className="admin-panel admin-form"
          onSubmit={(event) => void create(event)}
        >
          <h3>{t("admin.newWallpaper")}</h3>
          <fieldset disabled={busy} className="admin-form-fields">
            <label>
              {t("admin.name")}
              <input
                required
                maxLength={80}
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder={t("admin.wallpaperPlaceholder")}
              />
            </label>
            <label>
              {t("admin.imageFile")}
              <input
                id="wallpaper-image"
                ref={fileInput}
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={(event) => chooseImage(event.target.files?.[0])}
              />
              <span className="admin-hint">{t("admin.imageFormats")}</span>
            </label>
            <label>
              {t("admin.unlock")}
              <select
                value={unlock}
                onChange={(event) => setUnlock(event.target.value)}
              >
                <option value="price">{t("admin.unlockPrice")}</option>
                <option value="level">{t("admin.unlockLevel")}</option>
                <option value="exclusive">{t("admin.unlockExclusive")}</option>
              </select>
            </label>
            {unlock === "price" && (
              <label>
                {t("admin.price")}
                <input
                  type="number"
                  required
                  min={1}
                  max={1000000000}
                  value={price}
                  onChange={(event) => setPrice(Number(event.target.value))}
                />
              </label>
            )}
            {unlock === "level" && (
              <label>
                {t("admin.level")}
                <input
                  type="number"
                  required
                  min={1}
                  max={1000000}
                  value={level}
                  onChange={(event) => setLevel(Number(event.target.value))}
                />
              </label>
            )}
            <div className="admin-info">
              {t(
                unlock === "level"
                  ? "admin.levelHelp"
                  : unlock === "exclusive"
                    ? "admin.exclusiveHelp"
                    : "admin.priceHelp",
              )}
            </div>
            {notice && (
              <p
                role={notice === "admin.created" ? "status" : "alert"}
                className={`admin-notice ${notice === "admin.created" ? "success" : "error"}`}
              >
                {t(notice)}
              </p>
            )}
            <button
              className="admin-button primary"
              disabled={
                busy ||
                !name.trim() ||
                !file ||
                !imageUrl ||
                failedUrl === imageUrl
              }
            >
              {t(busy ? "admin.creating" : "admin.createWallpaper")}
            </button>
          </fieldset>
        </form>
      </div>
      <div className="admin-section-title">
        <h2>{t("admin.gallery")}</h2>
      </div>
      <div className="admin-card-grid">
        {data.wallpapers.length === 0 && (
          <div className="admin-panel admin-empty">
            <span>▧</span>
            <h3>{t("admin.emptyWallpapers")}</h3>
            <p>{t("admin.emptyWallpapersHelp")}</p>
          </div>
        )}
        {data.wallpapers.map((item) => (
          <WallpaperCard
            key={item.id}
            item={item}
            guildId={guildId}
            onUpdate={(updated) =>
              setData(
                (current) =>
                  current && {
                    ...current,
                    wallpapers: current.wallpapers.map((wallpaper) =>
                      wallpaper.id === updated.id ? updated : wallpaper,
                    ),
                  },
              )
            }
          />
        ))}
      </div>
    </div>
  );
}
