---
title: GPU speed of GCN propagation and edge-IG path schedule
author: Mhungdangbuonngu
date: 2026-11-16
branch: gate1-pipeline
cost: { minutes: 1, tokens: 1115 }
id: l-052f50c9
scope: repo
status: active
src: agent
touches:
  - src/model/gnn.py
---

Training was ~260 ms per batch because torch.sparse.mm with a COO adjacency is slow on GPU (and coalesces every call); CSR (norm_adj now builds CSR with a cached sort layout) is 5-14x faster, still differentiates w.r.t. the values (so edge-IG works), and reproduced the saved test QWK of COO-trained models exactly. For one-triple edge-IG, gather/index_add (propagate_scatter) beats both, but its memory is B*E*F, so it is only used for batches <= 16. Edge-IG with a uniform alpha grid is badly non-complete here (gaps as large as f(1)-f(0) at 20 steps) because GCN degree normalisation 1+sum(m) makes the output move mostly for alpha < 0.05; alpha = t^3 with 32 steps gives gaps ~0.1 and cosine 0.999 vs 512 steps. Also: pkill -f <pattern> kills the calling shell when the pattern appears in the command line; kill by PID.
