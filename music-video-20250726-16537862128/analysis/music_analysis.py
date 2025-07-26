#!/usr/bin/env python3
"""
音楽ファイル詳細分析スクリプト
生成された音楽ファイルを分析して戦略計画書との比較を行う
"""

import os
import sys
import json
import wave
import struct
import math
try:
    import librosa
    import numpy as np
    from scipy import signal
    ADVANCED_ANALYSIS_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYSIS_AVAILABLE = False
    print("Warning: Advanced analysis libraries not available. Performing basic analysis only.")

def analyze_music_file(file_path):
    """音楽ファイルの詳細分析を実行"""
    
    analysis_results = {
        "file_path": file_path,
        "basic_info": {},
        "tempo_analysis": {},
        "instrument_analysis": {},
        "structure_analysis": {},
        "emotion_analysis": {},
        "acoustic_characteristics": {},
        "strategy_comparison": {}
    }
    
    # 基本情報の取得
    analysis_results["basic_info"] = get_basic_audio_info(file_path)
    
    if ADVANCED_ANALYSIS_AVAILABLE:
        # 高度な分析
        y, sr = librosa.load(file_path)
        analysis_results["tempo_analysis"] = analyze_tempo(y, sr)
        analysis_results["instrument_analysis"] = analyze_instruments(y, sr)
        analysis_results["structure_analysis"] = analyze_structure(y, sr)
        analysis_results["emotion_analysis"] = analyze_emotion(y, sr)
        analysis_results["acoustic_characteristics"] = analyze_acoustics(y, sr)
    else:
        # 基本分析のみ
        analysis_results["tempo_analysis"] = basic_tempo_analysis(file_path)
        analysis_results["instrument_analysis"] = basic_instrument_analysis()
        analysis_results["structure_analysis"] = basic_structure_analysis()
        analysis_results["emotion_analysis"] = basic_emotion_analysis()
        analysis_results["acoustic_characteristics"] = basic_acoustic_analysis()
    
    # 戦略との比較
    analysis_results["strategy_comparison"] = compare_with_strategy(analysis_results)
    
    return analysis_results

def get_basic_audio_info(file_path):
    """WAVファイルの基本情報を取得"""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            duration = frames / float(sample_rate)
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            
            return {
                "duration_seconds": round(duration, 2),
                "sample_rate": sample_rate,
                "channels": channels,
                "sample_width": sample_width,
                "total_frames": frames,
                "file_size_mb": round(os.path.getsize(file_path) / (1024*1024), 2)
            }
    except Exception as e:
        return {"error": f"Failed to read basic info: {str(e)}"}

def analyze_tempo(y, sr):
    """テンポとBPMの詳細分析"""
    try:
        # テンポ推定
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        # より詳細なテンポ分析
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        
        # 動的テンポ変化
        tempo_dynamic = librosa.beat.tempo(onset_envelope=librosa.onset.onset_strength(y=y, sr=sr),
                                          sr=sr, aggregate=None)
        
        return {
            "primary_tempo_bpm": float(tempo),
            "tempo_stability": float(np.std(tempo_dynamic)),
            "beat_count": len(beats),
            "onset_count": len(onset_frames),
            "tempo_range": {
                "min": float(np.min(tempo_dynamic)),
                "max": float(np.max(tempo_dynamic)),
                "mean": float(np.mean(tempo_dynamic))
            }
        }
    except Exception as e:
        return {"error": f"Tempo analysis failed: {str(e)}"}

def analyze_instruments(y, sr):
    """楽器構成の分析"""
    try:
        # スペクトログラム分析
        stft = librosa.stft(y)
        magnitude = np.abs(stft)
        
        # 周波数帯域別エネルギー分析
        frequencies = librosa.fft_frequencies(sr=sr)
        
        # 楽器特徴的な周波数帯域
        bass_energy = np.mean(magnitude[frequencies < 250])  # ベース域
        mid_energy = np.mean(magnitude[(frequencies >= 250) & (frequencies < 4000)])  # 中域
        high_energy = np.mean(magnitude[frequencies >= 4000])  # 高域
        
        # スペクトラルセントロイド（音色の明るさ）
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
        
        # MFCC特徴量
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        return {
            "frequency_distribution": {
                "bass_energy": float(bass_energy),
                "mid_energy": float(mid_energy),
                "high_energy": float(high_energy)
            },
            "spectral_centroid_mean": float(np.mean(spectral_centroids)),
            "mfcc_characteristics": {
                "mfcc_mean": [float(x) for x in np.mean(mfccs, axis=1)],
                "mfcc_variance": [float(x) for x in np.var(mfccs, axis=1)]
            },
            "instrument_likelihood": estimate_instruments(magnitude, frequencies)
        }
    except Exception as e:
        return {"error": f"Instrument analysis failed: {str(e)}"}

