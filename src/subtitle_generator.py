from dataclasses import dataclass
from typing import List
import os


@dataclass
class SubtitleSegment:
    index: int
    start_ms: int
    end_ms: int
    text: str


class SubtitleGenerator:
    def __init__(self):
        pass

    def format_time_srt(self, milliseconds: int) -> str:
        hours = milliseconds // 3600000
        minutes = (milliseconds % 3600000) // 60000
        seconds = (milliseconds % 60000) // 1000
        ms = milliseconds % 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"

    def format_time_ass(self, milliseconds: int) -> str:
        hours = milliseconds // 3600000
        minutes = (milliseconds % 3600000) // 60000
        seconds = (milliseconds % 60000) // 1000
        cs = (milliseconds % 1000) // 10
        return f"{hours}:{minutes:02d}:{seconds:02d}.{cs:02d}"

    def format_time_lrc(self, milliseconds: int) -> str:
        minutes = milliseconds // 60000
        seconds = (milliseconds % 60000) // 1000
        ms = (milliseconds % 1000) // 10
        return f"{minutes:02d}:{seconds:02d}.{ms:02d}"

    def save_srt(self, segments: List[SubtitleSegment], output_path: str) -> bool:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for seg in segments:
                    f.write(f"{seg.index}\n")
                    f.write(f"{self.format_time_srt(seg.start_ms)} --> {self.format_time_srt(seg.end_ms)}\n")
                    f.write(f"{seg.text.strip()}\n\n")
            return True
        except Exception as e:
            print(f"Error saving SRT: {e}")
            return False

    def save_lrc(self, segments: List[SubtitleSegment], output_path: str) -> bool:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for seg in segments:
                    f.write(f"[{self.format_time_lrc(seg.start_ms)}]{seg.text.strip()}\n")
            return True
        except Exception as e:
            print(f"Error saving LRC: {e}")
            return False

    def save_ass(self, segments: List[SubtitleSegment], output_path: str) -> bool:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("[Script Info]\n")
                f.write("Title: Generated Subtitles\n")
                f.write("ScriptType: v4.00+\n\n")

                f.write("[V4+ Styles]\n")
                f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
                f.write("Style: Default,Arial,24,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1\n\n")

                f.write("[Events]\n")
                f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

                for seg in segments:
                    f.write(f"Dialogue: 0,{self.format_time_ass(seg.start_ms)},{self.format_time_ass(seg.end_ms)},Default,,0,0,0,,{seg.text.strip()}\n")
            return True
        except Exception as e:
            print(f"Error saving ASS: {e}")
            return False

    def save(self, segments: List[SubtitleSegment], output_path: str, format_type: str = 'srt') -> bool:
        if format_type.lower() == 'srt':
            return self.save_srt(segments, output_path)
        elif format_type.lower() == 'lrc':
            return self.save_lrc(segments, output_path)
        elif format_type.lower() == 'ass':
            return self.save_ass(segments, output_path)
        else:
            return self.save_srt(segments, output_path)
