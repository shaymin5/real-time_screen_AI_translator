### 快速开始
```python
from tts.ttsplayer import TTSplayer
player = TTSplayer()
text = """
穿着紫色长袍、犹如母亲般温柔慷慨、有着山羊外貌的怪物，是玩家在游戏中遇到的第二个角色，非常关心坠落到地下世界的人类。"""
player.generate_and_play_streaming(text)
```