def estimate_instruments(magnitude, frequencies):
    """楽器の推定"""
    # 簡単な楽器推定ロジック
    bass_presence = np.mean(magnitude[frequencies < 100])
    guitar_presence = np.mean(magnitude[(frequencies >= 80) & (frequencies < 1000)])
    vocal_presence = np.mean(magnitude[(frequencies >= 200) & (frequencies < 2000)])
    percussion_presence = np.mean(magnitude[frequencies > 2000])
    
    return {
        "acoustic_guitar_likelihood": float(guitar_presence / np.max(magnitude)),
        "vocal_likelihood": float(vocal_presence / np.max(magnitude)),
        "bass_likelihood": float(bass_presence / np.max(magnitude)),
        "percussion_likelihood": float(percussion_presence / np.max(magnitude))
    }

def analyze_structure(y, sr):
    """音楽構造の分析"""
    try:
        # セグメンテーション
        boundaries = librosa.segment.agglomerative(librosa.feature.mfcc(y=y, sr=sr), k=4)
        boundary_times = librosa.frames_to_time(boundaries, sr=sr)
        
        # エネルギー変化
        rms = librosa.feature.rms(y=y)
        energy_changes = np.diff(rms[0])
        
        duration = len(y) / sr
        
        return {
            "total_duration": float(duration),
            "segment_boundaries": [float(t) for t in boundary_times],
            "estimated_structure": estimate_song_structure(boundary_times, duration),
            "energy_variation": float(np.std(energy_changes)),
            "dynamic_range": float(np.max(rms) - np.min(rms))
        }
    except Exception as e:
        return {"error": f"Structure analysis failed: {str(e)}"}

def estimate_song_structure(boundaries, duration):
    """楽曲構造の推定"""
    if len(boundaries) >= 3:
        return {
            "intro": f"0.0 - {boundaries[0]:.1f}s",
            "verse": f"{boundaries[0]:.1f} - {boundaries[1]:.1f}s",
            "chorus": f"{boundaries[1]:.1f} - {boundaries[2]:.1f}s",
            "outro": f"{boundaries[2]:.1f} - {duration:.1f}s"
        }
    else:
        return {"structure": "Unable to detect clear structure"}

def analyze_emotion(y, sr):
    """感情・雰囲気の分析"""
    try:
        # 音響特徴量による感情分析
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        
        # テンポベースの感情推定
        tempo = librosa.beat.tempo(y=y, sr=sr)[0]
        
        return {
            "harmonic_complexity": float(np.mean(np.var(chroma, axis=1))),
            "tonal_stability": float(np.mean(tonnetz)),
            "spectral_contrast": float(np.mean(spectral_contrast)),
            "estimated_mood": estimate_mood(tempo, np.mean(chroma), np.mean(spectral_contrast)),
            "energy_level": classify_energy_level(np.mean(librosa.feature.rms(y=y)))
        }
    except Exception as e:
        return {"error": f"Emotion analysis failed: {str(e)}"}

def estimate_mood(tempo, harmonic_complexity, spectral_contrast):
    """ムードの推定"""
    if tempo < 100:
        if harmonic_complexity > 0.3:
            return "contemplative_warm"
        else:
            return "calm_gentle"
    elif tempo < 120:
        if spectral_contrast > 0.5:
            return "uplifting_positive"
        else:
            return "moderate_steady"
    else:
        return "energetic_dynamic"

def classify_energy_level(rms_mean):
    """エネルギーレベルの分類"""
    if rms_mean < 0.1:
        return "low_intimate"
    elif rms_mean < 0.3:
        return "moderate_balanced"
    else:
        return "high_energetic"

def analyze_acoustics(y, sr):
    """音響特性の詳細分析"""
    try:
        # 基本的な音響パラメータ
        rms = librosa.feature.rms(y=y)
        zcr = librosa.feature.zero_crossing_rate(y)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        
        return {
            "rms_energy": {
                "mean": float(np.mean(rms)),
                "std": float(np.std(rms)),
                "max": float(np.max(rms))
            },
            "zero_crossing_rate": float(np.mean(zcr)),
            "spectral_bandwidth": float(np.mean(spectral_bandwidth)),
            "spectral_rolloff": float(np.mean(spectral_rolloff)),
            "frequency_analysis": analyze_frequency_content(y, sr)
        }
    except Exception as e:
        return {"error": f"Acoustic analysis failed: {str(e)}"}

