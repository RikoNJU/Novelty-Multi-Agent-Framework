export function poll(task: (signal: AbortSignal) => Promise<boolean>, delay = 2500): () => void {
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  async function tick() {
    let again = true;
    try { again = await task(controller.signal); } catch { /* caller displays observation errors */ }
    if (again && !controller.signal.aborted) timer = setTimeout(tick, delay);
  }
  void tick();
  return () => {controller.abort(); clearTimeout(timer);};
}
