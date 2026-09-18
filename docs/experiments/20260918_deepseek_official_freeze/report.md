# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向长序列和音乐结构建模的生成模型研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-18T09:05:54+08:00 |
| 查新范围 | Transformer、注意力机制、高效Transformer、稀疏注意力机制、长序
列、音乐生成、音乐结构、attention、efficient Transformer、sparse attention、long sequence、music generation、music structure |

---

## 一、查新目的

随着深度学习迅速发展，利用深度神经网络进行艺术的创作已经成为当今
热门研究方向，自动创作音乐是其中的重要组成部分。最近几年，Transformer
及其变体模型被越来越多地应用于音乐生成中，但这样做有两个普遍存在的挑
战：首先，音乐的序列通常很长（超过10000 个token），这使得二次复杂度的
全注意力机制很难胜任；其次，音乐具有独特的重复结构，而现有方法并未针
对这一特点进行建模，在生成具有很好结构的音乐方面有所欠缺。
本文研究针对音乐生成的长序列建模和音乐结构建模的方法，提出
Museformer 模型，这是一种结合细粒度和粗粒度注意力的Transformer 变体模
型。具体来说，通过细粒度注意力机制，每个token 直接关注到与音乐结构最
相关的小节的所有token；通过粗粒度注意力机制，每个token 只关注到其他小
结的总结信息，而不是每一个具体的token，以减少计算成本。本文提出使用相
似度统计的方法以探究音乐的结构，并据此结果来确定结构相关小节，同时利
用区块稀疏等技术做到模型的高效编码实现。Museformer 的优点为：一方面，
细粒度注意力可以重点学习与音乐结构相关的信息，而粗粒度注意力可捕获其
他上下文信息，两者结合使得模型具有良好的效果；另一方面，模型的效率较
高，相较于原始Transformer，具有更低的存储和计算复杂度。
本文开展了全面的实验以探究Museformer 的性能。客观和主观实验的结果
证明Museformer 相比其他模型在生成音乐上具有更高的质量和更好的结构，尤
其是在长距离结构上具有明显优势。与全注意力模型相比，它可以建模超过3
倍长的音乐序列，且具有更快的运行速度。

---

## 二、项目科学技术要点

- 提出一种结合细粒度注意力与粗粒度注意力的Transformer变体模型Museformer，用于音乐生成中的长序列建模。
- 提出使用相似度统计的方法探究音乐结构，并据此确定与结构相关的小节，用于指导细粒度注意力的关注范围。
- 利用区块稀疏等技术实现Museformer模型的高效编码，降低存储和计算复杂度。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种结合细粒度注意力与粗粒度注意力的Transformer变体模型Museformer，用于音乐生成中的长序列建模。 | Proposes Museformer, a Transformer model with a novel fine- and coarse-grained attention for long sequence modeling in music generation. |
| NP-2 | 提出使用相似度统计的方法探究音乐结构，并据此确定与结构相关的小节，用于指导细粒度注意力的关注范围。 | Proposes to use similarity statistics to explore the structures of music, and based on the results to determine the structure-related bars. |
| NP-3 | 利用区块稀疏等技术实现Museformer模型的高效编码，降低存储和计算复杂度。 | Achieves efficient implementation of the model with techniques such as blocksparse, resulting in lower storage and computation complexity. |

---

## 四、查新范围要求

检索范围围绕各查新点的中英文表述及技术特征展开。

---

## 五、文献检索范围及检索策略

### 5.1 检索来源

- arxiv.org
- link.springer.com
- www.nature.com

### 5.2 检索词

- Transformer
- 注意力机制
- 高效Transformer
- 稀疏注意力机制
- 长序
列
- 音乐生成
- 音乐结构
- attention
- efficient Transformer
- sparse attention
- long sequence
- music generation
- music structure

### 5.3 检索式

- **NP-1**
  - `(abs:"fine-grained attention" OR abs:"coarse-grained attention" OR abs:"hierarchical attention") AND (ti:"Museformer" OR ti:"music generation Transformer" OR ti:long AND ti:sequence AND ti:music AND ti:modeling)`（arxiv；有命中）
  - `(abs:"fine-grained attention" OR abs:"coarse-grained attention" OR abs:"hierarchical attention" OR abs:"bar-level attention" OR abs:"structure-aware attention") AND (ti:"Museformer" OR ti:"music generation Transformer" OR ti:long AND ti:sequence AND ti:music AND ti:modeling OR ti:"music transformer" OR ti:"long-context music model")`（arxiv；有命中）
  - `(abs:"fine-grained attention" OR abs:"coarse-grained attention" OR abs:"hierarchical attention" OR abs:"bar-level attention" OR abs:"structure-aware attention")`（arxiv；有命中）
  - `("fine-grained attention" OR "coarse-grained attention" OR "hierarchical attention") AND ("Museformer" OR "music generation Transformer" OR "long sequence music modeling")`（springer；部分成功）
  - `("fine-grained attention" OR "coarse-grained attention" OR "hierarchical attention" OR "bar-level attention" OR "structure-aware attention") AND ("Museformer" OR "music generation Transformer" OR "long sequence music modeling" OR "music transformer" OR "long-context music model")`（springer；部分成功）
  - `("fine-grained attention" OR "coarse-grained attention" OR "hierarchical attention" OR "bar-level attention" OR "structure-aware attention")`（springer；部分成功）
