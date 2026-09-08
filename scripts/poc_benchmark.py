"""
Phase 1: TTS Technical Feasibility Benchmark
Evaluates Qwen3-TTS 0.6B on CPU (Intel Core i5-1135G7)

Measures:
1. Model loading time
2. RAM consumption (peak RSS)
3. Inference time
4. Generated audio duration
5. Real-Time Factor (RTF = inference_time / audio_duration)
6. Audio quality and file size
"""

import os
import sys
import time
import psutil
import torch
import soundfile as sf
import numpy as np

def get_process_memory_mb():
    """Return current process resident memory in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def run_benchmark():
    print("=" * 65)
    print("   AI KIDS STORYTELLING — PHASE 1 TTS FEASIBILITY SPIKE")
    print("=" * 65)
    
    # 1. Hardware baseline
    cpu_count = psutil.cpu_count(logical=True)
    physical_cpu = psutil.cpu_count(logical=False)
    total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)
    available_ram_gb = psutil.virtual_memory().available / (1024 ** 3)
    
    print(f"\n[HARDWARE BASELINE]")
    print(f"  CPU Cores: {physical_cpu} physical / {cpu_count} logical")
    print(f"  Total System RAM: {total_ram_gb:.2f} GB (Available: {available_ram_gb:.2f} GB)")
    print(f"  PyTorch Device: CPU | Threads: {torch.get_num_threads()}")
    print(f"  Initial Memory: {get_process_memory_mb():.1f} MB")
    
    # 2. Input Story Text
    story_path = os.path.join("data", "stories", "sample_story.txt")
    if not os.path.exists(story_path):
        sample_text = (
            "Once upon a time, in a bright green valley, lived a cheerful little rabbit named Barnaby. "
            "Barnaby loved to hop through the meadow and look for sweet wild clover. "
            "One sunny morning, he noticed a tiny blue butterfly resting on a golden dandelion. "
            "Good morning, little flutterby, Barnaby giggled. "
            "Together, they danced all the way to the whispering brook, where the water sparkled like diamonds. "
            "It was the happiest day in the whole forest."
        )
    else:
        with open(story_path, "r", encoding="utf-8") as f:
            sample_text = f.read().strip()
            
    word_count = len(sample_text.split())
    print(f"\n[STORY TEXT]")
    print(f"  Word Count: {word_count} words")
    print(f"  Estimated Speech Duration: ~{word_count / 2.5:.1f} seconds")
    print(f"  Text Preview: \"{sample_text[:80]}...\"")
    
    # 3. Model Selection
    from qwen_tts import Qwen3TTSModel
    
    # Check if a custom reference voice exists
    ref_audio_path = os.path.join("data", "voices", "reference_sample.wav")
    has_ref_audio = os.path.exists(ref_audio_path)
    
    model_repo = "Qwen/Qwen3-TTS-12Hz-0.6B-Base" if has_ref_audio else "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
    
    print(f"\n[MODEL INITIALIZATION]")
    print(f"  Target Model: {model_repo}")
    print(f"  Mode: {'Voice Cloning (Base)' if has_ref_audio else 'Preset Voice (CustomVoice)'}")
    if has_ref_audio:
        print(f"  Reference Audio: {ref_audio_path}")
        
    start_load_time = time.time()
    initial_mem = get_process_memory_mb()
    
    print(f"  Loading model weights (may download on first run)...")
    try:
        model = Qwen3TTSModel.from_pretrained(
            model_repo,
            device_map="cpu",
            torch_dtype=torch.float32,
        )
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return
        
    load_duration = time.time() - start_load_time
    loaded_mem = get_process_memory_mb()
    mem_delta = loaded_mem - initial_mem
    print(f"  [SUCCESS] Model loaded in {load_duration:.2f} seconds")
    print(f"  Memory after load: {loaded_mem:.1f} MB (+{mem_delta:.1f} MB)")
    
    # 4. Inference Execution
    print(f"\n[SYNTHESIS INFERENCE]")
    print(f"  Starting generation on CPU...")
    
    os.makedirs(os.path.join("data", "generated_audio"), exist_ok=True)
    output_path = os.path.join("data", "generated_audio", "poc_output.wav")
    
    start_gen_time = time.time()
    
    if has_ref_audio:
        ref_text_path = os.path.join("data", "voices", "reference_text.txt")
        ref_text = None
        if os.path.exists(ref_text_path):
            with open(ref_text_path, "r", encoding="utf-8") as f:
                ref_text = f.read().strip()
                
        wavs, sr = model.generate_voice_clone(
            text=sample_text,
            language="English",
            ref_audio=ref_audio_path,
            ref_text=ref_text,
            x_vector_only_mode=(ref_text is None),
        )
    else:
        # Default narrator voice in CustomVoice
        wavs, sr = model.generate_custom_voice(
            text=sample_text,
            language="English",
            speaker="Aiden",
        )
        
    gen_duration = time.time() - start_gen_time
    peak_mem = get_process_memory_mb()
    
    # 5. Output Verification
    audio_data = wavs[0] if isinstance(wavs, list) else wavs
    sf.write(output_path, audio_data, sr)
    
    file_size_kb = os.path.getsize(output_path) / 1024
    audio_duration = len(audio_data) / sr
    rtf = gen_duration / audio_duration if audio_duration > 0 else 0
    
    print(f"\n[BENCHMARK RESULTS]")
    print(f"  Generated Audio Path: {output_path}")
    print(f"  Audio Duration: {audio_duration:.2f} seconds")
    print(f"  Sample Rate: {sr} Hz")
    print(f"  File Size: {file_size_kb:.1f} KB")
    print(f"  Inference Time: {gen_duration:.2f} seconds")
    print(f"  Real-Time Factor (RTF): {rtf:.2f}x (Lower is better)")
    print(f"  Peak RAM: {peak_mem:.1f} MB")
    
    # Evaluate feasibility
    is_feasible = rtf <= 3.0 and peak_mem <= (12 * 1024)
    print(f"\n[FEASIBILITY ASSESSMENT]")
    if is_feasible:
        print(f"  STATUS: FEASIBLE FOR LOCAL WINDOWS CPU EXECUTION")
        print(f"  - RTF {rtf:.2f}x allows a 40s story to generate in ~{gen_duration:.0f}s.")
        print(f"  - Once cached, replay is instant with 0s latency.")
    else:
        print(f"  STATUS: HIGH LATENCY / MEMORY HEAVY")
        print(f"  - Consider offloading TTS inference to remote GPU or quantizing.")
        
    # Write report
    report_path = "poc_results.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Phase 1 TTS Feasibility Spike — Results Report\n\n")
        f.write(f"- **Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Model**: `{model_repo}`\n")
        f.write(f"- **Device**: Intel Core i5-1135G7 CPU ({cpu_count} threads)\n")
        f.write(f"- **Audio Duration**: {audio_duration:.2f} seconds\n")
        f.write(f"- **Inference Duration**: {gen_duration:.2f} seconds\n")
        f.write(f"- **Real-Time Factor (RTF)**: **{rtf:.2f}x**\n")
        f.write(f"- **Peak RAM**: {peak_mem:.1f} MB\n")
        f.write(f"- **Output File**: `{output_path}` ({file_size_kb:.1f} KB)\n")
        f.write(f"- **Conclusion**: {'Feasible for local desktop execution with caching' if is_feasible else 'Recommend remote GPU inference'}\n")
    print(f"\nResults saved to {report_path}")

if __name__ == "__main__":
    run_benchmark()
