# R27 캡처 계약의 실제 descriptor 필드명 정정

Master source 대조: 현재 및 frozen R25 WorkerBridge.cs:3712의 OperatorLaunchDescriptor는 property가 아닌 public string **field** 7개를 사용한다. WP의 PascalCase mapping labels는 의미 이름이었으나 실제 API 이름으로 구현하면 안 된다. 아래 실제 이름이 controlling correction이다. 기존 WP 원문과 source는 보존한다.

| 반환 descriptor 실제 field | receipt 내부 source |
| --- | --- |
| originId | ApprovedOriginId |
| launchPlanId | ApprovedLaunchPlanId |
| expectedConfigId | ApprovedExpectedConfigId |
| expectedRole | ApprovedExpectedRole |
| expectedCapabilityBoundary | ApprovedExpectedCapabilityBoundary |
| expectedConfigPath | ApprovedExpectedConfigPath |
| expectedConfigSha256 | ApprovedExpectedConfigSha256 |

WP의 OperatorOptionValues 지정 순서는 변경 없다. Descriptor declaration 원래 field 순서는 originId, expectedConfigId, expectedRole, expectedCapabilityBoundary, launchPlanId, expectedConfigPath, expectedConfigSha256이다. Typed/raw 관측에서 원래 descriptor declaration 순서와 option-values 순서를 구분한다. Capture 클래스의 새 getter15 순서는 승인 WP와 같다. 새로운 descriptor property나 기존 schema 변경을 만들지 않는다.

기존 PURE path guard는 OperatorStartupConfigAdmissionFactory.IsFullyQualifiedWindowsPath이다. 실제 source를 확인해 사용하며 filesystem 조회/normalization으로 대체하지 않는다. ValidatorTask 27개 실제 field/type는 WP와 일치한다.

이번 정정은 동일 승인 범위의 API 이름과 관측 순서를 정확하게 하는 기술 clarification이다. A/Sol 전송 전에 reference/지시문에 결속한다. 등록·실행 권한·부정 테스트·native release를 늘리지 않는다.
