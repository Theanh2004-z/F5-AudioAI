# F5-TTS INFERENCE PIPELINE: DEPENDENCY GRAPH
*(Reverse Engineering Document - No Optimization)*

The following Mermaid graph outlines the data flow and parameter dependencies during the inference execution.

```mermaid
graph TD
    %% Inputs
    AudioIn[Reference Audio] --> Utils(utils_infer.py: infer_batch_process)
    TextIn[Reference Text + Generated Text] --> Utils
    
    %% Pre-Processing Levers
    subgraph PreProcessing [1. Pre-Processing & Batching]
        L_RMS[target_rms] -.->|Scales Amplitude| Utils
        L_Speed[speed_ratio] -.->|Scales Target Duration| Utils
        L_Crossfade[cross_fade_duration] -.->|Mixes Chunks| Utils
    end
    
    %% Main Output from Pre-processing
    Utils -->|duration, cond_audio, text_tokens| CFM(cfm.py: CFM.sample)
    
    %% CFM Levers
    subgraph FlowMatching [2. Conditional Flow Matching]
        L_Steps[nfe_step] -.->|Defines Integration Steps| CFM
        L_CFG[cfg_strength] -.->|Amplifies Condition| CFM
        L_Sway[sway_sampling_coef] -.->|Warps Time Schedule| CFM
        L_EditMask[edit_mask] -.->|Freezes Segments| CFM
        
        %% Inter-lever dependencies
        L_Steps -.->|Constrains granularity of| L_Sway
    end
    
    %% DiT Core
    CFM -->|x_t, t, cond, text| DiT(dit.py: DiT.forward)
    
    subgraph DiTBlock [3. Diffusion Transformer Backbone]
        L_DropCond[drop_audio_cond] -.->|Null Branch| DiT
        L_DropText[drop_text] -.->|Null Branch| DiT
        Rope[Rotary Embedding] -.-> DiT
        
        %% Inter-lever dependencies
        L_CFG -.->|Requires execution of| L_DropCond
        L_CFG -.->|Requires execution of| L_DropText
    end
    
    %% Feedback Loop for ODE
    DiT -->|Velocity Prediction| CFM
    
    %% Output
    CFM -->|Predicted Spectrogram| Vocoder(Vocoder: BigVGAN/Vocos)
    Vocoder --> Output[Generated Audio]
    
    %% Final Post-processing
    L_RMS -.->|Inverse Scaling| Output
```

## Graph Analysis
1. **The Pre-Processing Layer** (`target_rms`, `speed_ratio`) runs strictly outside the neural network. Modifying these is mathematically safe and purely deterministic.
2. **The Flow Matching Layer** (`nfe_step`, `cfg_strength`, `sway_sampling_coef`) controls the iterative synthesis loop. Changes here dramatically affect the physical generation dynamics.
3. **The DiT Core** contains static weights and routing booleans. Interventions here (other than CFG routing) risk destroying the pre-trained manifold.
