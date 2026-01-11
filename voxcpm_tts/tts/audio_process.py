# audio_process.py
import json
import multiprocessing as mp
import threading
from pathlib import Path
import time

from voxcpm import VoxCPM
from voxcpm.model.voxcpm import LoRAConfig

from modern_player import AudioEngine

PROJECT_DIR = Path(__file__).resolve().parent.parent


class TTSProcess:
    """
    子进程内：
    - 持有 TTS 模型
    - 持有 AudioEngine
    - 管理抢占式 TTS 生成线程
    """

    def __init__(
        self,
        prompt_audio_path: Path = PROJECT_DIR / "model/prompt/prompt_haibara_ai.wav",
        prompt_text: str = "就因为有博士的帮忙，身体即使缩小了，还是能做少年侦探。",
    ):
        self.generate_conf = {
            "prompt_wav_path": str(prompt_audio_path),
            "prompt_text": prompt_text,
            "cfg_value": 2.2,
            "inference_timesteps": 20,
            "normalize": False,
            "denoise": False,
            "retry_badcase": True,
            "retry_badcase_max_times": 3,
            "retry_badcase_ratio_threshold": 6.0,
        }

        self.model = self._load_model()

        self.engine = AudioEngine(
            sample_rate=self.model.tts_model.sample_rate
        )
        self.engine.start()

        self._tts_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

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

    # ---------- TTS thread ----------

    def _tts_generate_loop(self, text: str):
        conf = dict(self.generate_conf)
        conf["text"] = text

        for chunk in self.model.generate_streaming(**conf):
            if self._stop_event.is_set():
                break
            self.engine.feed(chunk)

    def _stop_current_tts(self):
        """抢占式停止当前 TTS"""
        self._stop_event.set()

        if self._tts_thread and self._tts_thread.is_alive():
            self._tts_thread.join(timeout=0.2)

        self._tts_thread = None
        self.engine.clear()
        self._stop_event.clear()

    # ---------- public handlers ----------

    def speak(self, text: str):
        self._stop_current_tts()

        self._tts_thread = threading.Thread(
            target=self._tts_generate_loop,
            args=(text,),
            daemon=True,
        )
        self._tts_thread.start()

    def stop(self):
        self._stop_current_tts()

    def shutdown(self):
        self.stop()
        self.engine.stop()


# ---------- process entry ----------

def audio_process_entry(cmd_queue: mp.Queue):
    print("[AudioProcess] starting...")
    process = TTSProcess()
    print("[AudioProcess] ready")

    while True:
        cmd = cmd_queue.get()

        if cmd["type"] == "speak":
            process.speak(cmd["content"])

        elif cmd["type"] == "stop":
            process.stop()

        elif cmd["type"] == "exit":
            process.shutdown()
            break
        time.sleep(2)
