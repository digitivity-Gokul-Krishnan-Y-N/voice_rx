"""
Medical System with Live Microphone Recording
Records from mic and extracts prescription data
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import numpy as np

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, 'src')

# Import audio libraries
try:
    import sounddevice as sd
    import soundfile as sf
except ImportError:
    print("📦 Installing audio libraries...")
    os.system("pip install sounddevice soundfile -q")
    import sounddevice as sd
    import soundfile as sf

from medical_system_v2 import MedicalSystem

def record_live_consultation(sample_rate=16000):
    """Record live medical consultation from microphone (user-controlled duration)"""
    output_file = Path("data/live_recording.wav")
    output_file.parent.mkdir(exist_ok=True)
    
    print("\n" + "="*80)
    print("🎤 LIVE MICROPHONE RECORDING - MEDICAL CONSULTATION")
    print("="*80)
    
    print(f"\n📌 What to say (example):")
    print("   'Patient Rohit, age 32, has throat infection with fever.'")
    print("   'Diagnosis is bacterial throat infection. Prescribe erythromycin'")
    print("   '500 mg three times daily for 5 days. Drink warm water and rest.'")
    
    print(f"\n📊 Sample Rate: {sample_rate} Hz")
    print(f"⏱️  Duration: User-controlled (speak as long as needed)")
    
    input("\n✅ Press ENTER to START recording...")
    
    print(f"\n⏺️  RECORDING NOW... Speak clearly and fully!")
    print("💬 You can speak for as long as needed (no time limit)")
    print("⏹️  Press CTRL+C to STOP recording when done")
    print("-"*80)
    print()
    
    try:
        # Record audio with real-time level monitoring
        audio_data = []
        max_level = 0
        recording_started = datetime.now()
        
        def audio_callback(indata, frames, time_info, status):
            nonlocal max_level
            if status:
                print(f"⚠️  {status}")
            
            chunk = indata[:, 0]
            audio_data.append(chunk.copy())
            
            # Calculate RMS level
            rms = np.sqrt(np.mean(chunk**2))
            level = min(100, int(rms * 1000))
            max_level = max(max_level, level)
            
            # Visual feedback with elapsed time
            elapsed = (datetime.now() - recording_started).total_seconds()
            bar = "█" * (level // 5) + "░" * ((100-level) // 5)
            print(f"  ⏱️  {elapsed:.0f}s | [{bar}] {level:3d}%", end='\r')
        
        # Stream recording - runs until user stops (Ctrl+C)
        print("Recording started... speak now!")
        with sd.InputStream(channels=1, samplerate=sample_rate, callback=audio_callback, blocksize=4096):
            # Keep recording until user interrupts
            while True:
                sd.sleep(100)  # Check every 100ms
        
    except KeyboardInterrupt:
        # User pressed Ctrl+C to stop
        pass
    except Exception as e:
        print(f"\n❌ Recording error: {e}")
        return None
    
    try:
        # Combine audio chunks
        if not audio_data:
            print("\n❌ No audio captured!")
            return None
        
        full_audio = np.concatenate(audio_data)
        
        # Save to file
        sf.write(str(output_file), full_audio, sample_rate)
        
        file_size = output_file.stat().st_size
        duration_calc = len(full_audio) / sample_rate
        
        print("\n" + "-"*80)
        print(f"✅ Recording stopped!")
        print(f"📁 Saved: {output_file}")
        print(f"📊 File size: {file_size / 1024:.1f} KB")
        print(f"⏱️  Duration: {duration_calc:.1f} seconds")
        print(f"📈 Peak level: {max_level}%")
        
        if max_level < 20:
            print(f"⚠️  WARNING: Audio level very low!")
            print(f"💡 Microphone might not be working properly")
        
        return str(output_file)
        
    except Exception as e:
        print(f"\n❌ Error saving recording: {e}")
        return None


def process_consultation(audio_file, language=None):
    """Process recorded consultation with medical system"""

    print("\n" + "="*80)
    print("🔄 PROCESSING MEDICAL CONSULTATION")
    print("="*80)

    try:
        system = MedicalSystem()
        print(f"\n⏳ Extracting prescription data...\n")

        result = system.process(audio_file, language=language)

        # Extract prescription
        diagnosis = result.get('diagnosis', [])
        medicines = result.get('medicines', [])
        advice = result.get('advice', [])

        # Summary
        print("\n" + "="*80)
        print("✅ PRESCRIPTION SUMMARY")
        print("="*80)
        
        print(f"\n📋 Patient: {result.get('patient_name') or 'Not captured'}")
        print(f"📈 Extraction Quality: {result.get('confidence', 0):.0%}")
        print(f"🔍 Method: {result.get('extraction_method') or 'Unknown'}")
        
        if diagnosis:
            print(f"\n🔴 Diagnosis: {', '.join(diagnosis)}")
        
        if medicines:
            print(f"\n💊 Medicines ({len(medicines)} items):")
            for med in medicines:
                if isinstance(med, dict):
                    name = med.get('name') or 'Unknown'
                    dose = med.get('dose') or ''
                    freq = med.get('frequency') or ''
                    duration = med.get('duration') or ''
                    print(f"   • {name} {dose} - {freq} {f'for {duration}' if duration else ''}")
                else:
                    print(f"   • {med}")
        
        if advice:
            print(f"\n📋 Advice ({len(advice)} items):")
            for i, adv in enumerate(advice, 1):
                print(f"   {i}. {adv}")
        
        # Save full results
        results_file = Path("data/live_consultation_result.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full results saved: {results_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Processing error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point - live recording + processing"""
    
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  MEDICAL CONSULTATION SYSTEM - LIVE RECORDING MODE".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)

    # Record from microphone
    audio_file = record_live_consultation()

    if not audio_file:
        print("❌ Recording failed. Exiting.")
        return

    # Process recording (auto-detects language from audio)
    result = process_consultation(audio_file, language=None)
    
    if result:
        print("\n" + "="*80)
        print("✅ CONSULTATION PROCESSING COMPLETE")
        print("="*80)
        print(f"📁 Recording: {audio_file}")
        print(f"📄 Results: data/live_consultation_result.json")
    else:
        print("\n❌ Processing failed")
    
    print("\n" + "█"*80 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
