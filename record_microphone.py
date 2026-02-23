"""
Enhanced Microphone Recording Tool with Real-time Monitoring
"""

import sys
import os
import json
import numpy as np
from pathlib import Path

try:
    import sounddevice as sd
    import soundfile as sf
except ImportError:
    print("❌ Missing sounddevice - installing...")
    os.system("pip install sounddevice soundfile -q")
    import sounddevice as sd
    import soundfile as sf

def record_with_monitoring(duration=15, sample_rate=16000):
    """
    Record audio with real-time monitoring of audio levels
    """
    print("\n" + "="*80)
    print("🎤 MICROPHONE RECORDING WITH REAL-TIME MONITORING")
    print("="*80)
    
    print(f"\n📋 Configuration:")
    print(f"   Duration: {duration} seconds")
    print(f"   Sample rate: {sample_rate} Hz (16kHz = standard for speech)")
    print(f"   Channels: Mono (1)")
    
    # List available devices
    print(f"\n🔌 Available Audio Devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        marker = "✓ DEFAULT INPUT" if i == sd.default.device[0] else ""
        print(f"   [{i}] {device['name']} - IN:{device['max_input_channels']}, OUT:{device['max_output_channels']} {marker}")
    
    print(f"\n⚠️  IMPORTANT: Make sure your microphone is selected as default input device!")
    print(f"   1. Right-click speaker icon in taskbar")
    print(f"   2. Select 'Sounds' or 'Sound settings'")
    print(f"   3. Set your microphone as default under 'Input devices'")
    
    input("\n✅ Press ENTER to start recording... (Speak now, clearly and distinctly!)")
    
    print(f"\n⏺️  RECORDING... Speak now! (will auto-stop after {duration}s)")
    print("-"*80)
    
    # Record with callback for real-time monitoring
    audio_data = []
    levels = []
    
    def audio_callback(indata, frames, time_info, status):
        """Capture audio data"""
        if status:
            print(f"⚠️  Audio status: {status}")
        
        # Extract audio chunk
        chunk = indata[:, 0]
        audio_data.append(chunk.copy())
        
        # Calculate RMS level (0-100 scale)
        rms = np.sqrt(np.mean(chunk**2))
        level = min(100, int(rms * 1000))
        levels.append(level)
        
        # Visual feedback
        bar = "█" * (level // 5) + "░" * ((100-level) // 5)
        print(f"  [{bar}] {level:3d}%", end='\r')
    
    # Stream audio
    try:
        with sd.InputStream(
            channels=1,
            samplerate=sample_rate,
            callback=audio_callback,
            blocksize=4096
        ):
            sd.sleep(duration * 1000)
    except Exception as e:
        print(f"\n❌ Recording error: {e}")
        return None
    
    print("\n" + "-"*80)
    print("✅ Recording completed!")
    
    # Combine audio chunks
    if not audio_data:
        print("❌ No audio data captured!")
        return None
    
    full_audio = np.concatenate(audio_data)
    
    # Save audio
    output_path = Path("data/mic_recording.wav")
    output_path.parent.mkdir(exist_ok=True)
    
    sf.write(str(output_path), full_audio, sample_rate)
    
    file_size = output_path.stat().st_size
    duration_calc = len(full_audio) / sample_rate
    
    print(f"\n📁 Saved to: {output_path}")
    print(f"📊 File size: {file_size / 1024:.1f} KB")
    print(f"⏱️  Duration: {duration_calc:.1f} seconds")
    
    # Analyze audio
    max_level = max(levels) if levels else 0
    avg_level = sum(levels) / len(levels) if levels else 0
    
    print(f"\n📈 Audio Analysis:")
    print(f"   Peak level: {max_level:3d}%")
    print(f"   Average level: {avg_level:3d}%")
    
    if max_level < 20:
        print(f"   ⚠️  WARNING: Audio level very low - may not be detected!")
        print(f"   💡 TIP: Speak louder and closer to microphone")
    elif max_level < 50:
        print(f"   ⚠️  WARNING: Audio level low - check microphone")
        print(f"   💡 TIP: Speak louder or closer to microphone")
    else:
        print(f"   ✅ Audio level good!")
    
    return str(output_path)


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("🎙️  MEDICAL CONSULTATION MICROPHONE TEST")
    print("="*80)
    
    print("\n📝 What to say during recording:")
    print("   Example: 'Patient name is Rohit, age 32. He has throat infection")
    print("   with fever. Diagnosis is bacterial infection. Prescribe erythromycin")
    print("   500mg three times daily for 5 days. Drink warm water and rest.'")
    
    # Record audio
    audio_file = record_with_monitoring(duration=15)
    
    if not audio_file:
        print("❌ Failed to record audio")
        return
    
    # Now process with medical system
    print("\n" + "="*80)
    print("🔄 PROCESSING WITH MEDICAL SYSTEM")
    print("="*80)
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from src.medical_system_v2 import MedicalSystem
        
        system = MedicalSystem()
        print(f"\n⏳ Extracting medical data...")
        
        result = system.process(audio_file)
        prescription = result.get('prescription', {})
        
        print("\n" + "="*80)
        print("✅ RESULTS")
        print("="*80)
        
        if prescription and any(prescription.values()):
            print(f"\n👤 Patient: {prescription.get('patient_name', 'Not captured')}")
            
            if prescription.get('complaints'):
                print(f"\n🔴 Complaints:")
                for c in prescription['complaints']:
                    print(f"   • {c}")
            
            if prescription.get('diagnosis'):
                print(f"\n🔍 Diagnosis:")
                for d in prescription['diagnosis']:
                    print(f"   • {d}")
            
            if prescription.get('medicines'):
                print(f"\n💊 Medicines:")
                for m in prescription['medicines']:
                    print(f"   • {m['name']} {m.get('dose', '')} - {m.get('frequency', '')} for {m.get('duration', '')}")
            
            if prescription.get('advice'):
                print(f"\n📋 Advice:")
                for a in prescription['advice'][:3]:
                    print(f"   • {a}")
        else:
            print("⚠️  No prescription data extracted")
            print("   This may mean:")
            print("   - Audio quality was too low")
            print("   - Microphone wasn't properly selected")
            print("   - No clear speech was recorded")
            print("\n💡 Try again with louder, clear speech!")
        
        # Save results
        results_file = Path("data/mic_full_test_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Full results: {results_file}")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
