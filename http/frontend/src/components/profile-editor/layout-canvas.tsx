import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import type { ProfileLayout } from "../../models/profile";
import ShowProfile from "./show";

const elements = [
  { key: "profile_picture", width: 128, height: 128, maxX: 372, maxY: 153 },
  { key: "name", width: 230, height: 48, maxX: 450, maxY: 231 },
  { key: "username", width: 170, height: 28, maxX: 450, maxY: 253 },
  { key: "level", width: 50, height: 40, maxX: 450, maxY: 241 },
  { key: "badge", width: 32, height: 32, maxX: 468, maxY: 249 },
  { key: "level_bar", width: 500, height: 25, maxX: 450, maxY: 256 },
] as const;

type ElementKey = (typeof elements)[number]["key"];

interface Props {
  layout: ProfileLayout;
  background: string;
  onChange: (layout: ProfileLayout) => void;
}

export default function LayoutCanvas({ layout, background, onChange }: Props) {
  const { t } = useTranslation();
  const canvas = useRef<HTMLDivElement>(null);
  const drag = useRef<{
    key: ElementKey;
    x: number;
    y: number;
    startX: number;
    startY: number;
  } | null>(null);
  const [selected, setSelected] = useState<ElementKey>("profile_picture");

  const move = (key: ElementKey, x: number, y: number) => {
    const element = elements.find((item) => item.key === key)!;
    onChange({
      ...layout,
      [`${key}_x`]: Math.max(0, Math.min(element.maxX, Math.round(x))),
      [`${key}_y`]: Math.max(0, Math.min(element.maxY, Math.round(y))),
    });
  };

  return (
    <div className="layout-workspace">
      <div className="layout-canvas-scroll">
        <div
          ref={canvas}
          className="layout-canvas"
          aria-label={t("admin.canvas")}
        >
          <ShowProfile
            {...layout}
            background={background}
            displayName="Capitaine Hydromel"
            username="compagnie"
            level={12}
            progress={65}
            name_color="#fff4d4"
            bar_color="#edbd68"
            badges={["https://cdn.discordapp.com/embed/avatars/1.png"]}
          />
          <div className="layout-grid" aria-hidden="true" />
          {elements.map((element) => (
            <button
              key={element.key}
              type="button"
              className={`layout-handle ${selected === element.key ? "selected" : ""}`}
              style={{
                left: layout[`${element.key}_x`],
                top: layout[`${element.key}_y`],
                width: element.width,
                height: element.height,
              }}
              aria-label={t(`admin.elements.${element.key}`)}
              aria-pressed={selected === element.key}
              onFocus={() => setSelected(element.key)}
              onPointerDown={(event) => {
                if (event.button !== 0) return;
                event.preventDefault();
                event.currentTarget.focus();
                event.currentTarget.setPointerCapture(event.pointerId);
                setSelected(element.key);
                drag.current = {
                  key: element.key,
                  x: layout[`${element.key}_x`],
                  y: layout[`${element.key}_y`],
                  startX: event.clientX,
                  startY: event.clientY,
                };
              }}
              onPointerMove={(event) => {
                const current = drag.current;
                if (!current || current.key !== element.key) return;
                const scale =
                  500 / (canvas.current?.getBoundingClientRect().width || 500);
                move(
                  element.key,
                  current.x + (event.clientX - current.startX) * scale,
                  current.y + (event.clientY - current.startY) * scale,
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
              onKeyDown={(event) => {
                const step = event.shiftKey ? 10 : 1;
                const delta = {
                  ArrowLeft: [-step, 0],
                  ArrowRight: [step, 0],
                  ArrowUp: [0, -step],
                  ArrowDown: [0, step],
                }[event.key];
                if (!delta) return;
                event.preventDefault();
                move(
                  element.key,
                  layout[`${element.key}_x`] + delta[0],
                  layout[`${element.key}_y`] + delta[1],
                );
              }}
            >
              <span>{t(`admin.elements.${element.key}`)}</span>
            </button>
          ))}
        </div>
      </div>
      <p className="admin-hint">↔ {t("admin.dragHint")}</p>
      <div className="layout-layers">
        {elements.map((element) => (
          <button
            type="button"
            key={element.key}
            className={selected === element.key ? "selected" : ""}
            onClick={() => {
              setSelected(element.key);
              const handles =
                canvas.current?.querySelectorAll<HTMLButtonElement>(
                  ".layout-handle",
                );
              handles?.[elements.indexOf(element)]?.focus();
            }}
          >
            {t(`admin.elements.${element.key}`)}
          </button>
        ))}
      </div>
    </div>
  );
}
