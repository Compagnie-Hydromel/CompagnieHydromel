import { useEffect, useRef, useState } from "react";
import { superRequest } from "../../../models/superadmin";

interface Radio {
  id: number;
  slug: string;
  name: string;
  url: string;
}

export default function SuperadminRadios() {
  const [radios, setRadios] = useState<Radio[] | null>(null);
  const [editing, setEditing] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const submitting = useRef(false);

  const failure = (reason: unknown) =>
    setError(
      reason instanceof Error && ["401", "403"].includes(reason.message)
        ? "Accès réservé au superadmin."
        : reason instanceof Error && reason.message === "409"
          ? "Une radio porte déjà ce nom."
          : reason instanceof Error && reason.message === "422"
            ? "Vérifiez le nom et l’URL publique du flux HTTP(S), sans identifiants ni adresse privée."
            : "Impossible de gérer les radios. Vérifiez la connexion et les migrations.",
    );

  useEffect(() => {
    let cancelled = false;
    superRequest<Radio[]>("/radios")
      .then((data) => {
        if (!cancelled) setRadios(data);
      })
      .catch((reason) => {
        if (!cancelled) failure(reason);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const reset = () => {
    setEditing(null);
    setName("");
    setUrl("");
  };
  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      const radio = await superRequest<Radio>(
        editing === null ? "/radios" : `/radios/${editing}`,
        editing === null ? "POST" : "PATCH",
        { name, url },
      );
      setRadios(
        (current) =>
          current &&
          (editing === null
            ? [...current, radio]
            : current.map((item) => (item.id === editing ? radio : item))),
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
  const remove = async (radio: Radio) => {
    if (
      submitting.current ||
      !window.confirm(`Supprimer la radio « ${radio.name} » ?`)
    )
      return;
    submitting.current = true;
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      await superRequest(`/radios/${radio.id}`, "DELETE");
      setRadios(
        (current) => current?.filter((item) => item.id !== radio.id) ?? null,
      );
      if (editing === radio.id) reset();
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
        <h2>Radios du Ménestrel</h2>
        <p>
          Catalogue global proposé aux utilisateurs sur le web et Discord. Seul
          le superadmin peut le modifier.
        </p>
      </div>
      {error && (
        <p role="alert" className="admin-panel admin-notice error">
          {error}
        </p>
      )}
      {saved && (
        <p role="status" className="admin-panel admin-notice success">
          Catalogue enregistré.
        </p>
      )}
      {radios === null ? (
        !error && (
          <p role="status" className="admin-panel">
            Chargement…
          </p>
        )
      ) : (
        <>
          <form
            className="admin-panel admin-form"
            onSubmit={(event) => void save(event)}
          >
            <h3>
              {editing === null ? "Ajouter une radio" : "Modifier la radio"}
            </h3>
            <fieldset disabled={busy} className="admin-form-fields">
              <label>
                Nom
                <input
                  required
                  maxLength={80}
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                />
              </label>
              <label>
                URL du flux
                <input
                  required
                  type="url"
                  maxLength={255}
                  value={url}
                  onChange={(event) => setUrl(event.target.value)}
                  placeholder="https://radio.example/live.mp3"
                />
                <span className="admin-hint">
                  Flux audio direct, pas une page web. N’ajoutez que des sources
                  et redirections de confiance : le bot s’y connectera depuis
                  son réseau.
                </span>
              </label>
              <button
                className="admin-button primary"
                disabled={busy || !name.trim() || !url.trim()}
              >
                {busy ? "Enregistrement…" : "Enregistrer"}
              </button>
              {editing !== null && (
                <button
                  type="button"
                  className="admin-button secondary"
                  onClick={reset}
                >
                  Annuler
                </button>
              )}
            </fieldset>
          </form>
          <div className="admin-card-grid">
            {radios.length === 0 && (
              <p className="admin-panel admin-empty">
                Aucune radio. Ajoutez votre première station.
              </p>
            )}
            {radios.map((radio) => (
              <article key={radio.id} className="admin-panel">
                <h3>{radio.name}</h3>
                <p className="break-all">{radio.url}</p>
                <button
                  type="button"
                  className="admin-button secondary"
                  disabled={busy}
                  onClick={() => {
                    setEditing(radio.id);
                    setName(radio.name);
                    setUrl(radio.url);
                    setSaved(false);
                  }}
                >
                  Modifier
                </button>
                <button
                  type="button"
                  className="admin-button danger"
                  disabled={busy}
                  onClick={() => void remove(radio)}
                >
                  Supprimer
                </button>
              </article>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
