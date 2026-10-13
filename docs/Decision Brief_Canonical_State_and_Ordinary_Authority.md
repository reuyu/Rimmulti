# Decision Brief: Canonical State and Ordinary Authority

**To:** Master (GPT-5.6 Sol)
**From:** Architecture & Requirements Analysis Agent (Gemini 3.1 Pro C)
**Reference:** WP-ANALYSIS-STATE-AUTHORITY-01

---

## A. Canonical Settlement Representation

B2-lite 방식(수정 불가능한 엔진 생성 전체 타겟 맵 체크포인트 + 소규모 서버 투영/인덱스 + 순서가 지정된 델타 저널)은 서버가 커스텀 RimWorld 직렬화기(custom serializer)를 자체 구현해야 하는 치명적인 위험을 회피할 수 있는 가장 유력한 하이브리드 대안이다. 이 방식이 유효하려면 다음의 Entity Identity 구조가 반드시 선행되어야 한다.

* **Stable EntityId & Server-issued Namespace:** 프로세스 간(클라이언트 및 다수의 Worker) 충돌을 방지하기 위해 서버가 고유한 ID 범위(range) 또는 네임스페이스를 발급하고 관리해야 한다.


* **Native RimWorld loadID Binding:** 엔진 내부의 고유 ID와 서버의 Canonical ID를 매핑하는 신뢰할 수 있는 참조 계층이 필요하다.


* **Entity Creation/Destruction & Stack Split/Merge:** 아이템 분할, 병합, 파괴 시 엔진은 새로운 ID를 생성하거나 삭제한다. B2-lite 모델에서는 이러한 ID 변동이 Canonical Server State와 충돌하지 않도록 명시적인 교차 경계(cross-boundary) 매니페스트로 추적되어야 한다.


* **Pawn/Animal & Faction Identity:** Faction의 분리(FR-176)나 병합 시 여러 Worker 내에서 동일한 Faction Identity를 유지해야 하므로, 서버 권한의 글로벌 레지스트리가 필수적이다.


* **Nested Holders:** 폰 인벤토리, 수송 포드 등 중첩된 컨테이너 내부의 객체들 역시 이동 시 참조가 손실되지 않도록 ID 바인딩이 유지되어야 한다.



## B. Ordinary Simulation Authority

온라인 상태인 Settlement Owner의 클라이언트는 최종 도메인 권한을 직접 행사할 수 없으며(ADR-001), 서버의 임대(lease)를 받은 Simulation Writer로서 기능해야 한다.

* **Server Canonical Custody:** 서버가 Canonical Graph의 최종 소유권을 가지며, 클라이언트의 업로드는 승인 대기 상태의 후보(candidate)로 취급된다.


* **Checkpoint & Revision Rules:** 체크포인트는 반드시 이전 Canonical Head를 부모로 삼는 Fast-forward-only 방식이어야만 수락된다. 단, 단순한 리비전 확인만으로는 클라이언트가 메모리 조작으로 위조한 자산(forged wealth)을 감지할 수 없다.


* **Disconnect/Crash:** 클라이언트 연결이 끊기면 서버의 판단하에 Ordinary Simulation은 강제 정지(hard stop)되어야 한다.


* **Handoff (Client ↔ Tactical Worker):** Tactical Session 시작 시 Live Client의 Writer Lease를 즉각 회수하고 Worker로 이관(eviction)해야 하며, 종료 시 Worker의 결과를 Client로 Re-materialization 하는 무결성 프로토콜이 필요하다.



## C. Multi-Settlement Clock Topology

SRS는 한 명의 플레이어가 여러 Settlement를 소유할 수 있도록 허용하지만(CFG-008, FR-034), ADR-006A는 "Execution Island 하나당 하나의 활성 LocalClock"을 원칙으로 삼고 있다. 다음 토폴로지 중 하나를 채택해야 한다.

1. **Player-scoped Clock:** 플레이어 소유의 모든 정착지가 단일 LocalClock을 공유한다. 정복(FR-163) 시 획득한 정착지는 새 주인의 시계에 맞춰 재투영(reproject)된다. 이는 바닐라 다중 정착지 플레이와 가장 호환성이 높으나, "정복이 L_s를 초기화하지 않는다"는 ADR-006A의 기존 규칙을 명시적으로 수정해야 한다.