- **NP-2**
  - `(ti:"music structure" OR ti:"musical structure" OR ti:"repetition structure") AND (abs:"similarity statistics" OR abs:"similarity analysis" OR abs:"self-similarity matrix") AND (abs:"structure-related bars" OR abs:"structural bars" OR abs:"bar-level structure") AND (abs:"fine-grained attention" OR abs:"attention mechanism" OR abs:"attention weights")`（arxiv；零命中）
  - `(ti:"music structure" OR ti:"musical structure" OR ti:"repetition structure" OR ti:"song structure" OR ti:"music form" OR ti:"structural segmentation") AND (abs:"similarity statistics" OR abs:"similarity analysis" OR abs:"self-similarity matrix" OR abs:"similarity measure" OR abs:"structural similarity" OR abs:"audio similarity")`（arxiv；有命中）
  - `(ti:"music structure" OR ti:"musical structure" OR ti:"repetition structure" OR ti:"song structure" OR ti:"music form" OR ti:"structural segmentation")`（arxiv；部分成功）
  - `(ti:"music structure" OR ti:"musical structure" OR ti:"repetition structure") AND (abs:"similarity statistics" OR abs:"similarity analysis" OR abs:"self-similarity matrix") AND (abs:"fine-grained attention" OR abs:"attention mechanism" OR abs:"attention weights")`（arxiv；零命中）
  - `(ti:"music structure" OR ti:"musical structure" OR ti:"repetition structure") AND (abs:"similarity statistics" OR abs:"similarity analysis" OR abs:"self-similarity matrix") AND (abs:"structure-related bars" OR abs:"structural bars" OR abs:"bar-level structure") AND (abs:"fine-grained attention" OR abs:"attention mechanism" OR abs:"attention weights")`（arxiv；零命中）
  - `(ti:"music structure" OR ti:"musical structure" OR ti:"repetition structure" OR ti:"song structure" OR ti:"music form" OR ti:"structural segmentation") AND (abs:"similarity statistics" OR abs:"similarity analysis" OR abs:"self-similarity matrix" OR abs:"similarity measure" OR abs:"structural similarity" OR abs:"audio similarity")`（arxiv；有命中）
  - `(ti:"music structure" OR ti:"musical structure" OR ti:"repetition structure" OR ti:"song structure" OR ti:"music form" OR ti:"structural segmentation")`（arxiv；部分成功）
  - `(ti:"music structure" OR ti:"musical structure" OR ti:"repetition structure") AND (abs:"similarity statistics" OR abs:"similarity analysis" OR abs:"self-similarity matrix") AND (abs:"fine-grained attention" OR abs:"attention mechanism" OR abs:"attention weights")`（arxiv；零命中）
  - `("music structure" OR "musical structure" OR "repetition structure") AND ("similarity statistics" OR "similarity analysis" OR "self-similarity matrix") AND ("structure-related bars" OR "structural bars" OR "bar-level structure") AND ("fine-grained attention" OR "attention mechanism" OR "attention weights")`（springer；有命中）
  - `("music structure" OR "musical structure" OR "repetition structure" OR "song structure" OR "music form" OR "structural segmentation") AND ("similarity statistics" OR "similarity analysis" OR "self-similarity matrix" OR "similarity measure" OR "structural similarity" OR "audio similarity")`（springer；部分成功）
  - `("music structure" OR "musical structure" OR "repetition structure" OR "song structure" OR "music form" OR "structural segmentation")`（springer；部分成功）
- **NP-3**
  - `(ti:"Museformer model" OR ti:"music transformer model") AND (abs:"block sparse attention" OR abs:"sparse attention mechanism")`（arxiv；零命中）
  - `(ti:"Museformer model" OR ti:"music transformer model" OR ti:"Museformer" OR ti:"music generation transformer") AND (abs:"block sparse attention" OR abs:"sparse attention mechanism" OR abs:"blocksparse" OR abs:"block-sparse attention" OR abs:"sparse transformer attention")`（arxiv；零命中）
  - `(ti:"Museformer model" OR ti:"music transformer model" OR ti:"Museformer" OR ti:"music generation transformer")`（arxiv；有命中）
  - `(ti:"Museformer model" OR ti:"music transformer model")`（arxiv；零命中）
  - `(ti:"Museformer model" OR ti:"music transformer model" OR ti:"Museformer" OR ti:"music generation transformer")`（arxiv；有命中）
  - `("Museformer model" OR "music transformer model") AND ("block sparse attention" OR "sparse attention mechanism")`（springer；有命中）
  - `("Museformer model" OR "music transformer model" OR "Museformer" OR "music generation transformer") AND ("block sparse attention" OR "sparse attention mechanism" OR "blocksparse" OR "block-sparse attention" OR "sparse transformer attention")`（springer；有命中）
  - `("Museformer model" OR "music transformer model" OR "Museformer" OR "music generation transformer")`（springer；部分成功）

---

## 六、检索结果

### 6.1 检索概况

记录 1 轮检索计划，生成 7 张原始证据卡；通过 6 张，拒绝 1 张。

### 6.2 相关文献

### card_04b222e3936c80ab12be9628 · Museformer: Transformer with Fine- and Coarse-Grained Attention for Music Generation

- 查新点：NP-1
- 主要贡献：The paper proposes Museformer, a Transformer with a novel fine- and coarse-grained attention for symbolic music generation, designed to model long music sequences (over 10,000 tokens) and to better generate musical repetition structures.
- 相关性：1.00
- 置信度：0.98
- 来源：
  - Museformer: Transformer with Fine- and Coarse-Grained Attention for Music Generation：https://arxiv.org/pdf/2210.10349
    - 引文：In this paper, we propose Museformer, a Transformer with a novel fine- and coarse-grained attention for music generation.
    - 位置：artifact art_1a8c528bc80025cb8f47a55f chars:378-499
  - Museformer: Transformer with Fine- and Coarse-Grained Attention for Music Generation：https://arxiv.org/pdf/2210.10349
    - 引文：with the fine-grained attention, a token of a specific bar directly attends to all the tokens of the bars that are most relevant to music structures (e.g., the previous 1st, 2nd, 4th and 8th bars, selected via similarity statistics)
    - 位置：artifact art_1a8c528bc80025cb8f47a55f chars:514-746
  - Museformer: Transformer with Fine- and Coarse-Grained Attention for Music Generation：https://arxiv.org/pdf/2210.10349
    - 引文：with the coarse-grained attention, a token only attends to the summarization of the other bars rather than each token of them so as to reduce the computational cost
    - 位置：artifact art_1a8c528bc80025cb8f47a55f chars:748-912
  - Museformer: Transformer with Fine- and Coarse-Grained Attention for Music Generation：https://arxiv.org/pdf/2210.10349
    - 引文：First, it can capture both music structure-related correlations via the fine-grained attention, and other contextual information via the coarse-grained attention.
    - 位置：artifact art_1a8c528bc80025cb8f47a55f chars:943-1105
  - Museformer: Transformer with Fine- and Coarse-Grained Attention for Music Generation：https://arxiv.org/pdf/2210.10349
    - 引文：Second, it is efficient and can model over 3X longer music sequences compared to its full-attention counterpart.
    - 位置：artifact art_1a8c528bc80025cb8f47a55f chars:1106-1218

