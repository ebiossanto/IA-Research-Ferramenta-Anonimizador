# Bibliografia (com status de verificação)

**[V]** = existência/título/identificador conferidos por busca na web durante este trabalho (24–25/set e 15–17/out/2026).
**[M]** = citado de memória; **conferir antes de usar em texto formal**.

## Orçamento de irreversibilidade / agentes
* [V] *The Controllability Trap: A Governance Framework for Military AI Agents.* arXiv:2603.03515.
* [V] *The Irreversibility Budget: Fleet-Level Risk Accounting and Admission Control for Agent Operating Systems.* (MPI-SWS) arXiv:2609.00275.
* [V] revoco — github.com/rsh1k/revoco ; pypi.org/project/revoco.
* [V] irredux — pypi.org/project/irredux.

## Privacidade diferencial
* [V] Dwork, McSherry, Nissim, Smith. *Calibrating Noise to Sensitivity in Private Data Analysis.* TCC 2006; reimpressão J. Privacy and Confidentiality 7(3), 2016.
* [M] Dwork, Roth. *The Algorithmic Foundations of Differential Privacy.* Found. Trends Theor. Comput. Sci., 2014.
* [V] Ghosh, Roughgarden, Sundararajan. *Universally Utility-Maximizing Privacy Mechanisms.* STOC 2009; SIAM J. Comput. 2012; arXiv:0811.2841.
* [V] Mironov. *On Significance of the Least Significant Bits For Differential Privacy.* ACM CCS 2012.
* [V] Dwork, Naor, Pitassi, Rothblum, Yekhanin. *Pan-Private Streaming Algorithms.* ICS 2010.
* [V] *Verified Differential Privacy for Finite Computers.* CoqPL 2023 (autores: conferir).

## Unlearning
* [V] Bourtoule, Chandrasekaran, Choquette-Choo, Jia, Travers, Zhang, Lie, Papernot. *Machine Unlearning.* IEEE S&P 2021; arXiv:1912.03817.
* [V] *Revisiting the Past: Data Unlearning with Model State History.* arXiv:2506.20941.
* [V] *Machine Unlearning: Solutions and Challenges.* arXiv:2308.07061.
* [V] *An Introduction to Machine Unlearning.* arXiv:2209.00939.
* [M] Cao, Yang. *Towards Making Systems Forget with Machine Unlearning.* IEEE S&P 2015.
* [M] Ginart, Guan, Valiant, Zou. *Making AI Forget You: Data Deletion in Machine Learning.* NeurIPS 2019.
* [M] Guo, Goldstein, Hannun, van der Maaten. *Certified Data Removal from Machine Learning Models.* ICML 2020 (arXiv:1911.03030).
* [M] Sekhari, Acharya, Kamath, Suresh. *Remember What You Want to Forget: Algorithms for Machine Unlearning.* NeurIPS 2021.

## Controle, sistemas e verificação
* [M] Sontag. *Smooth stabilization implies coprime factorization.* IEEE Trans. Autom. Control, 1989 (origem da ISS).
* [M] Sontag, Wang. *On characterizations of the input-to-state stability property.* Systems & Control Letters, 1995.
* [M] Bak, Tang, Wiesenfeld. *Self-organized criticality: an explanation of 1/f noise.* Phys. Rev. Lett., 1987.
* [M] Garcia-Molina, Salem. *Sagas.* ACM SIGMOD 1987.
* [V] Ho, Protzenko. *Aeneas: Rust Verification by Functional Translation.* ICFP 2022 (há backend para Lean 4).

## Termodinâmica da computação e remanência
* [M] Landauer. *Irreversibility and heat generation in the computing process.* IBM J. Res. Dev., 1961.
* [M] Bennett. *The thermodynamics of computation — a review.* Int. J. Theor. Phys., 1982.
* [M] Gutmann. *Secure Deletion of Data from Magnetic and Solid-State Memory.* USENIX Security 1996.
* [M] Halderman et al. *Lest We Remember: Cold Boot Attacks on Encryption Keys.* USENIX Security 2008.

## Algoritmos de referência
* [V] SplitMix64: sequência de referência publicada com semente 0 (`0xE220A8397B1DCDAF, 0x6E789E6AA1B965F4, 0x06C45D188009454F`) — reproduzida em Python (executado) e conferida em Rust/Lean pelos vetores.