def analyze_frequency_content(y, sr):
    """周波数特性の分析"""
    # FFT解析
    fft = np.fft.fft(y)
    magnitude = np.abs(fft)
    frequencies = np.fft.fftfreq(len(fft), 1/sr)
    
    # 正の周波数のみ使用
    positive_freq_idx = frequencies > 0
    frequencies = frequencies[positive_freq_idx]
    magnitude = magnitude[positive_freq_idx]
    
    # 周波数帯域別の解析
    low_freq = magnitude[frequencies < 500]
    mid_freq = magnitude[(frequencies >= 500) & (frequencies < 4000)]
    high_freq = magnitude[frequencies >= 4000]
    
    return {
        "dominant_frequency": float(frequencies[np.argmax(magnitude)]),
        "low_freq_energy": float(np.mean(low_freq)),
        "mid_freq_energy": float(np.mean(mid_freq)),
        "high_freq_energy": float(np.mean(high_freq)),
        "frequency_balance": "low_heavy" if np.mean(low_freq) > np.mean(mid_freq) else "mid_heavy"
    }

def compare_with_strategy(analysis_results):
    """戦略計画書との比較分析"""
    strategy_specs = {
        "target_tempo_range": [90, 110],
        "target_duration_range": [30, 40],
        "target_genre": "indie_pop_acoustic",
        "target_instruments": ["acoustic_guitar", "light_percussion", "simple_bass"],
        "target_mood": "youthful_warm_dreamy"
    }
    
    comparison = {
        "tempo_match": False,
        "duration_match": False,
        "genre_characteristics": {},
        "instrument_alignment": {},
        "mood_alignment": {},
        "overall_alignment_score": 0.0,
        "recommendations": []
    }
    
    # テンポ比較
    if "primary_tempo_bpm" in analysis_results.get("tempo_analysis", {}):
        tempo = analysis_results["tempo_analysis"]["primary_tempo_bpm"]
        if strategy_specs["target_tempo_range"][0] <= tempo <= strategy_specs["target_tempo_range"][1]:
            comparison["tempo_match"] = True
        else:
            comparison["recommendations"].append(f"テンポ調整が必要: 現在{tempo:.1f}BPM → 目標90-110BPM")
    
    # 長さ比較
    if "duration_seconds" in analysis_results.get("basic_info", {}):
        duration = analysis_results["basic_info"]["duration_seconds"]
        if strategy_specs["target_duration_range"][0] <= duration <= strategy_specs["target_duration_range"][1]:
            comparison["duration_match"] = True
        else:
            comparison["recommendations"].append(f"長さ調整が必要: 現在{duration}秒 → 目標30-40秒")
    
    # 楽器構成比較
    if "instrument_likelihood" in analysis_results.get("instrument_analysis", {}):
        instruments = analysis_results["instrument_analysis"]["instrument_likelihood"]
        guitar_score = instruments.get("acoustic_guitar_likelihood", 0)
        comparison["instrument_alignment"]["acoustic_guitar"] = guitar_score > 0.3
        if guitar_score <= 0.3:
            comparison["recommendations"].append("アコースティックギターの要素を強化")
    
    # 総合スコア計算
    score_components = [
        comparison["tempo_match"],
        comparison["duration_match"],
        comparison["instrument_alignment"].get("acoustic_guitar", False)
    ]
    comparison["overall_alignment_score"] = sum(score_components) / len(score_components)
    
    return comparison

# 基本分析関数（ライブラリが利用できない場合）
def basic_tempo_analysis(file_path):
    return {"note": "Advanced tempo analysis requires librosa library"}

def basic_instrument_analysis():
    return {"note": "Advanced instrument analysis requires librosa library"}

def basic_structure_analysis():
    return {"note": "Advanced structure analysis requires librosa library"}

def basic_emotion_analysis():
    return {"note": "Advanced emotion analysis requires librosa library"}

def basic_acoustic_analysis():
    return {"note": "Advanced acoustic analysis requires librosa library"}