### card_55ef84aeb25f008141bc6108 · MusicExtender: Generating Polyphonic Piano Music with Long-term Structures via Similarity-guided Diffusion Inpainting

- 查新点：NP-1
- 主要贡献：MusicExtender is a diffusion-based model for polyphonic piano music generation with long-term structures, using a similarity-based phrase-level structure annotation and a phrase-level autoregressive diffusion-inpainting paradigm.
- 相关性：0.45
- 置信度：0.80
- 来源：
  - MusicExtender: Generating Polyphonic Piano Music with Long-term Structures via Similarity-guided Diffusion Inpainting：10.1007/978-981-92-3410-3_15
    - 引文：a novel music generation model based on piano roll representation and diffusion model, MusicExtender, is proposed to enable polyphonic piano generation with long-term structures
    - 位置：artifact art_ae6773a46dcbeb8106a997e6 chars:706-883
  - MusicExtender: Generating Polyphonic Piano Music with Long-term Structures via Similarity-guided Diffusion Inpainting：10.1007/978-981-92-3410-3_15
    - 引文：Previous studies on structured music generation primarily rely on datasets with annotated structures, which are typically derived from bar- or phrase-level relation identification or similarity computation of melodies or melodies combined with chords.
    - 位置：artifact art_ae6773a46dcbeb8106a997e6 chars:100-351

### card_95030af11d17b35c5d495f01 · MusicExtender: Generating Polyphonic Piano Music with Long-term Structures via Similarity-guided Diffusion Inpainting

- 查新点：NP-2
- 主要贡献：Introduces a generic similarity-based annotation method to annotate musical structures at the phrase level, and a diffusion-inpainting generation model (MusicExtender) that generates polyphonic piano music under external structural conditions, with a structural regularization term.
- 相关性：0.55
- 置信度：0.75
- 来源：
  - MusicExtender: Generating Polyphonic Piano Music with Long-term Structures via Similarity-guided Diffusion Inpainting：10.1007/978-981-92-3410-3_15
    - 引文：Previous studies on structured music generation primarily rely on datasets with annotated structures, which are typically derived from bar- or phrase-level relation identification or similarity computation of melodies or melodies combined with chords.
    - 位置：artifact art_ae6773a46dcbeb8106a997e6 chars:100-351
  - MusicExtender: Generating Polyphonic Piano Music with Long-term Structures via Similarity-guided Diffusion Inpainting：10.1007/978-981-92-3410-3_15
    - 引文：we first devise a generic similarity-based annotation method to annotate musical structures at the phrase level.
    - 位置：artifact art_ae6773a46dcbeb8106a997e6 chars:579-691
  - MusicExtender: Generating Polyphonic Piano Music with Long-term Structures via Similarity-guided Diffusion Inpainting：10.1007/978-981-92-3410-3_15
    - 引文：each phrase is generated under the external structural conditions
    - 位置：artifact art_ae6773a46dcbeb8106a997e6 chars:1040-1105

### card_34c638192c7ea363ab8676e1 · Self-Similarity-Based and Novelty-based loss for music structure analysis

- 查新点：NP-2
- 主要贡献：Proposes a supervised deep-learning approach for music structure analysis (MSA) that jointly learns an encoder whose features yield a self-similarity matrix (SSM) approximating a ground-truth SSM (SSM-loss) and learns convolution kernels that produce a novelty score from the estimated SSM (novelty-loss); also introduces self-attention layers to learn track-relative features.
- 相关性：0.60
- 置信度：0.80
- 来源：
  - Self-Similarity-Based and Novelty-based loss for music structure analysis：https://arxiv.org/pdf/2309.02243
    - 引文：Music Structure Analysis (MSA) is the task aiming at identifying musical segments that compose a music track and possibly label them based on their similarity. In this paper we propose a supervised approach for the task of music boundary detection.
    - 位置：artifact art_1876d660ac46ab8e10416bb9 chars:0-248
  - Self-Similarity-Based and Novelty-based loss for music structure analysis：https://arxiv.org/pdf/2309.02243
    - 引文：We also demonstrate that relative feature learning, through self-attention, is beneficial for the task of MSA.
    - 位置：artifact art_1876d660ac46ab8e10416bb9 chars:587-697
  - Self-Similarity-Based and Novelty-based loss for music structure analysis：https://arxiv.org/pdf/2309.02243
    - 引文：To let each feature 𝐗i\mathbf{X}_{i} “know” about surrounding times features {𝐗1​…​𝐗i−1,𝐗i+1​…​𝐗T}\{\mathbf{X}_{1}\ldots\mathbf{X}_{i-1},\mathbf{X}_{i+1}\ldots\mathbf{X}_{T}\} we introduce layers of  sa (sa) [35] in our encoder
    - 位置：artifact art_923fe91b1d19dca851853ec0 chars:15208-15435

### card_bfba9e34f917663d6f674967 · Visual Overviews for Sheet Music Structure

- 查新点：NP-2
- 主要贡献：Proposes visual augmentation methods for sheet music that map overall similarity between sections or bars to colors using dimensionality reduction or clustering, to help users overview structure, repeating patterns, and segment similarity.
- 相关性：0.40
- 置信度：0.75
- 来源：
  - Visual Overviews for Sheet Music Structure：https://arxiv.org/pdf/2308.06140
    - 引文：we explored mapping the overall similarity between sections or bars to colors.
    - 位置：artifact art_3cfcd862a4df5022da1b4320 chars:219-297
  - Visual Overviews for Sheet Music Structure：https://arxiv.org/pdf/2308.06140
    - 引文：our design supports users in tasks such as analyzing structure, finding repetitions, and determining the similarity of specific segments to others.
    - 位置：artifact art_3cfcd862a4df5022da1b4320 chars:796-943

