import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Guild } from "../models/guild";
import { Music } from "../models/music";
import type { MusicState, Track } from "../models/music";
import { subscribeLive } from "../utils/live";

function duration(track: Track) {
  if (!track.length) return "En direct";
  const seconds = Math.floor(track.length / 1000);
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

export default function MusicPlayer({
  compact = false,
}: {
  compact?: boolean;
}) {
  const [state, setState] = useState<MusicState | null>(null);
  const [guildId, setGuildId] = useState<number | null>(null);
  const [revision, setRevision] = useState(0);
  const [query, setQuery] = useState("");
  const [source, setSource] = useState("soundcloud");
  const [radioId, setRadioId] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const generation = useRef(0);
  const operation = useRef(0);
  const acting = useRef(false);

  useEffect(() => {
    const changed = () => {
      generation.current += 1;
      setGuildId(null);
      setState(null);
      setError("");
      setQuery("");
      setRadioId("");
      setBusy(false);
      acting.current = false;
      setRevision((value) => value + 1);
    };
    window.addEventListener("guild-changed", changed);
    return () => window.removeEventListener("guild-changed", changed);
  }, []);

  useEffect(() => {
    const version = ++generation.current;
    let cancelled = false;
    let unsubscribe: (() => void) | undefined;
    const load = async () => {
      const currentOperation = operation.current;
      try {
        const guild = await Guild.currentlySelectedGuild();
        if (!guild) throw new Error("Sélectionnez un serveur.");
        const id = Number(guild.get("id"));
        if (cancelled || version !== generation.current) return;
        setGuildId(id);
        unsubscribe = subscribeLive<MusicState>(
          `/api/sessions/guilds/${id}/music/live`,
          (data) => {
            if (cancelled || version !== generation.current) return;
            setState(data);
            setError("");
          },
          (status) => {
            if (cancelled || version !== generation.current) return;
            setState(null);
            setError(
              ["401", "403", "404"].includes(status)
                ? "Accès refusé."
                : "Ménestrel indisponible. Reconnexion…",
            );
          },
        );
      } catch (failure) {
        if (
          !cancelled &&
          version === generation.current &&
          !acting.current &&
          currentOperation === operation.current
        ) {
          setState(null);
          setError(
            failure instanceof Error
              ? failure.message
              : "Ménestrel indisponible.",
          );
        }
      }
    };
    void load();
    return () => {
      cancelled = true;
      unsubscribe?.();
    };
  }, [revision]);

  const control = async (action: string) => {
    if (!guildId || acting.current) return;
    const version = generation.current;
    operation.current += 1;
    acting.current = true;
    setBusy(true);
    setError("");
    try {
      const result = await Music.request(guildId, {
        action,
        query: source === "radio" ? radioId : query,
        source,
      });
      if (version === generation.current) {
        setState(result);
        if (action === "play") setQuery("");
      }
    } catch (failure) {
      if (version === generation.current)
        setError(
          failure instanceof Error ? failure.message : "Commande refusée.",
        );
    } finally {
      if (version === generation.current) {
        acting.current = false;
        setBusy(false);
      }
    }
  };

  return (
    <section className="dashboard-panel music-player" aria-label="Ménestrel">
      <div className="dashboard-panel-heading">
        <div>
          <p className="dashboard-eyebrow">Streaming</p>
          <h2>♬ Le Ménestrel</h2>
        </div>
        {compact && <Link to="/dashboard/music">Ouvrir le lecteur →</Link>}
      </div>
      <p className="dashboard-description">
        Rejoignez un salon vocal Discord pour lancer et contrôler la musique.
        YouTube, SoundCloud et radios de la liste proposée.
      </p>
      {error && (
        <p role="alert" className="dashboard-notice">
          {error}
        </p>
      )}
      {state?.error && <p role="status">{state.error}</p>}
      {state?.current ? (
        <div className="music-current">
          <strong>
            <a href={state.current.uri} target="_blank" rel="noreferrer">
              {state.current.title}
            </a>
          </strong>
          <span>
            {state.current.author} · {duration(state.current)} ·{" "}
            {state.current.source}
          </span>
          <small>
            {state.paused ? "En pause" : "En lecture"} · {state.channel_name}
          </small>
        </div>
      ) : (
        <p className="dashboard-empty">Aucune musique en cours.</p>
      )}
      <div className="music-controls">
        <button
          type="button"
          disabled={busy || !state?.connected || !state.has_previous}
          onClick={() => void control("back")}
        >
          ⏮ Précédent
        </button>
        <button
          type="button"
          disabled={busy || !state?.current}
          onClick={() => void control(state?.paused ? "resume" : "pause")}
        >
          {state?.paused ? "▶ Reprendre" : "⏸ Pause"}
        </button>
        <button
          type="button"
          disabled={busy || !state?.queue.length}
          onClick={() => void control("skip")}
        >
          ⏭ Suivant
        </button>
        <button
          type="button"
          disabled={busy || !state?.connected}
          onClick={() => void control("stop")}
        >
          ⏹ Arrêter
        </button>
      </div>
      {!compact && (
        <form
          className="music-search"
          onSubmit={(event) => {
            event.preventDefault();
            void control("play");
          }}
        >
          <label>
            Source
            <select
              value={source}
              onChange={(event) => setSource(event.target.value)}
              disabled={busy}
            >
              <option value="soundcloud">SoundCloud</option>
              <option value="youtube">YouTube</option>
              <option value="radio">Radio</option>
            </select>
          </label>
          <label className="music-query">
            {source === "radio" ? "Radio à écouter" : "Titre, artiste ou lien"}
            {source === "radio" ? (
              <select
                required
                value={radioId}
                onChange={(event) => setRadioId(event.target.value)}
                disabled={busy || !state?.radios?.length}
              >
                <option value="">
                  {state?.radios?.length
                    ? "Choisir une radio…"
                    : "Aucune radio disponible"}
                </option>
                {(state?.radios ?? []).map((radio) => (
                  <option key={radio.id} value={radio.id}>
                    {radio.name}
                  </option>
                ))}
              </select>
            ) : (
              <input
                required
                maxLength={500}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                disabled={busy}
                placeholder="Rechercher une musique…"
              />
            )}
          </label>
          <button
            disabled={
              busy ||
              !guildId ||
              (source === "radio"
                ? !state?.radios?.some((radio) => radio.id === radioId)
                : !query.trim())
            }
          >
            {busy ? "Patientez…" : "▶ Lire / Ajouter"}
          </button>
        </form>
      )}
      {!state && (
        <button type="button" onClick={() => setRevision((value) => value + 1)}>
          Réessayer
        </button>
      )}
      {!compact && (
        <div className="music-queue">
          <h3>File d’attente ({state?.queue.length ?? 0}/100)</h3>
          {state?.queue.length ? (
            <ol>
              {state.queue.map((track, index) => (
                <li key={`${index}-${track.uri}`}>
                  <a href={track.uri} target="_blank" rel="noreferrer">
                    {track.title}
                  </a>
                  <small>
                    {track.author} · {duration(track)} · {track.source}
                  </small>
                </li>
              ))}
            </ol>
          ) : (
            <p>Aucun titre en attente.</p>
          )}
        </div>
      )}
    </section>
  );
}
