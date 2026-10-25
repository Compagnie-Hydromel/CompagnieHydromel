import { useEffect, useRef, useState } from "react";
import ShowProfile from "./show";
import type { ComponentProps } from "react";

export default function ResponsiveProfilePreview(
  props: ComponentProps<typeof ShowProfile>,
) {
  const container = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  useEffect(() => {
    const element = container.current;
    if (!element) return;
    const resize = () =>
      setScale(Math.min(1, element.getBoundingClientRect().width / 500));
    resize();
    const observer = new ResizeObserver(resize);
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  return (
    <div
      ref={container}
      className="profile-preview-container"
      style={{ height: 281 * scale }}
    >
      <div
        className="profile-preview-scaled"
        style={{ transform: `scale(${scale})` }}
      >
        <ShowProfile {...props} />
      </div>
    </div>
  );
}