2. **One Active Settlement Per Client:** 한 번에 하나의 정착지만 시뮬레이션되고 나머지는 완전히 동결된다. 구현은 단순하나 바닐라 경험과 차이가 크다.


3. **Validated Per-map Clock Virtualization:** 단일 클라이언트 내부에서 맵별 독립 시계를 가상화한다. 이는 높은 검증 비용과 구현 리스크가 따른다.


4. **Separate Execution Islands:** 원격 Worker를 통해 오프라인 시뮬레이션과 유사하게 병렬 처리한다.

## D. Concurrent Economy / Tactical

Tactical Session 중 대상 정착지에 오프라인 자동 상점 거래(FR-206) 및 세금 징수(FR-187)가 발생할 때, B2-lite 아키텍처를 안전하게 유지하기 위한 모델 비교는 다음과 같다.

* **Primary Candidate (Exclusive Material-State Lease):** Tactical Worker가 활성화된 동안 해당 정착지에 대한 Auto Shop 및 Tax 처리 요청은 서버 대기열(Queue)에 보류된다. 세션이 종료되고 Canonical State가 병합된 이후에 델타 작업(Delta application)이 순차적으로 적용된다.


* **Field-level Concurrent Merge:** 전투 진행 중에도 인벤토리 필드를 개별 병합한다. 이는 복잡한 커스텀 직렬화 및 충돌 보상 로직을 요구하므로 실패 위험이 높다.



**SRS 충돌 분석:** SRS는 오프라인 거래와 세금을 허용하지만, 이것이 "진행 중인 전투 맵 내부와 1틱 단위로 실시간 동시 체결되어야 한다"고 강제하지 않는다. 따라서 임시 Queueing 메커니즘은 SRS의 명시적 문구와 충돌하지 않는 유효한 설계다. (참고: 부분 징수 시 LastCollection 시점 갱신에 관한 TBD-05는 향후 Economy 구현 전 최종 확정되어야 한다).

## E. Shared World Layer

카라반, 세계 객체(WorldObjects), 그리고 맵 외부의 상태는 Client나 Worker가 아닌 Dedicated Server가 배타적 권한을 가져야 한다.

* **Server-Authoritative Transit:** 이동 중인 카라반과 소속 Pawn/Animal/Item의 데이터 보관(Custody)은 서버가 전담한다.


* **Vision-Filtered Projection:** 서버는 Faction별 시야 및 정찰(Scout/Ambush) 규칙(FR-072~089)에 입각하여 필터링된 월드 상태만 Client와 Worker에 전송(Projection)해야 한다.


* **Tactical Ingress/Egress & Tax/Attack Caravans:** 전투 진입 전/후 및 세금 징수 카라반은 반드시 Shared World Layer를 거쳐 Settlement Local Domain으로 진입/퇴출해야 한다.


* **Transit Clock Policy:** 카라반 이동 중 생리적 변화(배고픔, 노화, 부상 악화)를 계산하기 위한 Transit Clock 규칙은 Tactical Production 이전에 반드시 선행 정의되어야 한다.



## F. Trust and Content

* **Hostile Input as Checkpoints:** Owner Client가 업로드하는 모든 체크포인트와 Save 파일은 잠재적인 공격 벡터(Hostile input)로 간주되어야 한다. ADR-002의 "Trusted Worker"는 서버 운영자가 통제하는 프로세스를 뜻할 뿐, 그 안으로 로드되는 클라이언트 데이터를 신뢰한다는 의미가 아니다.


* **Content Manifest & Schema Allowlist:** 허용된 모드 및 DLC의 Content Manifest를 서버가 핀(pinned) 상태로 유지해야 하며, Worker에 로드되기 전에 Type/Schema Allowlist 유효성을 통과해야 한다.


* **Fail-Closed Validation:** 미확인 시계열 데이터가 Tactical 입장을 차단하여 오프라인 공격을 무효화(Weaponization)하는 상황을 막으려면, 런타임이 아닌 '콘텐츠 승인(Approval)' 단계에서 사전에 완벽히 검증되어야 한다.


* **Cosmetic Client-only Mods:** 클라이언트 전용 모드는 시뮬레이션 직렬화와 게임플레이 상태에 일절 관여하지 않음이 증명된 경우에만 Allowlist에 포함될 수 있다.



## G. Red-Team Question Reconciliation

Opus 외부 리뷰어 질문(G-Q1~Q10)에 대한 분배 및 상태 조정 결과이다.

