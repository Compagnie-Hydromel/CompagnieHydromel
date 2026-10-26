import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Guild } from "../../models/guild";
import MusicPlayer from "../../components/music-player";
import { Dashboard as DashboardAPI } from "../../models/dashboard";
import type { DashboardData, LeaderboardMember } from "../../models/dashboard";

function Leaderboard({
  members,
  monthly,
}: {
  members: LeaderboardMember[];
  monthly: boolean;
}) {
  const { t, i18n } = useTranslation();
  const numbers = new Intl.NumberFormat(i18n.language);
  return (
    <section className="dashboard-panel dashboard-ranking">
      <div className="dashboard-panel-heading">
        <div>
          <p className="dashboard-eyebrow">
            {t(monthly ? "dashboard.monthlyEyebrow" : "dashboard.levelEyebrow")}
          </p>
          <h2>{t(monthly ? "dashboard.monthlyTop" : "dashboard.levelTop")}</h2>
        </div>
        <span className="dashboard-emblem">{monthly ? "♕" : "✦"}</span>
      </div>
      <p className="dashboard-description">
        {t(
          monthly
            ? "dashboard.monthlyDescription"
            : "dashboard.levelDescription",
        )}
      </p>
      {members.length === 0 ? (
        <p className="dashboard-empty">{t("dashboard.noRanking")}</p>
      ) : (
        <ol className="dashboard-leaderboard">
          {members.map((member) => (
            <li
              key={member.discord_id}
              className={member.rank <= 3 ? `podium rank-${member.rank}` : ""}
            >
              <span className="dashboard-rank">
                {member.rank === 1 ? "♛" : member.rank}
              </span>
              <img
                className="dashboard-avatar"
                src={member.avatar_url}
                alt=""
                loading="lazy"
              />
              <div className="dashboard-ranked-member">
                <strong>{member.display_name}</strong>
                <small>
                  {!member.in_guild
                    ? t("dashboard.formerMember")
                    : `@${member.username}`}
                </small>
                {!monthly && (
                  <div
                    className="dashboard-xp-track"
                    role="progressbar"
                    aria-label={t("dashboard.xpProgress", {
                      name: member.display_name,
                    })}
                    aria-valuemin={0}
                    aria-valuemax={member.xp_required}
                    aria-valuenow={Math.min(member.xp, member.xp_required)}
                  >
                    <span style={{ width: `${member.progress * 100}%` }} />
                  </div>
                )}
              </div>
              <div className="dashboard-score">
                <strong>
                  {monthly
                    ? numbers.format(member.monthly_xp)
                    : t("dashboard.levelValue", {
                        level: numbers.format(member.level),
                      })}
                </strong>
                <small>
                  {monthly
                    ? t("dashboard.monthlyXP")
                    : `${numbers.format(member.xp)} / ${numbers.format(member.xp_required)} XP`}
                </small>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

export default function Dashboard() {
  const { t, i18n } = useTranslation();
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [guildRevision, setGuildRevision] = useState(0);
  const [refreshRevision, setRefreshRevision] = useState(0);
  const [showEmpty, setShowEmpty] = useState(false);
  const generation = useRef(0);

  useEffect(() => {
    const changed = () => {
      generation.current += 1;
      setData(null);
      setShowEmpty(false);
      setGuildRevision((value) => value + 1);
    };
    window.addEventListener("guild-changed", changed);
    return () => window.removeEventListener("guild-changed", changed);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const version = ++generation.current;
    let inFlight = false;
    const load = async () => {
      if (inFlight) return;
      inFlight = true;
      setRefreshing(true);
      try {
        const guild = await Guild.currentlySelectedGuild();
        if (!guild) {
          if (!cancelled && version === generation.current) {
            setData(null);
            setError("dashboard.noGuild");
          }
          return;
        }
        const result = await DashboardAPI.forGuild(Number(guild.get("id")));
        if (!cancelled && version === generation.current) {
          setData(result);
          setError("");
        }
      } catch (failure) {
        if (!cancelled && version === generation.current) {
          const denied =
            failure instanceof Error &&
            ["401", "403", "404"].includes(failure.message);
          if (denied) setData(null);
          setError(denied ? "dashboard.denied" : "dashboard.loadError");
        }
      } finally {
        inFlight = false;
        if (!cancelled && version === generation.current) setRefreshing(false);
      }
    };
    void load();
    const timer = window.setInterval(() => {
      if (!document.hidden) void load();
    }, 20000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [guildRevision, refreshRevision]);

  const updated = data
    ? new Intl.DateTimeFormat(i18n.language, {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }).format(new Date(data.updated_at))
    : "";
  const channels =
    data?.voice_channels.filter(
      (channel) => showEmpty || channel.members.length > 0,
    ) ?? [];

  return (
    <div className="dashboard-shell">
      <header className="dashboard-hero">
        <div className="dashboard-guild-identity">
          {data?.guild.icon_url ? (
            <img src={data.guild.icon_url} alt="" />
          ) : (
            <span className="dashboard-guild-placeholder">♜</span>
          )}
          <div>
            <p className="dashboard-eyebrow">{t("dashboard.eyebrow")}</p>
            <h1>{data?.guild.name ?? t("dashboard.title")}</h1>
            <p>{t("dashboard.subtitle")}</p>
          </div>
        </div>
        <div className="dashboard-live-status">
          <span className={error ? "is-stale" : ""}>
            <i />
            {t(error ? "dashboard.stale" : "dashboard.live")}
          </span>
          {data && <small>{t("dashboard.updated", { time: updated })}</small>}
          <button
            type="button"
            disabled={refreshing}
            onClick={() => setRefreshRevision((value) => value + 1)}
          >
            {t(refreshing ? "dashboard.refreshing" : "dashboard.refresh")}
          </button>
        </div>
      </header>
      {error && (
        <div role="alert" className="dashboard-notice">
          {t(error)}
        </div>
      )}
      {!data ? (
        !error && (
          <div role="status" className="dashboard-panel dashboard-empty">
            {t("dashboard.loading")}
          </div>
        )
      ) : (
        <>
          <div className="dashboard-stats">
            <div>
              <span>♬</span>
              <div>
                <strong>{data.voice_member_count}</strong>
                <small>{t("dashboard.inVoice")}</small>
              </div>
            </div>
            <div>
              <span>◉</span>
              <div>
                <strong>{data.active_voice_channel_count}</strong>
                <small>{t("dashboard.activeChannels")}</small>
              </div>
            </div>
            <div>
              <span>♕</span>
              <div>
                <strong>{data.monthly_top[0]?.display_name ?? "—"}</strong>
                <small>{t("dashboard.monthlyLeader")}</small>
              </div>
            </div>
          </div>
          <MusicPlayer compact />
          <section className="dashboard-panel">
            <div className="dashboard-panel-heading">
              <div>
                <p className="dashboard-eyebrow">
                  {t("dashboard.voiceEyebrow")}
                </p>
                <h2>{t("dashboard.voiceTitle")}</h2>
              </div>
              <label className="dashboard-empty-toggle">
                <input
                  type="checkbox"
                  checked={showEmpty}
                  onChange={(event) => setShowEmpty(event.target.checked)}
                />
                {t("dashboard.showEmpty")}
              </label>
            </div>
            <p className="dashboard-description">
              {t("dashboard.voicePrivacy")}
            </p>
            {channels.length === 0 ? (
              <div className="dashboard-empty">
                <span>♬</span>
                <h3>{t("dashboard.noVoice")}</h3>
                <p>{t("dashboard.noVoiceHelp")}</p>
              </div>
            ) : (
              <div className="dashboard-voice-grid">
                {channels.map((channel) => (
                  <article
                    className="dashboard-voice-channel"
                    key={channel.discord_id}
                  >
                    <div className="dashboard-channel-heading">
                      <div>
                        {channel.category && <small>{channel.category}</small>}
                        <h3>
                          {channel.kind === "stage" ? "◉" : "♬"} {channel.name}
                        </h3>
                      </div>
                      <span>{channel.members.length}</span>
                    </div>
                    {channel.members.length === 0 ? (
                      <p className="dashboard-empty-channel">
                        {t("dashboard.emptyChannel")}
                      </p>
                    ) : (
                      <ul>
                        {channel.members.map((member) => (
                          <li key={member.discord_id}>
                            <img
                              className="dashboard-avatar"
                              src={member.avatar_url}
                              alt=""
                              loading="lazy"
                            />
                            <div>
                              <strong>{member.display_name}</strong>
                              <small>
                                @{member.username}
                                {member.bot ? " · BOT" : ""}
                              </small>
                            </div>
                            <div className="dashboard-voice-flags">
                              {member.muted && (
                                <span
                                  title={t("dashboard.muted")}
                                  aria-label={t("dashboard.muted")}
                                >
                                  ♩̸
                                </span>
                              )}
                              {member.deafened && (
                                <span
                                  title={t("dashboard.deafened")}
                                  aria-label={t("dashboard.deafened")}
                                >
                                  ◖̸
                                </span>
                              )}
                              {member.streaming && (
                                <span
                                  className="streaming"
                                  title={t("dashboard.streaming")}
                                >
                                  {t("dashboard.streaming")}
                                </span>
                              )}
                              {member.video && (
                                <span
                                  title={t("dashboard.video")}
                                  aria-label={t("dashboard.video")}
                                >
                                  ▣
                                </span>
                              )}
                            </div>
                          </li>
                        ))}
                      </ul>
                    )}
                  </article>
                ))}
              </div>
            )}
          </section>
          <div className="dashboard-rankings">
            <Leaderboard members={data.monthly_top} monthly />
            <Leaderboard members={data.level_top} monthly={false} />
          </div>
        </>
      )}
    </div>
  );
}
