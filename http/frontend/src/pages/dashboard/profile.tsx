import React, { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import ShowProfile from "../../components/profile-editor/show";
import Loading from "../../components/loading";
import { Guild } from "../../models/guild";
import {
  Profile as ProfileAPI,
  ProfileChanges,
  ProfileData,
} from "../../models/profile";

const Profile: React.FC = () => {
  const { t } = useTranslation();
  const [data, setData] = useState<ProfileData | null>(null);
  const [draft, setDraft] = useState<ProfileChanges | null>(null);
  const [guildId, setGuildId] = useState<number | null>(null);
  const [previewId, setPreviewId] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [guildRevision, setGuildRevision] = useState(0);
  const requestRevision = useRef(0);
  const lastSaved = useRef("");
  const lastAttempt = useRef("");

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
  }, [draft, guildId, busy, saving, guildRevision]);

  const pending = draft !== null && JSON.stringify(draft) !== lastSaved.current;

  useEffect(() => {
    if (!pending && !saving) return;
    const warn = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [pending, saving]);

  const buy = async (id: number) => {
    if (guildId === null) return;
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
      if (revision === requestRevision.current) setBusy(false);
    }
  };

  if (!data || !draft) {
    return error ? (
      <p role="alert" className="p-6">
        {t(error)}
      </p>
    ) : (
      <Loading />
    );
  }

  const layout =
    data.layouts.find((item) => item.id === draft.layout_id) ??
    data.default_layout;
  const wallpaper = data.wallpapers.find(
    (item) => item.id === (previewId ?? draft.wallpaper_id),
  );

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">{t("profile.title")}</h1>
      {error && (
        <p role="alert" className="text-red-700">
          {t(error)}
        </p>
      )}
      {(saving || (pending && !error) || message) && (
        <p role="status" className="text-green-700">
          {t(saving || (pending && !error) ? "profile.saving" : message)}
        </p>
      )}
      <div className="overflow-x-auto">
        <ShowProfile
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
      {previewId !== null && (
        <p>
          {t("profile.previewOnly")}{" "}
          <button className="underline" onClick={() => setPreviewId(null)}>
            {t("profile.stopPreview")}
          </button>
        </p>
      )}
      <fieldset disabled={busy} className="space-y-4 disabled:opacity-60">
        <div className="flex flex-wrap gap-6">
          <label className="flex items-center gap-2">
            {t("profile.nameColor")}
            <input
              type="color"
              value={draft.name_color}
              onChange={(event) =>
                setDraft({ ...draft, name_color: event.target.value })
              }
            />
          </label>
          <label className="flex items-center gap-2">
            {t("profile.barColor")}
            <input
              type="color"
              value={draft.bar_color}
              onChange={(event) =>
                setDraft({ ...draft, bar_color: event.target.value })
              }
            />
          </label>
          <label>
            {t("profile.layout")}
            <select
              className="border rounded p-2 ml-2"
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
          </label>
        </div>
        <label>
          {t("profile.wallpaper")}
          <select
            className="border rounded p-2 ml-2"
            value={draft.wallpaper_id ?? ""}
            onChange={(event) => {
              setDraft({
                ...draft,
                wallpaper_id: event.target.value
                  ? Number(event.target.value)
                  : null,
              });
              setPreviewId(null);
            }}
          >
            <option value="">{t("profile.default")}</option>
            {data.wallpapers
              .filter((item) => item.owned)
              .map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
          </select>
        </label>
        <h2 className="text-2xl font-bold">{t("profile.wallpapers")}</h2>
        <p>{t("profile.balance", { count: data.user.smartpoint })}</p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.wallpapers.map((item) => (
            <article key={item.id} className="border rounded p-3 space-y-2">
              <img
                src={item.url}
                alt={item.name}
                className="w-full aspect-video object-cover rounded"
                loading="lazy"
              />
              <h3 className="font-bold">{item.name}</h3>
              <p>
                {item.owned
                  ? t("profile.owned")
                  : item.price > 0
                    ? t("profile.price", { count: item.price })
                    : item.level > 0
                      ? t("profile.unlockLevel", { count: item.level })
                      : t("profile.unavailable")}
              </p>
              <div className="flex gap-3">
                <button
                  className="underline"
                  onClick={() => setPreviewId(item.id)}
                >
                  {t("profile.preview")}
                </button>
                {item.owned ? (
                  <button
                    className="underline"
                    onClick={() => {
                      setDraft({ ...draft, wallpaper_id: item.id });
                      setPreviewId(null);
                    }}
                  >
                    {t("profile.select")}
                  </button>
                ) : (
                  item.price > 0 && (
                    <button
                      className="underline disabled:opacity-40"
                      disabled={
                        item.price > data.user.smartpoint || saving || pending
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
                      {t("profile.buy")}
                    </button>
                  )
                )}
              </div>
            </article>
          ))}
        </div>
      </fieldset>
    </div>
  );
};

export default Profile;