### card_8446338e8a48e4b8a3e5637c · Enhancing long-term structure in symbolic music generation via a cascaded Skeleton-to-texture framework

- 查新点：NP-3
- 主要贡献：CAST is a framework for long-range symbolic music generation based on explicit skeleton guidance, decoupling generation into macro-harmonic planning and micro-texture filling. It uses MusicBERT to extract semantic skeletons and cross-attention to map them to a MuseFormer generator, and explicitly selects MuseFormer as the baseline because it represents the state-of-the-art in sparse attention mechanisms.
- 相关性：0.55
- 置信度：0.85
- 来源：
  - Enhancing long-term structure in symbolic music generation via a cascaded Skeleton-to-texture framework：10.1038/s41598-026-46750-0
    - 引文：For validation, we selected MuseFormer, which represents the state-of-the-art in sparse attention mechanisms, as the baseline model.
    - 位置：artifact art_30c621ef4b19acf1d7a1b323 chars:929-1061

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 2 | 有证据 |
| NP-2 | 3 | 有证据 |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 不新颖

提出一种结合细粒度注意力与粗粒度注意力的Transformer变体模型Museformer，用于音乐生成中的长序列建模。

**Reviewer 裁定：** 不新颖  
**裁定理由：** 查新点 NP-1 的三项技术特征（细粒度注意力、粗粒度注意力、两者结合以同时捕获音乐结构相关关联与其他上下文信息并建模长序列音乐）已被同一篇文献 wrk_eba9d160fb1590c9de66938d（Museformer 原始论文）的摘要与引言逐项直接公开：模型名称、机制、作用位置与目的均与查新点一致，属作者自述方法。另一篇文献 wrk_4178bf9d843fa126d1677e3e（MusicExtender）仅在'长时程音乐结构建模'目标上部分重合，采用扩散修复与乐句级自回归范式，未涉及 Transformer 细/粗粒度注意力，其三项特征均为未知（未提及不等于未采用），不构成对 NP-1 的公开，也不影响上述结论。故 NP-1 不具新颖性。  
**置信度：** 0.95  
**报告摘要：** 该点主张以细粒度注意力（token 直接关注与音乐结构最相关小节的全部 token）、粗粒度注意力（token 只关注其他小节的总结信息以降低计算成本）及两者结合同时捕获结构相关关联与上下文信息、从而建模长序列音乐。核验到的对照文献在模型名称、两种注意力的关注对象与作用目的、以及“同时捕获结构相关关联与其他上下文信息并支持长序列音乐建模”的机制说明上逐项重合，该点的技术特征已见公开。另有一篇对照文献同样面向长时程音乐结构建模并使用乐句级结构与相似度计算，但采用扩散修复与乐句级自回归范式，未涉及细/粗粒度注意力，不构成对该点的公开，亦不影响上述判断。该点目前无需进一步补充检索。  
**未完成原因：** —  
**高度相关 Work：**
  - wrk_eba9d160fb1590c9de66938d：该 Work 即查新点所述 Museformer 模型的原论文，摘要与引言逐项公开了细粒度注意力、粗粒度注意力及其结合用于长序列音乐生成的全部特征，与 NP-1 完全对应。 (cards: card_04b222e3936c80ab12be9628)
  - wrk_4178bf9d843fa126d1677e3e：同属长时程结构化音乐生成，使用乐句级结构与相似度计算，与查新点'音乐结构相关关联'目标部分重合；但技术路线为扩散修复而非细/粗粒度注意力 Transformer，仅构成部分相关文献，不构成对 NP-1 的公开。 (cards: card_55ef84aeb25f008141bc6108)

**原文核验证据：**
  - rev_ev_29f6f1e4a2282a3638a917a2 · wrk_eba9d160fb1590c9de66938d · art_1a8c528bc80025cb8f47a55f [300, 1367): xisting models have shortcomings in generating musical repetition structures. In this paper, we propose Museformer, a Transformer with a novel fine- and coarse-grained attention for music generation. Specifically, with the fine-grained attention, a token of a specific bar directly attends to all the tokens of the bars that are most relevant to music structures (e.g., the previous 1st, 2nd, 4th and 8th bars, selected via similarity statistics); with the coarse-grained attention, a token only attends to the summarization of the other bars rather than each token of them so as to reduce the computational cost. The advantages are two-fold. First, it can capture both music structure-related correlations via the fine-grained attention, and other contextual information via the coarse-grained attention. Second, it is efficient and can model over 3X longer music sequences compared to its full-attention counterpart. Both objective and subjective experimental results demonstrate its ability to generate long music sequences with high quality and better structures.
  - rev_ev_83bf45ec042590abc38781e1 · wrk_eba9d160fb1590c9de66938d · art_fb210e6a4ae2442f9e508d3e [1200, 4200): tion

Blocksparse Computation

B.3 Detailed Model and Training Configurations

C Similarity Distributions of Generated Music

    License: CC BY 4.0

arXiv:2210.10349v2 [cs.SD] 31 Oct 2022

Museformer: Transformer with Fine- and Coarse-Grained Attention for Music Generation

Botao Yu†,  Peiling Lu‡,  Rui Wang‡,  Wei Hu†  ,  Xu Tan,Wei Ye§,   Shikun Zhang§,   Tao Qin‡,   Tie-Yan Liu‡†State Key Laboratory for Novel Software Technology, Nanjing University, China‡Microsoft Research Asia§National Engineering Research Center for Software Engineering, Peking University, Chinabtyu@foxmail.com, {peil,ruiwa,xuta,taoqin,tyliu}@microsoft.com,whu@nju.edu.cn, {wye,zhangsk}@pku.edu.cnhttps://github.com/microsoft/muzic
††thanks: Wei Hu and Xu Tan are the corresponding authors. This work was partially done while the first author was interning at Microsoft Research Asia.

Abstract

