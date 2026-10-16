# Autonomy and antifragile stress record

Use this template for material or repeated operational stress. It is a learning record, not merely an incident closure note.

```yaml
stress:
  signal: <signal-id>
  detected_at: <timestamp>
  target: <asset-or-service>
  observed_impact: <facts>
  immediate_action: <stabilisation>
  result: stabilized | degraded | failed

cause:
  classification: capacity_growth | abnormal_producer | policy_gap | unknown
  confidence: low | medium | high
  evidence:
    - <probe-or-record>

lesson:
  repeated: true | false
  system_weakness: <what should improve>

proposal:
  type: adaptation
  change: <specific change>
  alternatives:
    - <alternative>
  recommendation: <reasoned recommendation>
  rollback: <credible rollback or containment>
  success_probe: <how to verify>

decision:
  required: true | false
  reason: <why the active intent boundary does or does not require a decision>
```

Checklist:

- [ ] Stabilisation and learning are recorded separately.
- [ ] Observed facts are separated from inference.
- [ ] Repetition and trend are checked.
- [ ] A systemic improvement proposal exists, or the evidence-based reason for no change is recorded.
- [ ] The proposal is classified as autonomous, notify-after, or ask-before.
- [ ] Technical state and user outcome are both verified after adaptation.
