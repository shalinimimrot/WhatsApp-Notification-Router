from pathlib import Path
import easyocr
from faster_whisper import WhisperModel


class MediaProcessor:

    def __init__(self):

        self.reader = easyocr.Reader(["en"], gpu=False)

        self.whisper = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

    def process(self, message, data):

        text = str(message.get("message_text", ""))

        media_type = str(message.get("media_type", "")).lower()

        # ------------------------
        # IMAGE
        # ------------------------

        if media_type == "image":

            image_id = message["media_id"]

            image = data["images"]

            row = image[
                image["image_id"] == image_id
            ]

            if not row.empty:

                image_path = "../dataset/" + row.iloc[0]["file_path"]

                if Path(image_path).exists():

                    try:

                        result = self.reader.readtext(
                            image_path,
                            detail=0
                        )

                        text += "\n\n" + " ".join(result)

                    except Exception:

                        pass

        # ------------------------
        # VOICE
        # ------------------------

        elif media_type == "voice_note":

            voice_id = message["media_id"]

            voices = data["voice_notes"]

            row = voices[
                voices["voice_note_id"] == voice_id
            ]

            if not row.empty:

                audio_path = "../dataset/" + row.iloc[0]["file_path"]

                if Path(audio_path).exists():

                    try:

                        segments, _ = self.whisper.transcribe(audio_path)

                        transcript = ""

                        for segment in segments:

                            transcript += segment.text + " "

                        text += "\n\n" + transcript

                    except Exception:

                        pass

        return text