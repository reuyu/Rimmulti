G-Q1 Ordinary Multi-Settlement Topology — MASTER CORRECTED BASELINE
Status: ANALYSIS BASELINE — G-Q1 OPEN
Controlling facts
1. Players may own multiple Settlements.
2. Canonical requirements do not currently require simultaneous divergent-LocalClock simulation in one client process.
3. LocalClock remains Settlement-scoped.
4. One execution island may actively advance one LocalClock unless separately validated virtualization is introduced.
5. WriterLease/Fencing is Settlement-scoped.
6. Current domain transaction slices may proceed without choosing the final ordinary topology.
Candidate status
- Single Active Materialization: PROMISING / ENGINE PROOF FIRST
- Multiple Local Islands: ENGINE/RESOURCE PROOF FIRST
- Server-Hosted Ordinary Workers: ARCHITECTURE FALLBACK; requires explicit direction change
- Hybrid Lazy Materialization: PROMISING COMPOSITION / ENGINE PROOF FIRST
No candidate is selected yet.
First required proof
Before topology freeze:
- sequential A/B materialization with divergent LocalClockIds;
- hard unload/reload;
- singleton/cache contamination oracle;
- lease/fencing switch;
- crash/reconnect;
- stale publication rejection.
Only after that should simultaneous separate-process islands be compared.
Decision point
Resolve G-Q1 before ordinary multi-Settlement Client Integration.