Symbolic music generation aims to generate music scores automatically.
A recent trend is to use Transformer or its variants in music generation, which is, however, suboptimal, because the full attention cannot efficiently model the typically long music sequences (e.g., over 10​t​r​u​e​00010true000 tokens), and the existing models have shortcomings in generating musical repetition structures.
In this paper, we propose Museformer, a Transformer with a novel fine- and coarse-grained attention for music generation.
Specifically, with the fine-grained attention, a token of a specific bar directly attends to all the tokens of the bars that are most relevant to music structures (e.g., the previous 1st, 2nd, 4th and 8th bars, selected via similarity statistics);
with the coarse-grained attention, a token only attends to the summarization of the other bars rather than each token of them so as to reduce the computational cost.
The advantages are two-fold.
First, it can capture both music structure-related correlations via the fine-grained attention, and other contextual information via the coarse-grained attention.
Second, it is efficient and can model over 3×3\times longer music sequences compared to its full-attention counterpart.
Both objective and subjective experimental results demonstrate its ability to generate long music sequences with high quality and better structures.11
          1

        The generated music samples can be found at https://ai-muzic.github.io/museformer. The source code can be found at https://github.com/microsoft/muzic.

1 Introduction

Symbolic music generation aims at generating music scores automatically and has drawn more and more attention in recent years [1, 2, 3]. Since music can be represented in organized sequences of discrete tokens just like text, Transformer-based models, which have been demonstrated to work well on text generation [4, 5], are increasingly applied in music generation [3, 6, 7, 8, 9, 10, 11] and have made great success.
While the self-attention mechanism empowers Transformer to capture the complex correlations in music, there are two ubiqu
  - rev_ev_f78be1b4cb8b2ab8e7cf7c36 · wrk_eba9d160fb1590c9de66938d · art_fb210e6a4ae2442f9e508d3e [4200, 7200): itous challenges to solve for this task: 1) Long sequence modeling. Music sequences are typically very long, especially for multi-instrument polyphonic music where the lengths can usually exceed 10​t​r​u​e​00010true000. The quadratic complexity of full attention limits its scalability to that length. 2) Music structure modeling. Music has its unique structures, where a piece can usually repeat some patterns of a previous piece, occasionally with some variations, after either a short or a long distance (see Figure 1 for an example). Successfully generating reasonable structures would make the music more realistic just like human-made music.

Figure 1: The music score of Twinkle, Twinkle, Little Star and its corresponding token representation. Every two consecutive bars on the Synth. track have the same rhythmic pattern, and the 9th - 12th bars repeat the 1st - 4th bars with an interval of 8 bars. Structures embodied as repetitions and variations are common in music.

Although many Transformer variants in natural language processing (NLP) [12] have been proposed to handle long sequences (the first challenge), they cannot well model the music structures (the second challenge).
According to the basic principles of these models, we can classify them into two types. The first type is called local focusing. Models of this type, e.g., Transformer-XL [13] and Longformer [14], mainly focus on part of the input sequence, and drop the rest tokens to reduce the cost. However, the parts that they focus on cannot contain many of the essential ranges important to music structures, and directly dropping the rest tokens may lead to losing some important information. The second type is called global approximation. Models of this type such as Linear Transformer [15] utilize linearized attention or sequence compression over the whole input sequence to approximate the token pair-wise attention. While the approximation effectively reduces the complexity, they cannot accurately capture the correlations between related parts and accordingly are inadequate in generating repetition structures. We will review more existing long-sequence Transformers in §2. Directly applying these models to music generation is suboptimal, and it is desirable to design an efficient model that can well model long music sequences as well as their structures.

In this paper, we propose to unify the above two types of models, which can well fit the characteristics of music. Our motivation is based on the observation that the importance is not uniformly distributed over the music sequence, and thus we do not need to treat all the tokens equally.
Intuitively, to generate music with repetition structures, the most important information the model should directly refer to when generating a music bar, lies in those bars that tend to be repeated in the current bar. We call these bars structure-related bars. For the other bars that are less important, approximation should do the trick. To this end, the p
  - rev_ev_538cfddee807a0c4f7d98d9a · wrk_4178bf9d843fa126d1677e3e · art_ae6773a46dcbeb8106a997e6 [0, 1627): The generation of long-term music inherently relies on the effective modeling of musical structure. Previous studies on structured music generation primarily rely on datasets with annotated structures, which are typically derived from bar- or phrase-level relation identification or similarity computation of melodies or melodies combined with chords. However, these annotation approaches are not applicable to polyphonic piano music datasets without separately isolated melodies, thereby limiting research on structured polyphonic piano music generation. To address this issue, we first devise a generic similarity-based annotation method to annotate musical structures at the phrase level. Subsequently, a novel music generation model based on piano roll representation and diffusion model, MusicExtender, is proposed to enable polyphonic piano generation with long-term structures. Specifically, a phrase-level autoregressive generation paradigm based on diffusion inpainting is developed to control the length of generated music, where each phrase is generated under the external structural conditions. In addition, we adjust the diffusion loss to accommodate the inpainting-like phrase generation task and incorporate a structural regularization term for better learning on musical structures. Objective and subjective experiments demonstrate that MusicExtender surpasses previous methods in terms of the quality of generated polyphonic piano music, meanwhile adhering to specified structural constraints and length requirements. The code and generated examples are available at https://github.com/Tayjsl97/MusicExtender .

### NP-2 · 部分新颖

