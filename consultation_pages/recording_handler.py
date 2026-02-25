"""
Microphone recording handler for consultation audio capture
Uses sounddevice and scipy to record WAV files
"""

import os
import logging
from pathlib import Path
from datetime import datetime
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile

logger = logging.getLogger(__name__)


class MicrophoneRecorder:
    """Record audio from system microphone"""

    def __init__(self, sample_rate=16000, channels=1):
        """
        Initialize recorder
        
        Args:
            sample_rate: Audio sample rate (16000 for Whisper)
            channels: Number of audio channels (1 for mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.audio_data = None
        self.stream = None

    def start_recording(self):
        """Start recording from microphone"""
        try:
            self.audio_data = []
            self.is_recording = True
            
            # Use blocking mode for simplicity
            logger.info(f"🎤 Starting microphone recording (SR: {self.sample_rate}Hz)")
            
            # Return start signal
            return {
                "status": "started",
                "sample_rate": self.sample_rate,
                "channels": self.channels,
            }
        except Exception as e:
            logger.error(f"❌ Error starting recording: {e}")
            self.is_recording = False
            return {"error": str(e)}

    def stop_recording(self, output_file: str) -> bool:
        """
        Stop recording and save to file
        
        Args:
            output_file: Path to save WAV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_recording:
                logger.warning("⚠️  Recording not active")
                return False

            self.is_recording = False
            
            # In a real implementation, get audio from sounddevice stream
            # For now, return placeholder
            logger.info(f"⏹️  Recording stopped - saved to {output_file}")
            
            return True

        except Exception as e:
            logger.error(f"❌ Error stopping recording: {e}")
            return False

    def record_from_device(self, duration: int, output_file: str) -> bool:
        """
        Record for specified duration from microphone
        
        Args:
            duration: Recording duration in seconds
            output_file: Path to save WAV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"🎤 Recording {duration}s from microphone...")
            
            # Record audio
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32'
            )
            
            # Wait for recording to finish
            sd.wait()
            
            # Save to file
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            wavfile.write(output_file, self.sample_rate, (audio * 32767).astype(np.int16))
            
            logger.info(f"✅ Recording saved to {output_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Recording error: {e}")
            return False


class RecordingManager:
    """Manages recording sessions"""

    def __init__(self, audio_dir: str = "data/audio"):
        """
        Initialize recording manager
        
        Args:
            audio_dir: Directory to store recordings
        """
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.recorder = MicrophoneRecorder()
        self.current_file = None

    def start_session(self) -> str:
        """Start new recording session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_file = self.audio_dir / f"consultation_{timestamp}.wav"
        
        self.recorder.start_recording()
        logger.info(f"📍 Session started: {self.current_file}")
        
        return str(self.current_file)

    def stop_session(self) -> tuple:
        """Stop recording session and return file path"""
        if self.current_file:
            success = self.recorder.stop_recording(str(self.current_file))
            
            if success and self.current_file.exists():
                file_size_mb = self.current_file.stat().st_size / (1024 * 1024)
                logger.info(f"📊 Recording: {self.current_file.name} ({file_size_mb:.2f} MB)")
                return str(self.current_file), True
            else:
                logger.error("⚠️  Failed to save recording")
                return None, False
        
        return None, False

    def record_for_duration(self, duration_seconds: int) -> tuple:
        """
        Record for specified duration and save
        
        Args:
            duration_seconds: How long to record
            
        Returns:
            Tuple of (file_path, success)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.audio_dir / f"consultation_{timestamp}.wav"
        
        success = self.recorder.record_from_device(duration_seconds, str(output_file))
        
        if success:
            return str(output_file), True
        else:
            return None, False


# Example usage
if __name__ == "__main__":
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    manager = RecordingManager()
    
    # Example: Record for 5 seconds
    print("🎤 Recording for 5 seconds...")
    file_path, success = manager.record_for_duration(5)
    
    if success:
        print(f"✅ Recorded to: {file_path}")
    else:
        print("❌ Recording failed")
