import json
import multiprocessing as mp
from pathlib import Path
from collections import deque
import queue
import time

from voxcpm import VoxCPM
from voxcpm.model.voxcpm import LoRAConfig

from modern_player import AudioEngine

PROJECT_DIR = Path(__file__).resolve().parent.parent


class AudioScheduler:
    """
    单线程、可中断、two-slot 条件抢占 TTS 调度器
    """

    def __init__(self, cmd_queue: mp.Queue, max_play_seconds: float = 30.0):
        self.cmd_queue = cmd_queue
        self._running = True
        self.MAX_PLAY_SECONDS = max_play_seconds # 超时打断时间

        # generation 用于强制中断正在播放的 TTS
        self._generation_id = 0

        # two-slot task queue：current + next
        self._task_queue = deque(maxlen=2)

        # ---------- model ----------
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

    def _load_model(
        self,
        lora_ckpt_dir: Path = PROJECT_DIR / "model/lora/save/step_0002000",
    ):
        with open(lora_ckpt_dir / "lora_config.json", "r", encoding="utf-8") as f:
            lora_info = json.load(f)

        base_model = PROJECT_DIR / lora_info["base_model"]
        lora_cfg = LoRAConfig(**lora_info["lora_config"])

        return VoxCPM.from_pretrained(
            hf_model_id=str(base_model),
            lora_config=lora_cfg,
            lora_weights_path=str(lora_ckpt_dir),
        )

    # ---------- command handling ----------

    def _handle_speak(self, text: str):
        """
        Two-slot conditional preemptive strategy
        """
        if len(self._task_queue) < 2:
            # 未满：不打断
            self._task_queue.append(text)
        else:
            # 已满：打断当前，只保留最新
            self._generation_id += 1
            self.engine.clear()
            self._task_queue.clear()
            self._task_queue.append(text)

    def _handle_stop(self):
        self._generation_id += 1
        self._task_queue.clear()
        self.engine.clear()

    def _handle_exit(self):
        self._handle_stop()
        self._running = False

    def _handle_cmd(self, cmd: dict):
        cmd_type = cmd.get("type")

        if cmd_type == "speak":
            self._handle_speak(cmd["text"])

        elif cmd_type == "stop":
            self._handle_stop()

        elif cmd_type == "exit":
            self._handle_exit()

    # ---------- TTS streaming (可中断) ----------

    def _run_tts_stream(self, text: str, my_gen: int):
        conf = dict(self.generate_conf)
        conf["text"] = text

        start_time = time.monotonic()

        for chunk in self.model.generate_streaming(**conf):
            # ---------- 1. 最高优先级：处理 cmd_queue ----------
            try:
                while True:
                    cmd = self.cmd_queue.get_nowait()
                    self._handle_cmd(cmd)

                    # stop / exit / text 抢占
                    if my_gen != self._generation_id or not self._running:
                        return
            except queue.Empty:
                pass

            # ---------- 2. generation 抢占 ----------
            if my_gen != self._generation_id or not self._running:
                return

            # ---------- 3. 播放超时逻辑（新增） ----------
            elapsed = time.monotonic() - start_time
            if elapsed >= self.MAX_PLAY_SECONDS:
                # 情况 A：已经有 next → 打断
                if self._task_queue:
                    self._generation_id += 1
                    self.engine.clear()
                    return
                # 情况 B：还没有 next → 继续播（什么都不做）

            # ---------- 4. 正常输出 ----------
            self.engine.feed(chunk)

    # ---------- main loop ----------

    def run(self):
        print("[AudioProcess] ready")

        while self._running:
            # 1. 没有待播任务：阻塞等命令
            if not self._task_queue:
                cmd = self.cmd_queue.get()
                self._handle_cmd(cmd)
                continue

            # 2. 有任务：播放（可被 stop / exit / text 抢占）
            my_gen = self._generation_id
            text = self._task_queue.popleft()
            self._run_tts_stream(text, my_gen)

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
    time.sleep(15)
    for i in range(15):
        if i == 5:
            cmd_queue.put({
                "type": "speak",
                "text": f"这是超过5秒的的语音输出测试，测试第{i}次，超级超级超级长，长到无法想象，你不会停止，也不知道它最后能到哪里。也许我们应该静下心来慢慢等待"
            })
        else:
            cmd_queue.put({
                "type": "speak",
                "text": f"这是一次稳定的语音输出测试，测试第{i}次"
            })
        if i==6:
            cmd_queue.put({
                "type": "stop"
            })
        if i == 8:
            cmd_queue.put({
                "type": "speak",
                "text": f"这是一次稳定的语音输出测试，测试第{i}次"
            })
        time.sleep(4)

    time.sleep(10)
    cmd_queue.put({"type": "exit"})
    audio_proc.join()