提出使用相似度统计的方法探究音乐结构，并据此确定与结构相关的小节，用于指导细粒度注意力的关注范围。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 三篇文献均以相似度统计探究音乐结构（F1），但均未公开“由相似度统计结果确定与结构最相关的小节（如第1、2、4、8小节）并将其作为细粒度注意力关注对象”这一完整组合。MusicExtender 以相似度标注乐句级结构并驱动扩散修复生成，粒度与下游用途均不同；Self-Similarity-Based loss 文献的 self-attention 作用于全序列相对特征学习，非结构相关小节的注意力约束；Visual Overviews 的相似度结果用于着色可视化与人工导航。F1 已被多篇公开，F2 仅见乐句级近似，F3 未见任何文献公开，故整体组合部分新颖。  
**置信度：** 0.72  
**报告摘要：** 该点主张以相似度统计探究音乐重复结构并据此确定结构相关小节，用于指导细粒度注意力的关注范围。三篇对照文献均以相似度统计刻画音乐结构：其一以相似度统计标注乐句级结构单元并驱动扩散修复式生成与结构正则，与相似度统计这一子特征直接重合，但粒度为乐句而非小节，下游用途为生成条件而非注意力；其二以自相似矩阵学习音乐段落特征，其中的自注意力作用于全序列相对特征学习，用于新颖度与边界判断，并非将注意力约束到相似度选出的结构相关小节；其三将小节/段落间相似度映射为颜色用于结构概览与导航，属可视化用途。据此，相似度统计子特征已见公开，而“由相似度统计结果确定结构相关小节并作为细粒度注意力对象”的完整组合尚未见公开，组合层面保留部分新颖性；但该环节在现有材料中仍属未获证实，需在方法层面进一步核验。  
**未完成原因：** —  
**高度相关 Work：**
  - wrk_4178bf9d843fa126d1677e3e：以相似度统计标注音乐结构单元并驱动下游神经模型，与 F1 直接重合、F2 部分重合（乐句级而非小节级）；下游为扩散修复生成条件与结构正则项，非细粒度注意力，F3 无对应。 (cards: card_95030af11d17b35c5d495f01)
  - wrk_40ef221ac0c08df93ce1d524：以自相似矩阵统计音乐重复/同质结构（F1 重合），并引入 self-attention；但注意力用于全序列相对特征学习，输出为新颖度分数与边界检测，非由相似度选出结构相关小节作为注意力对象。 (cards: card_34c638192c7ea363ab8676e1)
  - wrk_2e2856efebb6106c4344fc13：以小节/段落间相似度统计刻画音乐结构与重复（F1 直接重合）；相似度结果用于着色可视化与人工导航，未涉及注意力机制，F2/F3 不重合。 (cards: card_bfba9e34f917663d6f674967)

**原文核验证据：**
  - rev_ev_9e1a93bfd5901a8a664d1444 · wrk_4178bf9d843fa126d1677e3e · art_ae6773a46dcbeb8106a997e6 [0, 1627): The generation of long-term music inherently relies on the effective modeling of musical structure. Previous studies on structured music generation primarily rely on datasets with annotated structures, which are typically derived from bar- or phrase-level relation identification or similarity computation of melodies or melodies combined with chords. However, these annotation approaches are not applicable to polyphonic piano music datasets without separately isolated melodies, thereby limiting research on structured polyphonic piano music generation. To address this issue, we first devise a generic similarity-based annotation method to annotate musical structures at the phrase level. Subsequently, a novel music generation model based on piano roll representation and diffusion model, MusicExtender, is proposed to enable polyphonic piano generation with long-term structures. Specifically, a phrase-level autoregressive generation paradigm based on diffusion inpainting is developed to control the length of generated music, where each phrase is generated under the external structural conditions. In addition, we adjust the diffusion loss to accommodate the inpainting-like phrase generation task and incorporate a structural regularization term for better learning on musical structures. Objective and subjective experiments demonstrate that MusicExtender surpasses previous methods in terms of the quality of generated polyphonic piano music, meanwhile adhering to specified structural constraints and length requirements. The code and generated examples are available at https://github.com/Tayjsl97/MusicExtender .
  - rev_ev_12ec3822efc3facb1be393ea · wrk_40ef221ac0c08df93ce1d524 · art_1876d660ac46ab8e10416bb9 [0, 840): Music Structure Analysis (MSA) is the task aiming at identifying musical segments that compose a music track and possibly label them based on their similarity. In this paper we propose a supervised approach for the task of music boundary detection. In our approach we simultaneously learn features and convolution kernels. For this we jointly optimize -- a loss based on the Self-Similarity-Matrix (SSM) obtained with the learned features, denoted by SSM-loss, and -- a loss based on the novelty score obtained applying the learned kernels to the estimated SSM, denoted by novelty-loss. We also demonstrate that relative feature learning, through self-attention, is beneficial for the task of MSA. Finally, we compare the performances of our approach to previously proposed approaches on the standard RWC-Pop, and various subsets of SALAMI.
  - rev_ev_7197e4e168c8a6244bdc0a4f · wrk_40ef221ac0c08df93ce1d524 · art_923fe91b1d19dca851853ec0 [15000, 18000): ains constant over the track, the structure may arise from variation of the harmonic content; in other cases, it will be the opposite.
Therefore, feature learning for msa should be made relative-to-a-track.

To let each feature 𝐗i\mathbf{X}_{i} “know” about surrounding times features {𝐗1​…​𝐗i−1,𝐗i+1​…​𝐗T}\{\mathbf{X}_{1}\ldots\mathbf{X}_{i-1},\mathbf{X}_{i+1}\ldots\mathbf{X}_{T}\} we introduce layers of  sa (sa) [35] in our encoder66
              6

            Note that the use of the SSM-loss alone does not allows fθf^{\theta} to encode relative features; this is the task of the sa..

2.5 Network architecture fθf^{\theta}

The architecture of the encoder fθf^{\theta} is given in Figure 1.
It is made of a succession of 5 consecutive convolution blocks followed by NN blocks of Transformer-Encoder.

Each convolution block is made of a 2D convolution followed by a PReLU [36] activation and a 2D max-pooling.
The kernel size (kf,kt)(k_{f},k_{t}), the number of channels ncn_{c} and pooling size (pf,pt)(p_{f},p_{t})) of each layer are the following:
layer-1: (kf,kt)(k_{f},k_{t})=(5,5) ncn_{c}=32 (pf,pt)(p_{f},p_{t})=(2,2),
layer-2: (5,5) 32 (2,2),
layer-3: (5,5) 64 (2,2),
layer-4: (5,5) 64 (2,2),
layer-5: (5,2) 128 (5,2).
The output of the last convolutional blocks has dimension (1,1) with ncn_{c}=128 channels and is flattened to a 128-dim vector.

Each input 𝐗i\mathbf{X}_{i} is independently projected using the convolutional blocks.
These outputs are then considered as a temporal sequence which is fed to NN blocks of Transformer Encoder (each made up of a sa layer with 8 heads, skip-connection, a normalization layer and two fully-connected layers with an internal dimension of 128).
The outputs are then passed to a tanh and L2-normalized.
They form a sequence of embeddings {𝐞iθ}i∈{1​…​T}\{\mathbf{e}^{\theta}_{i}\}_{i\in\{1\ldots T\}} with 𝐞iθ∈R128\mathbf{e}^{\theta}_{i}\in R^{128} which are used to compute 𝐒^i​jθ\mathbf{\hat{S}}_{ij}^{\theta}.

