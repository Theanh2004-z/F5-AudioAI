import matplotlib.pyplot as plt
import numpy as np

def generate_dashboard(ref_arrays, gen_arrays, ref_scalars, gen_scalars, output_path):
    """
    Generates a 6-panel visualization dashboard:
    1 Pitch | 2 Energy
    3 Speech Timeline | 4 Silence Timeline
    5 Spectral Overview | 6 Summary Table
    """
    fig = plt.figure(figsize=(18, 12))
    
    # 1. Pitch
    ax1 = plt.subplot(3, 2, 1)
    ax1.set_title("1. Pitch Contour (F0)")
    ax1.plot(ref_arrays['f0_contour'], label="Ref", alpha=0.7)
    ax1.plot(gen_arrays['f0_contour'], label="Gen", alpha=0.7)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Energy
    ax2 = plt.subplot(3, 2, 2)
    ax2.set_title("2. Energy Contour (RMS)")
    ax2.plot(ref_arrays['rms_contour'], label="Ref", alpha=0.7)
    ax2.plot(gen_arrays['rms_contour'], label="Gen", alpha=0.7)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Speech Timeline
    ax3 = plt.subplot(3, 2, 3)
    ax3.set_title("3. Speech Timeline")
    ax3.plot(ref_arrays['timeline_mask'], label="Ref", drawstyle='steps-pre', alpha=0.7)
    ax3.plot(gen_arrays['timeline_mask'], label="Gen", drawstyle='steps-pre', alpha=0.7)
    ax3.set_ylim(-0.1, 1.1)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Silence Timeline (Inverted Speech Mask)
    ax4 = plt.subplot(3, 2, 4)
    ax4.set_title("4. Silence Timeline")
    ref_silence = 1.0 - np.array(ref_arrays['timeline_mask'])
    gen_silence = 1.0 - np.array(gen_arrays['timeline_mask'])
    ax4.plot(ref_silence, label="Ref", drawstyle='steps-pre', alpha=0.7)
    ax4.plot(gen_silence, label="Gen", drawstyle='steps-pre', alpha=0.7)
    ax4.set_ylim(-0.1, 1.1)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Spectral Overview
    ax5 = plt.subplot(3, 2, 5)
    ax5.set_title("5. Spectral Centroid Contour")
    ax5.plot(ref_arrays['centroid_contour'], label="Ref", alpha=0.7)
    ax5.plot(gen_arrays['centroid_contour'], label="Gen", alpha=0.7)
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Summary Table
    ax6 = plt.subplot(3, 2, 6)
    ax6.axis('tight')
    ax6.axis('off')
    ax6.set_title("6. Feature Summary (Means)")
    
    col_labels = ['Metric', 'Reference', 'Generated']
    table_data = [
        ['Pitch Mean (Hz)', f"{ref_scalars['pitch_f0_mean']:.2f}", f"{gen_scalars['pitch_f0_mean']:.2f}"],
        ['Energy Peak', f"{ref_scalars['energy_peak']:.4f}", f"{gen_scalars['energy_peak']:.4f}"],
        ['Speech Rate', f"{ref_scalars['rhythm_speech_rate']:.2f}", f"{gen_scalars['rhythm_speech_rate']:.2f}"],
        ['Pause Count', f"{ref_scalars['rhythm_pause_count']}", f"{gen_scalars['rhythm_pause_count']}"],
        ['Spectral Centroid', f"{ref_scalars['spectral_centroid_mean']:.2f}", f"{gen_scalars['spectral_centroid_mean']:.2f}"],
        ['Zero Crossing', f"{ref_scalars['vq_zero_crossing_rate']:.4f}", f"{gen_scalars['vq_zero_crossing_rate']:.4f}"]
    ]
    
    table = ax6.table(cellText=table_data, colLabels=col_labels, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