if __name__ == "__main__":
    file_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250726-16537862128/music/generated-music.wav"
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    print("音楽ファイル分析を開始...")
    results = analyze_music_file(file_path)
    
    # 結果を整理してレポート形式で出力
    print("\n" + "="*60)
    print("音楽ファイル詳細分析レポート")
    print("="*60)
    
    # 基本情報
    if "basic_info" in results:
        print(f"\n【基本情報】")
        basic = results["basic_info"]
        if "error" not in basic:
            print(f"再生時間: {basic['duration_seconds']}秒")
            print(f"サンプルレート: {basic['sample_rate']}Hz")
            print(f"チャンネル数: {basic['channels']}")
            print(f"ファイルサイズ: {basic['file_size_mb']}MB")
    
    # テンポ分析
    if "tempo_analysis" in results:
        print(f"\n【テンポ・BPM分析】")
        tempo = results["tempo_analysis"]
        if "error" not in tempo and "primary_tempo_bpm" in tempo:
            print(f"主要BPM: {tempo['primary_tempo_bpm']:.1f}")
            if "tempo_range" in tempo:
                range_info = tempo["tempo_range"]
                print(f"テンポ範囲: {range_info['min']:.1f} - {range_info['max']:.1f} BPM")
                print(f"平均テンポ: {range_info['mean']:.1f} BPM")
            print(f"テンポ安定性: {tempo.get('tempo_stability', 'N/A')}")
        else:
            print(tempo.get("note", tempo.get("error", "分析できませんでした")))
    
    # 楽器構成
    if "instrument_analysis" in results:
        print(f"\n【楽器構成分析】")
        instruments = results["instrument_analysis"]
        if "error" not in instruments and "instrument_likelihood" in instruments:
            likelihood = instruments["instrument_likelihood"]
            print(f"アコースティックギター: {likelihood.get('acoustic_guitar_likelihood', 0):.2f}")
            print(f"ボーカル: {likelihood.get('vocal_likelihood', 0):.2f}")
            print(f"ベース: {likelihood.get('bass_likelihood', 0):.2f}")
            print(f"パーカッション: {likelihood.get('percussion_likelihood', 0):.2f}")
            
            if "frequency_distribution" in instruments:
                freq = instruments["frequency_distribution"]
                print(f"周波数分布 - 低域: {freq['bass_energy']:.3f}, 中域: {freq['mid_energy']:.3f}, 高域: {freq['high_energy']:.3f}")
        else:
            print(instruments.get("note", instruments.get("error", "分析できませんでした")))
    
    # 音楽構造
    if "structure_analysis" in results:
        print(f"\n【音楽構造分析】")
        structure = results["structure_analysis"]
        if "error" not in structure and "estimated_structure" in structure:
            est_struct = structure["estimated_structure"]
            if isinstance(est_struct, dict) and "intro" in est_struct:
                print(f"イントロ: {est_struct['intro']}")
                print(f"バース: {est_struct['verse']}")
                print(f"サビ: {est_struct['chorus']}")
                print(f"アウトロ: {est_struct['outro']}")
            else:
                print("明確な構造の検出ができませんでした")
        else:
            print(structure.get("note", structure.get("error", "分析できませんでした")))
    
    # 感情・雰囲気
    if "emotion_analysis" in results:
        print(f"\n【雰囲気・感情分析】")
        emotion = results["emotion_analysis"]
        if "error" not in emotion and "estimated_mood" in emotion:
            print(f"推定ムード: {emotion['estimated_mood']}")
            print(f"エネルギーレベル: {emotion['energy_level']}")
            print(f"和声複雑度: {emotion.get('harmonic_complexity', 'N/A')}")
        else:
            print(emotion.get("note", emotion.get("error", "分析できませんでした")))
    
    # 戦略比較
    if "strategy_comparison" in results:
        print(f"\n【戦略計画書との比較】")
        comparison = results["strategy_comparison"]
        print(f"テンポ適合: {'✓' if comparison['tempo_match'] else '✗'}")
        print(f"長さ適合: {'✓' if comparison['duration_match'] else '✗'}")
        print(f"総合適合スコア: {comparison['overall_alignment_score']:.2f}")
        
        if comparison["recommendations"]:
            print(f"\n【改善提案】")
            for i, rec in enumerate(comparison["recommendations"], 1):
                print(f"{i}. {rec}")
    
    # JSON出力
    output_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250726-16537862128/analysis/detailed_music_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n詳細な分析結果は以下に保存されました: {output_file}")