1. **G-Q1 (Multi-settlement clock topology):** Master Architecture Decision Required. (Player-scoped clock 선택 시 ADR-006A 수정 수반).


2. **G-Q2 (Ordinary-simulation trust posture):** Master Architecture Decision Required. (클라이언트 신뢰 위험 수용 여부).


3. **G-Q3 (Asset availability during Tactical):** Master Architecture Decision Required. (Exclusive lease vs Field merge).


4. **G-Q4 (Worker crash semantics):** Master Architecture Decision Required..


5. **G-Q5 / Q5b (Mid-session domain events & Storytellers):** Defer to ADR-002 개정 및 ADR-005..


6. **G-Q6 (Online progress-loss window):** Master Architecture Decision Required..


7. **G-Q7 (Mod policy & Content migration):** Defer to ADR-006B (Configuration & Content Manifest)..


8. **G-Q8 (Settlement Inventory definition for Economy):** Master Architecture Decision Required (또는 ADR-003으로 위임)..


9. **G-Q9 (Occupy Auto-shop state):** Master Architecture Decision Required. (SRS에 관련 내용 없음).


10. **G-Q10 (Owner UX under Candidate C remote-play):** Master Architecture Decision Required. (온라인 방어자가 원격 플레이 레이턴시를 감수할지에 대한 제품 UX 정책).



*(참고: 기존 TBD-01~05 외에 새로운 TBD ID를 생성하지 않았으며, 요구사항에 이미 명시된 답변은 배제하였다.)*

---

## Deliverable Summary for Master

**1. Architecture Decisions Master Can Safely Make Now**

* **ADR-003 Scope Redefinition:** "Canonical Settlement State & Entity Identity"를 최우선으로 다루도록 스코프 확장.
* **B2-Lite Granularity Adoption:** 커스텀 직렬화를 피하기 위해 Exclusive Writer Lease 하에서 생성된 Immutable Target Snapshot 및 Cross-boundary Manifest 방식을 기본 베이스라인으로 확정.
* **Concurrent Tactical vs Economy (G-Q3):** Tactical Session 진행 중 대상 정착지의 상점/세금 처리를 Queueing(Exclusive Asset Lease) 처리하는 방안 채택.
* **Hostile Client Checkpoint:** Owner Client의 데이터를 비신뢰 입력(Untrusted Input)으로 간주하고, 허용 목록(Allowlist) 검증을 의무화.

**2. Decisions Requiring Runtime Validation (PoCs / Falsification Gates)**

* **Remote Tactical Presentation (G-Q10 & Candidate C):** 원격 클라이언트가 Worker 내부의 맵을 제어할 때의 반응성(NFR-011) 및 구현 타당성.
* **Live Client Eviction & Re-injection:** 온라인 중인 Owner Client의 맵 권한을 회수하여 Worker로 이관하고, 종료 후 델타와 함께 재구성(Materialization)하는 프로세스 검증.

**3. Decisions Requiring User / Product-Policy Input**

* **Multi-Settlement Clock Topology (G-Q1):** Player-scoped Clock(정복 시 L_s 덮어쓰기)을 사용할지 여부.
* **Ordinary Simulation Trust (G-Q2):** 클라이언트가 생산하는 일반 시뮬레이션의 위조(Wealth 뻥튀기 등) 방지를 위한 실사(Audit) 범위 및 위험 수용 한도.
* **Crash Semantics (G-Q4):** Tactical Worker 크래시 발생 시 롤백 정책.

**4. Proposed ADR Dependency Graph**

```text
[Master Product Decisions: G-Q1, Q2, Q3, Q4, Q6, Q8, Q9, Q10]
       │
       ├─────────────────────────────────────────────┐
       ▼                                             ▼
[ADR-007] Ordinary Simulation Authority      [ADR-006B] Config &
   & Settlement Custody (Writer Lease)          Content Manifest
       │                                             │
       ▼                                             │
[ADR-003] Canonical Settlement State                 │
   & Entity Identity (Save Provenance, Escrow) ◄─────┤
       │
       ▼
[ADR-004] Ownership Txn / Repair
   (Single DB Commit, Outbox)
       │
       ▼
[ADR-008] Shared World Layer
   (Transit Clock, Caravans, World Projection)
       │
       ▼
[SETTLEMENT STATE PIPELINE] ────────► [ECONOMY] & [TACTICAL / ADR-002 Final]

```