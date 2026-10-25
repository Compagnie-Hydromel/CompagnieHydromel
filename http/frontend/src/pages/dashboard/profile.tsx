import { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import ResponsiveProfilePreview from "../../components/profile-editor/responsive-preview";
import { Guild } from "../../models/guild";
import { Profile as ProfileAPI } from "../../models/profile";
import type { ProfileChanges, ProfileData } from "../../models/profile";

const Profile = () => {
  const { t, i18n } = useTranslation();
  const [data, setData] = useState<ProfileData | null>(null);
  const [draft, setDraft] = useState<ProfileChanges | null>(null);
  const [guildId, setGuildId] = useState<number | null>(null);
  const [previewId, setPreviewId] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [guildRevision, setGuildRevision] = useState(0);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [retry, setRetry] = useState(0);
  const requestRevision = useRef(0);
  const lastSaved = useRef("");
  const lastAttempt = useRef("");
  const purchaseInFlight = useRef(false);
  const previewSection = useRef<HTMLElement>(null);

  useEffect(() => {
    const changed = () => {
      requestRevision.current += 1;
      setGuildRevision((value) => value + 1);
    };
    window.addEventListener("guild-changed", changed);
    return () => window.removeEventListener("guild-changed", changed);
  }, []);

  const apply = (profile: ProfileData) => {
    setData(profile);
    const changes = {
      name_color: profile.user.name_color,
      bar_color: profile.user.bar_color,
      wallpaper_id: profile.wallpaper_id,
      layout_id: profile.layout_id,
    };
    lastSaved.current = JSON.stringify(changes);
    lastAttempt.current = lastSaved.current;
    setDraft(changes);
    setPreviewId(null);
  };

  useEffect(() => {
    let cancelled = false;
    setData(null);
    setDraft(null);
    setError("");
    setMessage("");
    setBusy(false);
    setSaving(false);
    setSearch("");
    setFilter("all");
    const load = async () => {
      try {
        const guild = await Guild.currentlySelectedGuild();
        if (!guild) throw new Error("noGuild");
        const id = Number(guild.get("id"));
        const profile = await ProfileAPI.requestProfile(id);
        if (!cancelled) {
          setGuildId(id);
          apply(profile);
        }
      } catch {
        if (!cancelled) setError("profile.loadError");
      }
    };
    void load();
    return () => {
      cancelled = true;
      requestRevision.current += 1;
    };
  }, [guildRevision]);

  useEffect(() => {
    if (!draft || guildId === null || busy || saving) return;
    const signature = JSON.stringify(draft);
    if (signature === lastSaved.current || signature === lastAttempt.current)
      return;
    const revision = requestRevision.current;
    const timer = window.setTimeout(async () => {
      lastAttempt.current = signature;
      setSaving(true);
      setError("");
      setMessage("");
      try {
        const profile = await ProfileAPI.requestProfile(
          guildId,
          "PATCH",
          draft,
        );
        if (revision !== requestRevision.current) return;
        lastSaved.current = signature;
        setData(profile);
        setMessage("profile.saved");
      } catch {
        if (revision === requestRevision.current) setError("profile.saveError");
      } finally {
        if (revision === requestRevision.current) setSaving(false);
      }
    }, 400);
    return () => window.clearTimeout(timer);
  }, [draft, guildId, busy, saving, guildRevision, retry]);

  const pending = draft !== null && JSON.stringify(draft) !== lastSaved.current;
  useEffect(() => {
    if (!pending && !saving) return;
    const warn = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [pending, saving]);

  const buy = async (id: number) => {
    if (guildId === null || purchaseInFlight.current || saving || pending)
      return;
    purchaseInFlight.current = true;
    const revision = requestRevision.current;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const profile = await ProfileAPI.requestProfile(
        guildId,
        "POST",
        undefined,
        `/wallpapers/${id}/buy`,
      );
      if (revision !== requestRevision.current) return;
      setData(profile);
      setMessage("profile.bought");
    } catch {
      if (revision === requestRevision.current) setError("profile.buyError");
    } finally {
      purchaseInFlight.current = false;
      if (revision === requestRevision.current) setBusy(false);
    }
  };

  const retrySave = () => {
    lastAttempt.current = "";
    setError("");
    setRetry((value) => value + 1);
  };
  const reload = () => setGuildRevision((value) => value + 1);
  if (!data || !draft)
    return (
      <div className="profile-studio">
        <div
          className="profile-panel profile-loading"
          role={error ? "alert" : "status"}
        >
          <span aria-hidden="true">✦</span>
          <h1>{t("profile.title")}</h1>
          <p>{t(error || "profile.loading")}</p>
          {error && (
            <button className="profile-button secondary" onClick={reload}>
              {t("profile.retry")}
            </button>
          )}
        </div>
      </div>
    );

  const numbers = new Intl.NumberFormat(i18n.language);
  const layout =
    data.layouts.find((item) => item.id === draft.layout_id) ??
    data.default_layout;
  const wallpaper = data.wallpapers.find(
    (item) => item.id === (previewId ?? draft.wallpaper_id),
  );
  const owned = data.wallpapers.filter((item) => item.owned);
  const gallery = data.wallpapers.filter(
    (item) =>
      item.name
        .toLocaleLowerCase()
        .includes(search.trim().toLocaleLowerCase()) &&
      (filter === "all" ||
        (filter === "owned" ? item.owned : !item.owned && item.price > 0)),
  );
  const status =
    error === "profile.saveError"
      ? "profile.saveFailed"
      : saving || pending
        ? "profile.saving"
        : "profile.autosaved";
  const selectWallpaper = (id: number | null) => {
    setDraft({ ...draft, wallpaper_id: id });
    setPreviewId(null);
  };
  const previewWallpaper = (id: number) => {
    setPreviewId(id);
    previewSection.current?.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  };

  return (
    <div className="profile-studio">
      <header className="profile-studio-heading">
        <div>
          <p className="profile-eyebrow">{t("profile.studioEyebrow")}</p>
          <h1>{t("profile.title")}</h1>
          <p className="profile-subtitle">{t("profile.studioSubtitle")}</p>
        </div>
        <div
          className={`profile-save-status ${error === "profile.saveError" ? "failed" : saving || pending ? "saving" : ""}`}
          role="status"
        >
          <span aria-hidden="true">
            {error === "profile.saveError"
              ? "!"
              : saving || pending
                ? "◌"
                : "✓"}
          </span>
          {t(status)}
        </div>
      </header>
      {error && (
        <div className="profile-alert error" role="alert">
          <p>{t(error)}</p>
          {error === "profile.saveError" && (
            <button onClick={retrySave}>{t("profile.retry")}</button>
          )}
        </div>
      )}
      {message === "profile.bought" && (
        <div className="profile-alert success" role="status">
          {t(message)}
        </div>
      )}
      <div className="profile-editor-grid">
        <section
          ref={previewSection}
          className="profile-panel profile-preview-panel"
        >
          <div className="profile-section-heading">
            <div>
              <p className="profile-eyebrow">{t("profile.livePreview")}</p>
              <h2>{t("profile.yourCard")}</h2>
            </div>
            <span
              className={`profile-tag ${previewId !== null ? "preview" : ""}`}
            >
              {t(
                previewId !== null ? "profile.preview" : "profile.currentLook",
              )}
            </span>
          </div>
          <div className="profile-preview-stage">
            <ResponsiveProfilePreview
              {...layout}
              background={wallpaper?.url ?? data.default_wallpaper}
              avatar={data.user.avatar_url}
              displayName={data.user.display_name}
              username={data.user.username}
              level={data.user.level}
              badges={data.user.badges}
              progress={data.user.progress * 100}
              name_color={draft.name_color}
              bar_color={draft.bar_color}
            />
          </div>
          <div className="profile-card-caption">
            <span>◈ {wallpaper?.name ?? t("profile.default")}</span>
            <span>
              ▦ {draft.layout_id === null ? t("profile.default") : layout.name}
            </span>
          </div>
          {previewId !== null ? (
            <div className="profile-preview-notice">
              <p>{t("profile.previewOnly")}</p>
              <button onClick={() => setPreviewId(null)}>
                {t("profile.stopPreview")} ×
              </button>
            </div>
          ) : (
            <p className="profile-preview-hint">{t("profile.previewHint")}</p>
          )}
          <div className="profile-mini-stats">
            <div>
              <span>✦</span>
              <strong>{numbers.format(data.user.level)}</strong>
              <small>{t("profile.levelLabel")}</small>
            </div>
            <div>
              <span>◈</span>
              <strong>{owned.length}</strong>
              <small>{t("profile.collectionLabel")}</small>
            </div>
            <div>
              <span>♜</span>
              <strong>{data.user.badges.length}</strong>
              <small>{t("profile.badgesLabel")}</small>
            </div>
          </div>
        </section>
        <section className="profile-panel profile-settings">
          <div className="profile-section-heading">
            <div>
              <p className="profile-eyebrow">{t("profile.makeItYours")}</p>
              <h2>{t("profile.appearance")}</h2>
            </div>
            <span aria-hidden="true" className="profile-section-icon">
              ✧
            </span>
          </div>
          <fieldset disabled={busy}>
            <div className="profile-color-grid">
              {(["name_color", "bar_color"] as const).map((key) => (
                <label key={key} className="profile-color-control">
                  <span>
                    {t(
                      key === "name_color"
                        ? "profile.nameColor"
                        : "profile.barColor",
                    )}
                  </span>
                  <div>
                    <input
                      type="color"
                      value={draft[key]}
                      onChange={(event) =>
                        setDraft({ ...draft, [key]: event.target.value })
                      }
                    />
                    <code>{draft[key].toUpperCase()}</code>
                  </div>
                </label>
              ))}
            </div>
            <label className="profile-select-label">
              <span>▦ {t("profile.layout")}</span>
              <select
                value={draft.layout_id ?? ""}
                onChange={(event) =>
                  setDraft({
                    ...draft,
                    layout_id: event.target.value
                      ? Number(event.target.value)
                      : null,
                  })
                }
              >
                <option value="">{t("profile.default")}</option>
                {data.layouts.map((item) => (
                  <option key={item.id} value={item.id ?? ""}>
                    {item.name}
                  </option>
                ))}
              </select>
              <small>{t("profile.layoutHint")}</small>
            </label>
            <label className="profile-select-label">
              <span>◈ {t("profile.wallpaper")}</span>
              <select
                value={draft.wallpaper_id ?? ""}
                onChange={(event) =>
                  selectWallpaper(
                    event.target.value ? Number(event.target.value) : null,
                  )
                }
              >
                <option value="">{t("profile.default")}</option>
                {owned.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </label>
            <p className="profile-autosave-hint">
              ✓ {t("profile.autosaveHint")}
            </p>
          </fieldset>
        </section>
      </div>
      <section className="profile-panel profile-gallery-section">
        <div className="profile-section-heading">
          <div>
            <p className="profile-eyebrow">{t("profile.galleryEyebrow")}</p>
            <h2>{t("profile.wallpapers")}</h2>
            <p className="profile-subtitle">{t("profile.galleryHint")}</p>
          </div>
          <div className="profile-wallet">
            <span aria-hidden="true">◈</span>
            <div>
              <small>{t("profile.wallet")}</small>
              <strong>
                {numbers.format(data.user.smartpoint)} <span>smartpoints</span>
              </strong>
            </div>
          </div>
        </div>
        <div className="profile-gallery-toolbar">
          <div
            className="profile-filter-tabs"
            role="group"
            aria-label={t("profile.filterLabel")}
          >
            {["all", "owned", "shop"].map((tab) => (
              <button
                key={tab}
                aria-pressed={filter === tab}
                className={filter === tab ? "active" : ""}
                onClick={() => setFilter(tab)}
              >
                {t(`profile.filters.${tab}`)}
                <span>
                  {tab === "all"
                    ? data.wallpapers.length
                    : tab === "owned"
                      ? owned.length
                      : data.wallpapers.filter(
                          (item) => !item.owned && item.price > 0,
                        ).length}
                </span>
              </button>
            ))}
          </div>
          <label className="profile-gallery-search">
            <span aria-hidden="true">⌕</span>
            <input
              type="search"
              maxLength={100}
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder={t("profile.searchWallpapers")}
              aria-label={t("profile.searchWallpapers")}
            />
          </label>
        </div>
        {gallery.length === 0 ? (
          <div className="profile-gallery-empty">
            <span aria-hidden="true">◈</span>
            <h3>
              {t(
                data.wallpapers.length === 0
                  ? "profile.emptyGallery"
                  : "profile.noResults",
              )}
            </h3>
            <p>
              {t(
                data.wallpapers.length === 0
                  ? "profile.emptyGalleryHint"
                  : "profile.noResultsHint",
              )}
            </p>
            {data.wallpapers.length > 0 && (
              <button
                className="profile-button secondary"
                onClick={() => {
                  setFilter("all");
                  setSearch("");
                }}
              >
                {t("profile.clearFilters")}
              </button>
            )}
          </div>
        ) : (
          <div className="profile-wallpaper-grid">
            {gallery.map((item) => {
              const equipped = item.id === draft.wallpaper_id;
              const previewing = item.id === previewId;
              const tooExpensive = item.price > data.user.smartpoint;
              return (
                <article
                  key={item.id}
                  className={`profile-wallpaper-card ${equipped ? "equipped" : ""} ${previewing ? "previewing" : ""}`}
                >
                  <div className="profile-wallpaper-image">
                    <img src={item.url} alt={item.name} loading="lazy" />
                    <span
                      className={`profile-wallpaper-badge ${equipped ? "equipped" : item.owned ? "owned" : ""}`}
                    >
                      {equipped
                        ? `✓ ${t("profile.equipped")}`
                        : item.owned
                          ? `✓ ${t("profile.owned")}`
                          : item.price > 0
                            ? `◈ ${numbers.format(item.price)}`
                            : item.level > 0
                              ? `✦ ${t("profile.unlockLevel", { count: item.level })}`
                              : t("profile.unavailable")}
                    </span>
                  </div>
                  <div className="profile-wallpaper-body">
                    <h3>{item.name}</h3>
                    <p>
                      {equipped
                        ? t("profile.equippedHint")
                        : item.owned
                          ? t("profile.ownedHint")
                          : item.price > 0
                            ? t("profile.price", { count: item.price })
                            : item.level > 0
                              ? t("profile.unlockLevel", { count: item.level })
                              : t("profile.unavailable")}
                    </p>
                    <div className="profile-wallpaper-actions">
                      <button
                        className="profile-button secondary"
                        aria-pressed={previewing}
                        onClick={() => previewWallpaper(item.id)}
                      >
                        {t("profile.preview")}
                      </button>
                      {item.owned ? (
                        <button
                          className="profile-button primary"
                          disabled={busy || equipped}
                          onClick={() => selectWallpaper(item.id)}
                        >
                          {t(equipped ? "profile.equipped" : "profile.select")}
                        </button>
                      ) : item.price > 0 ? (
                        <button
                          className="profile-button primary"
                          disabled={busy || tooExpensive || saving || pending}
                          title={
                            tooExpensive
                              ? t("profile.insufficientFunds")
                              : undefined
                          }
                          onClick={() => {
                            if (
                              window.confirm(
                                t("profile.confirmBuy", {
                                  name: item.name,
                                  count: item.price,
                                }),
                              )
                            )
                              void buy(item.id);
                          }}
                        >
                          {t(busy ? "profile.working" : "profile.buy")}
                        </button>
                      ) : (
                        <span className="profile-locked-label">
                          {t("profile.locked")}
                        </span>
                      )}
                    </div>
                    {!item.owned && item.price > 0 && tooExpensive && (
                      <small className="profile-funds-hint">
                        {t("profile.insufficientFunds")}
                      </small>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
};

export default Profile;
