import whisper
import torch
from typing import List, Optional, Callable
import os
import sys
import shutil
import tempfile
import numpy as np


def contains_chinese(path: str) -> bool:
    for char in path:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False


def load_audio_without_ffmpeg(file_path: str) -> np.ndarray:
    try:
        import soundfile as sf
        audio, sample_rate = sf.read(file_path)
        
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
        
        if sample_rate != 16000:
            from scipy.signal import resample
            audio = resample(audio, int(len(audio) * 16000 / sample_rate))
        
        return audio.astype(np.float32)
    except ImportError:
        raise ImportError("需要安装 soundfile 和 scipy")
    except Exception as e:
        raise RuntimeError(f"读取音频失败: {e}")


class WhisperRecognizer:
    def __init__(self, model_name: str = "small", device: Optional[str] = None):
        self.model_name = model_name
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        self.model = None

    def load_model(self) -> bool:
        try:
            print(f"Loading Whisper model '{self.model_name}' on {self.device}...")
            self.model = whisper.load_model(self.model_name, device=self.device)
            print("Model loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def transcribe(self,
                   audio_path: str,
                   language: str = "zh",
                   progress_callback: Optional[Callable[[float], None]] = None) -> dict:
        if self.model is None:
            if not self.load_model():
                return {"success": False, "error": "Failed to load model"}

        try:
            audio_path = os.path.abspath(audio_path)
            print(f"Transcribing: {audio_path}")
            print(f"Language: {language}, Device: {self.device}")

            if not os.path.exists(audio_path):
                return {"success": False, "error": f"文件不存在: {audio_path}"}

            temp_path = None
            use_temp = contains_chinese(audio_path) and sys.platform.startswith('win')
            
            if use_temp:
                print("检测到中文路径，创建临时文件...")
                temp_dir = tempfile.mkdtemp()
                ext = os.path.splitext(audio_path)[1]
                temp_path = os.path.join(temp_dir, f"temp_audio{ext}")
                shutil.copy2(audio_path, temp_path)
                print(f"临时文件: {temp_path}")
                audio_path = temp_path

            options = {
                "language": language,
                "task": "transcribe",
                "verbose": False,
            }

            try:
                result = self.model.transcribe(audio_path, **options)
            except FileNotFoundError as e:
                print(f"ffmpeg调用失败，尝试使用Python库读取...")
                print(f"错误: {e}")
                
                audio_data = load_audio_without_ffmpeg(audio_path)
                result = self.model.transcribe(audio_data, **options)

            if temp_path:
                try:
                    os.remove(temp_path)
                    os.rmdir(os.path.dirname(temp_path))
                except:
                    pass

            segments = []
            if "segments" in result:
                for i, seg in enumerate(result["segments"]):
                    start_ms = int(seg["start"] * 1000)
                    end_ms = int(seg["end"] * 1000)
                    text = seg["text"].strip()

                    from .subtitle_generator import SubtitleSegment
                    segments.append(SubtitleSegment(
                        index=i + 1,
                        start_ms=start_ms,
                        end_ms=end_ms,
                        text=text
                    ))

            return {
                "success": True,
                "segments": segments,
                "text": result.get("text", ""),
                "language": result.get("language", language)
            }

        except Exception as e:
            print(f"Transcription error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def get_available_models(self) -> List[str]:
        return ["tiny", "base", "small", "medium", "large"]

    def get_device_info(self) -> dict:
        return {
            "device": self.device,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
