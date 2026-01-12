import json
import multiprocessing as mp
import time
from pathlib import Path
from typing import Optional
from collections import deque

from voxcpm import VoxCPM
from voxcpm.model.voxcpm import LoRAConfig

from modern_player import AudioEngine

PROJECT_DIR = Path(__file__).resolve().parent.parent


class AudioScheduler:
    """
    音频进程内的唯一调度器：
    - 串行消费 cmd_queue
    - 同一时间只允许一个 TTS 任务
    - 使用 generation_id 实现强抢占
    """

    def __init__(self, cmd_queue: mp.Queue):
        self.cmd_queue = cmd_queue
        self._running = True

        self._generation_id = 0
        self._task_queue = deque(maxlen=2)

        self.model = self._load_model()
        self.engine = AudioEngine(
            sample_rate=self.model.tts_model.sample_rate
        )
        self.engine.start()

        self.generate_conf = {
            "prompt_wav_path": str(PROJECT_DIR / "model/prompt/prompt_haibara_ai.wav"),
            "prompt_text": "就因为有博士的帮忙，身体即使缩小了，还是能做少年侦探。",
            "cfg_value": 2.2,
            "inference_timesteps": 20,
            "normalize": False,
            "denoise": False,
            "retry_badcase": True,
            "retry_badcase_max_times": 3,
            "retry_badcase_ratio_threshold": 6.0,
        }

    # ---------- model ----------

    def _load_model(self, lora_ckpt_dir: Path = PROJECT_DIR / "model/lora/save/step_0002000"):
        with open(lora_ckpt_dir / "lora_config.json", "r", encoding="utf-8") as f:
            lora_info = json.load(f)

        base_model = PROJECT_DIR / lora_info["base_model"]
        lora_cfg = LoRAConfig(**lora_info["lora_config"])

        return VoxCPM.from_pretrained(
            hf_model_id=str(base_model),
            lora_config=lora_cfg,
            lora_weights_path=str(lora_ckpt_dir),
        )

    # ---------- public API ----------

    def stop_current(self):
        """
        强制终止当前任务：
        - generation_id 自增
        - 清空音频 buffer
        """
        self._generation_id += 1
        self._task_queue.clear()
        self.engine.clear()

    def speak(self, text: str):
        """
        Two-slot conditional preemptive strategy:
        - queue size < 2: enqueue, do NOT interrupt
        - queue size == 2: interrupt current, keep only newest
        """
        if len(self._task_queue) < 2:
            # 情况 1 / 2：不抢占
            self._task_queue.append(text)
        else:
            # 情况 3：队列已满，触发抢占
            self._generation_id += 1          # 终止当前播放
            self.engine.clear()               # 清空残余音频
            self._task_queue.clear()          # 丢弃旧任务
            self._task_queue.append(text)     # 只保留最新

    # ---------- core loop ----------
    def _run_tts_blocking(self, text: str, my_generation: int):
        conf = dict(self.generate_conf)
        conf["text"] = text

        for chunk in self.model.generate_streaming(**conf):
            # 抢占检查（这是整个系统的核心）
            if my_generation != self._generation_id:
                return
            self.engine.feed(chunk)

    def run(self):
        """
        音频进程的唯一主循环
        """
        print("[AudioProcess] ready")

        while self._running:
            # 优先处理命令
            while not self.cmd_queue.empty():
                cmd = self.cmd_queue.get()

                if cmd["type"] == "speak":
                    self.speak(cmd["text"])

                elif cmd["type"] == "stop":
                    self.stop_current()

                elif cmd["type"] == "exit":
                    self.stop_current()
                    self._running = False
                    break

            # 如果当前有任务，就同步跑 TTS
            if self._task_queue:
                my_gen = self._generation_id
                text = self._task_queue.popleft()
                self._run_tts_blocking(text, my_gen)

            time.sleep(0.01)

        self.engine.stop()
        print("[AudioProcess] exited")


def audio_process_entry(cmd_queue: mp.Queue):
    scheduler = AudioScheduler(cmd_queue)
    scheduler.run()


if __name__ == "__main__":
    cmd_queue = mp.Queue()

    audio_proc = mp.Process(
        target=audio_process_entry,
        args=(cmd_queue,),
        daemon=False,
    )
    audio_proc.start()

    
    for i in range(5):
        cmd_queue.put({
        "type": "speak",
        "text": f"这是一次稳定的语音输出测试，测试第{i}次"
        })
        time.sleep(8)
    time.sleep(10)
    cmd_queue.put({"type": "exit"})
    audio_proc.join()
