import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { superRequest } from "../../../models/superadmin";
import type { Badge } from "../../../models/superadmin";

export default function SuperadminBadges() {
  const { t } = useTranslation();
  const [badges, setBadges] = useState<Badge[] | null>(null);
  const [name, setName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [editing, setEditing] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const submitting = useRef(false);
  const failure = (reason: unknown) =>
    setError(
      reason instanceof Error && ["401", "403"].includes(reason.message)
        ? "superadmin.badges.denied"
        : reason instanceof Error && reason.message === "409"
          ? "superadmin.badges.duplicate"
          : reason instanceof Error && reason.message === "413"
            ? "admin.imageTooLarge"
            : reason instanceof Error && reason.message === "422"
              ? "superadmin.badges.invalid"
              : "superadmin.badges.error",
    );
  useEffect(() => {
    let cancelled = false;
    superRequest<Badge[]>("/badges")
      .then((data) => {
        if (!cancelled) setBadges(data);
      })
      .catch((reason) => {
        if (!cancelled) failure(reason);
      });
    return () => {
      cancelled = true;
    };
  }, []);
  useEffect(() => {
    if (!file) {
      setPreview("");
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const reset = () => {
    setEditing(null);
    setName("");
    setFile(null);
  };
  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    if (submitting.current) return;
    if (file && file.size > 8 * 1024 * 1024) {
      setError("admin.imageTooLarge");
      return;
    }
    submitting.current = true;
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      let result: Badge;
      if (editing === null) {
        if (!file) throw new Error("422");
        const form = new FormData();
        form.append("name", name);
        form.append("image", file);
        result = await superRequest<Badge>("/badges", "POST", form);
      } else {
        if (file) {
          const form = new FormData();
          form.append("image", file);
          const image = await superRequest<Badge>(
            `/badges/${editing}/image`,
            "POST",
            form,
          );
          setBadges(
            (current) =>
              current?.map((badge) => (badge.id === editing ? image : badge)) ??
              null,
          );
        }
        result = await superRequest<Badge>(`/badges/${editing}`, "PATCH", {
          name,
        });
      }
      setBadges(
        (current) =>
          current &&
          (editing === null
            ? [...current, result]
            : current.map((badge) => (badge.id === editing ? result : badge))),
      );
      reset();
      setSaved(true);
    } catch (reason) {
      failure(reason);
    } finally {
      submitting.current = false;
      setBusy(false);
    }
  };
  const remove = async (badge: Badge) => {
    if (
      submitting.current ||
      !window.confirm(
        t("superadmin.badges.confirmDelete", { name: badge.name }),
      )
    )
      return;
    submitting.current = true;
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      await superRequest(`/badges/${badge.id}`, "DELETE");
      setBadges(
        (current) => current?.filter((item) => item.id !== badge.id) ?? null,
      );
      if (editing === badge.id) reset();
      setSaved(true);
    } catch (reason) {
      failure(reason);
    } finally {
      submitting.current = false;
      setBusy(false);
    }
  };

  return (
    <div className="admin-content">
      <div className="admin-section-title">
        <h2>{t("superadmin.badges.title")}</h2>
        <p>{t("superadmin.users.badgeCatalogHelp")}</p>
      </div>
      {error && (
        <p role="alert" className="admin-panel admin-notice error">
          {t(error)}
        </p>
      )}
      {saved && (
        <p role="status" className="admin-panel admin-notice success">
          {t("superadmin.badges.saved")}
        </p>
      )}
      {!badges ? (
        !error && (
          <p role="status" className="admin-panel">
            {t("admin.loading")}
          </p>
        )
      ) : (
        <>
          <div className="admin-editor-grid">
            <form
              className="admin-panel admin-form"
              onSubmit={(event) => void save(event)}
            >
              <h3>
                {t(
                  editing === null
                    ? "superadmin.badges.new"
                    : "superadmin.badges.edit",
                )}
              </h3>
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
                  {t("superadmin.badges.image")}
                  <input
                    key={editing ?? "new"}
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    onChange={(event) =>
                      setFile(event.target.files?.[0] ?? null)
                    }
                  />
                  <span className="admin-hint">
                    {t("superadmin.badges.imageHelp")}
                  </span>
                </label>
                <button
                  className="admin-button primary"
                  disabled={busy || !name.trim()}
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
            <div className="admin-panel badge-preview">
              <span className="admin-eyebrow">{t("admin.livePreview")}</span>
              {preview || badges.find((badge) => badge.id === editing)?.url ? (
                <img
                  src={
                    preview || badges.find((badge) => badge.id === editing)?.url
                  }
                  alt={name}
                />
              ) : (
                <span className="badge-placeholder">✦</span>
              )}
              <h3>{name || t("superadmin.badges.new")}</h3>
            </div>
          </div>
          <div className="admin-card-grid">
            {badges.length === 0 && (
              <p className="admin-panel admin-empty">
                {t("superadmin.badges.empty")}
              </p>
            )}
            {badges.map((badge) => (
              <article key={badge.id} className="admin-panel badge-card">
                <img src={badge.url} alt={badge.name} />
                <h3>{badge.name}</h3>
                <div className="wallpaper-edit-actions">
                  <button
                    className="admin-text-button"
                    disabled={busy}
                    onClick={() => {
                      setEditing(badge.id);
                      setName(badge.name);
                      setFile(null);
                      window.scrollTo({ top: 0, behavior: "smooth" });
                    }}
                  >
                    {t("superadmin.badges.edit")}
                  </button>
                  <button
                    className="role-remove-button"
                    disabled={busy}
                    onClick={() => void remove(badge)}
                  >
                    {t("superadmin.badges.delete")}
                  </button>
                </div>
              </article>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
