### 快速开始
```python
from tts.audio_process import audio_process_entry
import multiprocessing as mp
import time

if __name__ == "__main__":
    cmd_queue = mp.Queue()

    audio_proc = mp.Process(
        target=audio_process_entry,
        args=(cmd_queue,),
        daemon=False,
    )
    audio_proc.start()
    cmd_queue.put({
        "type": "speak",
        "text": "你想要说什么就写在这里。"
    })

    time.sleep(10)

    # 停止播放
    # cmd_queue.put({"type": "stop"})

    # 终止程序(可以直接exit，不用先stop再exit)
    cmd_queue.put({"type": "exit"})
    audio_proc.join()
```