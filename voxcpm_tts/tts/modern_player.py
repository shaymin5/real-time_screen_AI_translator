# audio_process.py
import sounddevice as sd
import numpy as np
import threading
import multiprocessing as mp
import collections
from typing import Union


class AudioEngine:
    """
    纯音频引擎：
    - sounddevice callback
    - ring buffer
    - 不知道 TTS、不知道进程
    """

    def __init__(self, sample_rate: int, block_size: int = 1024, max_seconds=5.0):
        self.sample_rate = sample_rate
        self.block_size = block_size

        self.max_samples = int(sample_rate * max_seconds)
        self.buffer = collections.deque(maxlen=self.max_samples)
        self.lock = threading.Lock()

        self._stream: Union[sd.OutputStream, None] = None

    def callback(self, outdata, frames, time_info, status):
        out = np.zeros(frames, dtype=np.float32)

        with self.lock:
            n = min(len(self.buffer), frames)
            for i in range(n):
                out[i] = self.buffer.popleft()

        outdata[:] = out.reshape(-1, 1)

    def start(self):
        self._stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=self.block_size,
            callback=self.callback,
            latency="low",
        )
        self._stream.start()

    def stop(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def clear(self):
        """抢占时清空残余音频"""
        with self.lock:
            self.buffer.clear()

    def feed(self, chunk: np.ndarray):
        with self.lock:
            self.buffer.extend(chunk.tolist())

if __name__ == "__main__":
    import time

    from audio_process import audio_process_entry

    cmd_queue = mp.Queue()
    audio_proc = mp.Process(
        target=audio_process_entry,
        args=(cmd_queue,),
        daemon=False,  # 关键
    )
    audio_proc.start()

    for i in range(10):
        cmd_queue.put({
            "type": "speak",
            "content": f"测试发言：第 {i} 次"
        })
        time.sleep(5)
    # cmd_queue.put({
    #     'type': 'speak',
    #     'content': '你好朋友，这是一次声音测试。'
    # })
    time.sleep(5)
    cmd_queue.put({"type": "exit"})
    audio_proc.join()