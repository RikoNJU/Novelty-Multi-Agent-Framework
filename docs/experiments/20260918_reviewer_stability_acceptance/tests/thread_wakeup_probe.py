"""Diagnostic only: compare asyncio.to_thread with explicit Future polling."""
import asyncio
import concurrent.futures
import contextvars
import threading


def blocking(event):
    event.wait(1)
    return "worker-returned"


async def probe():
    event = threading.Event()
    task = asyncio.create_task(asyncio.to_thread(blocking, event))
    await asyncio.sleep(0.05)
    event.set()
    try:
        result = await asyncio.wait_for(task, 0.3)
        print(f"to_thread={result}", flush=True)
    except TimeoutError:
        print("to_thread=timed_out_after_worker_release", flush=True)
    result_future = concurrent.futures.Future()
    context = contextvars.copy_context()
    def invoke():
        result_future.set_result(context.run(blocking, event))
    threading.Thread(target=invoke, daemon=True).start()
    while not result_future.done():
        await asyncio.sleep(0.01)
    print(f"polling={result_future.result()}", flush=True)


asyncio.run(probe())
