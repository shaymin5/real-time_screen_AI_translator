from .player import SyncBufferedTTSPlayer
from voxcpm import VoxCPM
from voxcpm.model.voxcpm import LoRAConfig
import json
from typing import Union
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

class TTSplayer:
    def __init__(
            self, 
            lora_ckpt_dir: Path = PROJECT_DIR/"./model/lora/save/step_0002000", 
            prompt_path: Path = PROJECT_DIR/"./model/prompt/prompt_haibara_ai.wav", 
            prompt_text: str = "就因为有博士的帮忙，身体即使缩小了，还是能做少年侦探。"
        ):
        self.lora_ckpt_dir = lora_ckpt_dir
        self.model = self._load_model()
        self.player = SyncBufferedTTSPlayer(self.model)
        self.generate_conf = {
            'text':"为您播报测试音频。",
            'prompt_wav_path':str(prompt_path),      # optional: path to a prompt speech for voice cloning
            'prompt_text':str(prompt_text),          # optional: reference text
            'cfg_value':2.2,             # LM guidance on LocDiT, higher for better adherence to the prompt, but maybe worse
            'inference_timesteps':20,   # LocDiT inference timesteps, higher for better result, lower for fast speed
            'normalize':False,           # enable external TN tool, but will disable native raw text support
            'denoise':False,             # enable external Denoise tool, but it may cause some distortion and restrict the sampling rate to 16kHz
            'retry_badcase':True,        # enable retrying mode for some bad cases (unstoppable)
            'retry_badcase_max_times':3,  # maximum retrying times
            'retry_badcase_ratio_threshold':6.0  # maximum length restriction for bad case detection (simple but effective), it could be adjusted for slow pace speech
        }

    def _load_model(self):
        with open(f"{self.lora_ckpt_dir}/lora_config.json") as f:
            lora_info = json.load(f)
        base_model = PROJECT_DIR/lora_info["base_model"]
        lora_cfg = LoRAConfig(**lora_info["lora_config"])
        # Load model with LoRA
        model = VoxCPM.from_pretrained(
            hf_model_id=str(base_model),
            lora_config=lora_cfg,
            lora_weights_path=str(self.lora_ckpt_dir),
        )
        return model
    
    def generate_and_play_streaming(self, text: str, generate_conf:Union[None, dict]=None):
        """
            关于generate_conf参数，可考虑以下kv对

            ==============================  ========================  ============================================================
            参数                               默认值                     描述
            ==============================  ========================  ============================================================
            text                            "为您播报测试音频。"          要合成的文本
            prompt_wav_path                 'prompt_haibara_ai.wav'     用于声音克隆的提示音频路径 (可选)
            prompt_text                     "你那个小小的电话..."       参考文本，用于声音克隆 (可选)
            cfg_value                       2.2                       LocDiT的LM引导值，较高的值可更好地遵循提示，但可能质量下降
            inference_timesteps             20                        LocDiT推理时间步长，较高的值结果更好，较低的值速度更快
            normalize                       False                     启用外部文本规范化工具，但会禁用原生原始文本支持
            denoise                         False                     启用外部降噪工具，但可能导致失真并将采样率限制为16kHz
            retry_badcase                   True                      启用对某些错误情况的重试模式(无法停止的情况)
            retry_badcase_max_times         3                         最大重试次数
            retry_badcase_ratio_threshold   6.0                       错误情况检测的最大长度限制，简单但有效
            ==============================  =======================  ============================================================
        """
        if generate_conf is None:
            self.generate_conf['text'] = text
            self.player.play_streaming(self.generate_conf)
        else:
            self.generate_conf.update(generate_conf)
            self.generate_conf['text'] = text
            self.player.play_streaming(self.generate_conf) # 接收外来的合成config

    def stop(self):
        self.player.stop()
    


