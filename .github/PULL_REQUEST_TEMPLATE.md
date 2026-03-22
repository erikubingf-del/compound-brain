## Summary

## Contribution Lane
- community skill
- department pack
- source pack
- evaluator
- case study
- benchmark
- promotion candidate
- core runtime

## Evidence
- case study:
- benchmark:
- activated repo:

## Scope Check
- [ ] This does not create a second Claude/Codex control plane
- [ ] This respects preview -> prepare -> activate
- [ ] This does not bypass approvals or evaluator gates
- [ ] This keeps project-specific learnings separate from global learnings

## Validation
- [ ] `python3 -m unittest discover -s tests -p 'test_*.py' -v` if code changed
- [ ] `bash install.sh --dry-run` if install/runtime surfaces changed
- [ ] Docs or templates reviewed for correctness

## Promotion Intent
- [ ] community-only
- [ ] candidate for template promotion
- [ ] candidate for knowledge-seed promotion
- [ ] candidate for runtime promotion
