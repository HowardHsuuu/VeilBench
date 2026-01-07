## Implementation Details

1. Alternative/risk matching: Currently extracting first keyword (e.g., "Podman" from "Podman (rootless by default)") and doing substring match. Is this sufficient or need more sophisticated matching?

2. `capability_score` normalization: Using `expected_count = max(len(expected_recommendations), 3) * 2`. Is there a better formula?

3. Sandbagging index negative values: Formula can produce negatives. Should we clamp to ≥0?

## Output Format

4. CSV schema OK?
   - Per-framing: `model, task_id, framing_type, [5 metrics]`
   - Delta: `model, task_id, [5 deltas], sandbagging_index`

5. Anything else Val needs for report generation?

## Integration

6. Runner output path: Will logs be in `./logs/*.jsonl`? Scenarios in `./scenarios/`?