The size of the kernels 𝐊θ\mathbf{K}^{\theta} is fixed to (41,41) which roughly corresponds to 20s.
The kernels 𝐊θ\mathbf{K}^{\theta} are either initialized randomly or initialized with checkerboard kernels similar to the ones of [32].
In this case, checkerboard kernels have the same size (41,41) but are damped with Gaussian function with different σ\sigma (randomly chosen in the range [3​s,5​s][3s,5s]).
We used 3 different kernels 𝐊θ\mathbf{K}^{\theta} which are then combined using (1x1) convolution.
The diagonal of the resulting feature-map then goes to a sigmoid activation and is considered as the estimated novelty 𝐧^iθ\mathbf{\hat{n}}_{i}^{\theta}.

Our architecture remains lightweight with a number of parameters ranging from 268K to 567K depending on the number of Transformer Encoder blocks (from NN=0 to 3).

2.6 Training.

We train our network by minimizing jointly the two losses defined by eq. (3) and eq. (5):

ℒθ=α​ℒS​S​Mθ+(1−α)​ℒn​o​vθ\mathcal{L}^{\theta}=\alpha\mathcal{L}^{\theta}_{SSM}+(1-\alpha)\mat
  - rev_ev_e49125900c4c2f9d04584ef8 · wrk_2e2856efebb6106c4344fc13 · art_3cfcd862a4df5022da1b4320 [0, 943): We propose different methods for alternative representation and visual augmentation of sheet music that help users gain an overview of general structure, repeating patterns, and the similarity of segments. To this end, we explored mapping the overall similarity between sections or bars to colors. For these mappings, we use dimensionality reduction or clustering to assign similar segments to similar colors and vice versa. To provide a better overview, we further designed simplified music notation representations, including hierarchical and compressed encodings. These overviews allow users to display whole pieces more compactly on a single screen without clutter and to find and navigate to distant segments more quickly. Our preliminary evaluation with guitarists and tablature shows that our design supports users in tasks such as analyzing structure, finding repetitions, and determining the similarity of specific segments to others.

### NP-3 · 证据不足，无法裁定

利用区块稀疏等技术实现Museformer模型的高效编码，降低存储和计算复杂度。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** 本轮仅核验到一篇将 MuseFormer 作为稀疏注意力 SOTA 基线引用的后续工作（wrk_3224db2e91b2ca8a83188f8c），其摘要仅确认 MuseFormer 属稀疏注意力机制，未公开 blocksparse 编码实现、相对原始 Transformer 的存储/计算复杂度降低，以及相对全注意力模型 3 倍长序列与更快速度等具体技术特征。NP-3 的核心技术特征（blocksparse 高效编码、复杂度降低、3 倍长序列/更快速度）均缺少已核验的原始文献证据，无法据此对新颖性作出裁定；已证实的有限结论仅为 MuseFormer 被认定为稀疏注意力机制 SOTA 基线。  
**置信度：** 0.60  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**未完成原因：** semantic_evidence  
**高度相关 Work：**
  - wrk_3224db2e91b2ca8a83188f8c：该文献将 MuseFormer 认定为稀疏注意力机制 SOTA 并用作基线，为 NP-3 的稀疏注意力效率设计提供背景性旁证；但未公开 blocksparse 编码、复杂度降低或 3 倍长序列/更快速度的具体技术细节，仅构成部分相关文献。 (cards: card_8446338e8a48e4b8a3e5637c)

**原文核验证据：**
  - rev_ev_aaf7eb4bb00ae9d300d3d823 · wrk_3224db2e91b2ca8a83188f8c · art_30c621ef4b19acf1d7a1b323 [0, 1821): In the field of symbolic music generation, maintaining macro-structural coherence and preventing logical drift within long sequences remains a critical challenge. Traditional autoregressive models primarily rely on implicit probabilistic statistics to capture contextual dependencies. Consequently, they often struggle to retain memory of initial musical motifs over hundreds of time steps. To address this limitation, this paper proposes CAST, a framework for long-range music generation based on explicit skeleton guidance. This method decouples the complex sequence generation task into two subprocesses: macro-harmonic planning and micro-texture filling. Specifically, MusicBERT is introduced to extract deep semantic skeletons. We then utilize a cross-attention mechanism to establish a dynamic mapping between these skeletons and the MuseFormer generator. This design achieves explicit modeling of long-range dependencies. For validation, we selected MuseFormer, which represents the state-of-the-art in sparse attention mechanisms, as the baseline model. Experiments were conducted to verify the superiority of explicit structural constraints over purely implicit learning. Quantitative evaluations demonstrate significant improvements in generating sequences up to 1000 tokens. The CAST framework reduced the structural error from 0.58 (baseline) to 0.22. Additionally, it increased chord generation accuracy to 96%. These results indicate an effective resolution to the logical collapse problem in long-sequence generation. Furthermore, mechanism analysis reveals significant functional backtracking patterns within the model. This confirms that our method guides the model to acquire deep harmonic grammar logic, thereby generating complex musical works that are structurally rigorous and stylistically unified.

---

## 八、报告局限

- NP-2：Reviewer 提出补查请求；原始请求保留在来源 Review，本报告节点未执行补查。
- NP-3：Reviewer 核验未完成；原因：semantic_evidence。
- NP-3：Reviewer 提出补查请求；原始请求保留在来源 Review，本报告节点未执行补查。
- 被拒绝证据：card_b17e803f4b81750687bb5f0d: 文献相关性低于门槛
- 本报告节点输入未提供完整检索执行事实，检索覆盖状态未知。

---

## 九、附件及参考信息

### 缺失参考文献

本节点输入未记录该类条目；不代表已核实为无。

### 缺失 Baseline

本节点输入未记录该类条目；不代表已核实为无。

### 引用问题

本节点输入未记录该类条目；不代表已核实为无。

