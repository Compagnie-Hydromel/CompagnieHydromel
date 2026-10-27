/** Server-driven snapshots, with a fresh snapshot after every reconnect. */
export function subscribeLive<T>(
  path: string,
  onData: (data: T) => void,
  onError: (status: string) => void,
) {
  let stopped = false;
  let socket: WebSocket | undefined;
  let timer: number | undefined;
  let delay = 1000;
  const connect = () => {
    if (stopped) return;
    const url = new URL(path, window.location.href);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    socket = new WebSocket(url);
    socket.onmessage = (event) => {
      if (stopped) return;
      try {
        const message = JSON.parse(event.data);
        if (message.type === "snapshot") {
          delay = 1000;
          onData(message.data as T);
        }
      } catch {
        onError("503");
      }
    };
    socket.onclose = (event) => {
      if (stopped) return;
      const denied = [4401, 4403, 4404].includes(event.code);
      onError(denied ? String(event.code - 4000) : "503");
      if (!denied) {
        timer = window.setTimeout(connect, delay);
        delay = Math.min(delay * 2, 30000);
      }
    };
  };
  connect();
  return () => {
    stopped = true;
    window.clearTimeout(timer);
    socket?.close();
  };
}
