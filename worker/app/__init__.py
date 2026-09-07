"""Research Radar analysis worker package (`worker.app`).

The worker claims analysis tasks from the server, runs them through a provider adapter and
submits results. Two adapter families (D41): API-key providers over ``httpx``, and CLI/ACP
providers over ``subprocess`` with tool and network flags from
``contracts/ai/providers.yaml`` -- because ADR-0010's isolation requirement is a
process-level requirement and only a subprocess boundary can enforce it.
"""
