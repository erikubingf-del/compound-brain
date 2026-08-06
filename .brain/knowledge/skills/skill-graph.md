# compound-brain — Skill Graph
_Last updated: 2026-08-04_

## Loadable project skills (`.claude/skills/`)

These are real skills Claude Code auto-loads in any session in this repo —
not notes about skills. Entries below this block are capability notes.

| Skill | Purpose |
|---|---|
| [brain-orient](../../../.claude/skills/brain-orient/SKILL.md) | Read AGENTS.md, queue, and recent digests before acting; report pending and stale state |
| [brain-write](../../../.claude/skills/brain-write/SKILL.md) | Route a fact/decision/pattern to its correct home in `.brain/`; scrub, dedup, index |
| [brain-digest](../../../.claude/skills/brain-digest/SKILL.md) | Run the weekly research digest: scan, verify against official docs, write, self-apply SAFE, push |
| [validate-digest](../../../.claude/skills/validate-digest/SKILL.md) | Check a digest against its typed contract before commit |



## _(Add skills as they are used and improved)_

Template:
## Skill Name
**Level:** Beginner | Intermediate | Advanced | Expert
**Key Knowledge:** ...
**Next Improvements:** ...

## brev-cli
**Level:** Intermediate
**Related Projects:** compound-brain
**Key Knowledge:** Manage GPU and CPU cloud instances with the Brev CLI for ML workloads and general compute. Use when users want to create instances, search for GPUs or CPUs, SSH into instances, open editors, copy files, port forward, manage organizations, or work with cloud compute. Supports fine-tuning, reinforcement learning, training, inference, batch processing, and other ML/AI workloads. Trigger keywords - brev, gpu, cpu, instance, create instance, ssh, vram, vcpu, A100, H100, cloud gpu, cloud cpu, remote machine, finetune, fine-tune, RL, RLHF, training, inference, deploy model, serve model, batch job.
**Next Improvements:** Adapt to the repo's local control plane.

## Database Engineering
**Level:** Intermediate
**Related Projects:** compound-brain
**Key Knowledge:** ** PostgreSQL, Prisma ORM, migration management
**Next Improvements:** ** Database backup automation, migration testing, replication

## WhatsApp Bot Engineering
**Level:** Intermediate
**Related Projects:** compound-brain
**Key Knowledge:** ** WhatsApp Web.js, PM2 multi-instance, audio transcription pipeline, OpenAI Whisper, per-instance spending limits
**Next Improvements:** ** Bot resilience patterns, automated QA, cost optimization

## AI Product Architecture
**Level:** Intermediate
**Related Projects:** compound-brain
**Key Knowledge:** ** RAG systems, prompt engineering, agent architecture, MCP servers, QMD hybrid search
**Next Improvements:** ** Multi-agent coordination, vector database optimization, agentic memory systems

## autoresearch-loop
**Level:** Intermediate
**Related Projects:** compound-brain
**Key Knowledge:** Autonomous experiment-loop workflow for fixed-evaluator research repos. Use when a repo has a small mutable surface, a fixed evaluation harness, a fixed runtime budget, and iterative keep/discard experiments. Triggers on repos shaped like karpathy/autoresearch, or any project with program.md + a fixed evaluator + a results log. Also applies to private strategy-research repos that follow the same program.md + fixed-evaluator + results-log layout; the specific repo and path stay in private memory, not in this public file.
**Next Improvements:** Adapt to the repo's local control plane.