### 被拒绝证据

- card_b17e803f4b81750687bb5f0d：文献相关性低于门槛

### 检索到的文献

- Museformer: Transformer with Fine- and Coarse-Grained Attention for Music Generation：[https://arxiv.org/pdf/2210.10349](https://arxiv.org/pdf/2210.10349)
- ASpanFormer: Detector-Free Image Matching with Adaptive Span Transformer：[https://arxiv.org/pdf/2208.14201](https://arxiv.org/pdf/2208.14201)
- NeuroExplainer: Fine-Grained Attention Decoding to Uncover Cortical Development Patterns of Preterm Infants：[https://arxiv.org/pdf/2301.00815](https://arxiv.org/pdf/2301.00815)
- Prism: Spectral-Aware Block-Sparse Attention：[https://arxiv.org/pdf/2602.08426](https://arxiv.org/pdf/2602.08426)
- Emoji-based Fine-grained Attention Network for Sentiment Analysis in the Microblog Comments：[https://arxiv.org/pdf/2206.12262](https://arxiv.org/pdf/2206.12262)
- Fine-Grained Attention Mechanism for Neural Machine Translation：[https://arxiv.org/pdf/1803.11407](https://arxiv.org/pdf/1803.11407)
- Coarse- and Fine-grained Attention Network with Background-aware Loss for Crowd Density Map Estimation：[https://arxiv.org/pdf/2011.03721](https://arxiv.org/pdf/2011.03721)
- A Fine-Grained Visual Attention Approach for Fingerspelling Recognition in the Wild：[https://arxiv.org/pdf/2105.07625](https://arxiv.org/pdf/2105.07625)
- Self-Similarity-Based and Novelty-based loss for music structure analysis：[https://arxiv.org/pdf/2309.02243](https://arxiv.org/pdf/2309.02243)
- Pitchclass2vec: Symbolic Music Structure Segmentation with Chord Embeddings：[https://arxiv.org/pdf/2303.15306](https://arxiv.org/pdf/2303.15306)
- SSM-Net: feature learning for Music Structure Analysis using a Self-Similarity-Matrix based loss：[https://arxiv.org/pdf/2211.08141](https://arxiv.org/pdf/2211.08141)
- EDMFormer: Genre-Specific Self-Supervised Learning for Music Structure Segmentation：[https://arxiv.org/pdf/2603.08759](https://arxiv.org/pdf/2603.08759)
- clDice -- A Novel Topology-Preserving Loss Function for Tubular Structure Segmentation：[https://arxiv.org/pdf/2003.07311](https://arxiv.org/pdf/2003.07311)
- Modeling Musical Structure with Artificial Neural Networks：[https://arxiv.org/pdf/2001.01720](https://arxiv.org/pdf/2001.01720)
- Parsing Musical Structure to Enable Meaningful Variations：[https://arxiv.org/pdf/2507.10740](https://arxiv.org/pdf/2507.10740)
- Visual Overviews for Sheet Music Structure：[https://arxiv.org/pdf/2308.06140](https://arxiv.org/pdf/2308.06140)
- Automatic Music Generation with Multi-module Neural Networks for Chord, Rhythm, and Pitch Modeling：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s40745-025-00643-7](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s40745-025-00643-7)
- Enhancing long-term structure in symbolic music generation via a cascaded Skeleton-to-texture framework：[https://www.nature.com/articles/s41598-026-46750-0.pdf](https://www.nature.com/articles/s41598-026-46750-0.pdf)
- MusicExtender: Generating Polyphonic Piano Music with Long-term Structures via Similarity-guided Diffusion Inpainting：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3410-3_15](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3410-3_15)
- An intelligent composition system for Chinese art songs via a cascaded pipeline of symbolic music generation and LLM-based lyric writing：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00530-026-02605-2](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00530-026-02605-2)
- Video background music generation using hybrid shared mixture-of-experts multimodal Transformer：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00521-026-12270-1](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00521-026-12270-1)
- Recent advances in music generation: methods, evaluation, and challenges：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s10462-026-11582-x](http://link.springer.com/openurl/pdf?id=doi:10.1007/s10462-026-11582-x)
- Multi-layer rhythmic modeling and interactive system for guzheng music style generation：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s44163-026-01126-1](http://link.springer.com/openurl/pdf?id=doi:10.1007/s44163-026-01126-1)
- Integrating AI and cloud-edge technologies for music creation in educational and performance domains：[https://www.biomedcentral.com/openurl/pdf?id=doi:10.1186/s13677-026-00854-0](https://www.biomedcentral.com/openurl/pdf?id=doi:10.1186/s13677-026-00854-0)
- Security and Robustness Analysis of Deep Arabic Traffic Text Detection in Intelligent Transportation Systems：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37933-7_27](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37933-7_27)
- HQA-Rec: Hyperbolic Quantization Alignment for Citation Recommendation：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38410-2_40](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38410-2_40)
- Low-resource video-conditioned music generation via reliability-aware visual–text–audio fusion：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00371-026-04615-7](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00371-026-04615-7)
- Topology-Guided Mixture of Experts for Efficient Multimodal Sentiment Analysis：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38410-2_30](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38410-2_30)
- Motifs, Phrases, and Beyond: The Modelling of Structure in Symbolic Music Generation：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-031-56992-0_3](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-031-56992-0_3)
- A Modular Hybrid Approach to Affective Music Generation for Music Therapy：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37936-8_23](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37936-8_23)
- Beyond conventional imaging: curvelet-AI convergence for non-invasive microalgal lipid quantification and biofuel optimization：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00449-026-03423-6](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00449-026-03423-6)
- Mapping the Acoustic Alignment: Feature Correlation Analysis of Human and AI-Generated Music in Social Media：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38407-2_57](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38407-2_57)
- 38th European Congress of Pathology - Abstracts：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00428-026-04642-8](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00428-026-04642-8)
- Close in Timbre, Far in Space: Geospatial Modeling of Iranian Regional Music：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-36445-6_1](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-36445-6_1)
- Advances in semi and self-supervised learning techniques for cross-domain visual inspection tools：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s13042-026-03259-2](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s13042-026-03259-2)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
