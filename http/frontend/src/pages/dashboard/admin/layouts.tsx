import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useGuildAdmin } from "./context";
import { GuildAdmin } from "../../../models/guild-admin";
import type { ProfileLayout } from "../../../models/profile";
import LayoutCanvas from "../../../components/profile-editor/layout-canvas";
import ShowProfile from "../../../components/profile-editor/show";

export default function AdminLayouts() {
  const { t } = useTranslation();
  const { guildId, data, setData } = useGuildAdmin();
  const [draft, setDraft] = useState<ProfileLayout>({
    ...data.default_layout,
    name: "",
  });
  const [background, setBackground] = useState(data.default_wallpaper);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const submitting = useRef(false);

  const create = async (event: React.FormEvent) => {
    event.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setBusy(true);
    setNotice("");
    try {
      const { id: _id, ...changes } = draft;
      void _id;
      const result = await GuildAdmin.request<ProfileLayout>(
        guildId,
        "/layouts",
        changes,
      );
      setData(
        (current) =>
          current && { ...current, layouts: [...current.layouts, result] },
      );
      setDraft((current) => ({ ...current, name: "" }));
      setNotice("admin.created");
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
    <div className="admin-content">
      <div className="admin-section-title">
        <div>
          <h2>{t("admin.layoutTitle")}</h2>
          <p>{t("admin.layoutDescription")}</p>
        </div>
        <span className="admin-count">
          {data.layouts.length} {t("admin.layouts")}
        </span>
      </div>
      <div className="admin-editor-grid">
        <div className="admin-panel admin-canvas-panel">
          <div className="admin-panel-heading">
            <span className="admin-eyebrow">{t("admin.livePreview")}</span>
            <span className="admin-dimensions">500 × 281</span>
          </div>
          <fieldset disabled={busy}>
            <LayoutCanvas
              layout={draft}
              background={background}
              onChange={setDraft}
            />
          </fieldset>
        </div>
        <form
          className="admin-panel admin-form"
          onSubmit={(event) => void create(event)}
        >
          <h3>{t("admin.newLayout")}</h3>
          <p>{t("admin.layoutHelp")}</p>
          <label>
            {t("admin.name")}
            <input
              required
              maxLength={80}
              value={draft.name}
              onChange={(event) =>
                setDraft({ ...draft, name: event.target.value })
              }
              placeholder={t("admin.layoutPlaceholder")}
              disabled={busy}
            />
          </label>
          <label>
            {t("admin.previewBackground")}
            <select
              value={background}
              onChange={(event) => setBackground(event.target.value)}
            >
              <option value={data.default_wallpaper}>
                {t("profile.default")}
              </option>
              {data.wallpapers.map((item) => (
                <option key={item.id} value={item.url}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
          <div className="admin-info">✦ {t("admin.guildOnly")}</div>
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
            disabled={busy || !draft.name.trim()}
          >
            {t(busy ? "admin.creating" : "admin.createLayout")}
          </button>
          <button
            className="admin-button secondary"
            type="button"
            disabled={busy}
            onClick={() =>
              setDraft({ ...data.default_layout, name: draft.name })
            }
          >
            {t("admin.resetPositions")}
          </button>
        </form>
      </div>
      <div className="admin-section-title">
        <h2>{t("admin.savedLayouts")}</h2>
      </div>
      <div className="admin-card-grid">
        {data.layouts.length === 0 && (
          <div className="admin-panel admin-empty">
            <span>▦</span>
            <h3>{t("admin.emptyLayouts")}</h3>
            <p>{t("admin.emptyLayoutsHelp")}</p>
          </div>
        )}
        {data.layouts.map((layout) => (
          <article className="admin-asset-card" key={layout.id}>
            <div className="admin-layout-thumbnail">
              <ShowProfile
                {...layout}
                background={background}
                displayName="Capitaine Hydromel"
                username="compagnie"
                name_color="#fff4d4"
                bar_color="#edbd68"
              />
            </div>
            <div className="admin-card-body">
              <h3>{layout.name}</h3>
              <button
                type="button"
                className="admin-text-button"
                onClick={() => {
                  setDraft({
                    ...layout,
                    id: null,
                    name: `${layout.name} — copie`,
                  });
                  setNotice("");
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
              >
                {t("admin.useAsTemplate")} ↗
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
