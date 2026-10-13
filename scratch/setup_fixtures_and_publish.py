#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_fixtures_and_publish.py

Prepares task-owned fixtures for Gate05-R29 and executes the standalone publisher
(publish_operator_pair.py) across 6 positive normal cases, capturing full telemetry.
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from datetime import datetime, timezone

WORKSPACE_ROOT = os.path.abspath(".")
FIXTURES_DIR = os.path.join(WORKSPACE_ROOT, "scratch", "EngineGate05R29StartupPair", "Fixtures")
PUBLISHED_DIR = os.path.join(WORKSPACE_ROOT, "scratch", "EngineGate05R29StartupPair", "PublishedPairs")
PUBLISHER_SCRIPT = os.path.join(WORKSPACE_ROOT, "scratch", "OperatorStartupPairR29", "publish_operator_pair.py")

os.makedirs(FIXTURES_DIR, exist_ok=True)
os.makedirs(PUBLISHED_DIR, exist_ok=True)

def make_config(config_id: str, role: str, desc_suffix: str = "") -> str:
    # Exactly 14 closed fields
    cfg = {
        "schemaVersion": "WE-OPERATOR-BOOTSTRAP-V1",
        "configId": config_id,
        "role": role,
        "admittedValidatorExecutablePath": os.path.join(WORKSPACE_ROOT, f"scratch\\SimExe_{role}.exe"),
        "admittedValidatorExecutableSha256": "A" * 64,
        "validatorArguments": "",
        "workerUserDataDirectory": os.path.join(WORKSPACE_ROOT, f"scratch\\WorkerUserData_{role}_{desc_suffix}"),
        "validatorUserDataDirectory": os.path.join(WORKSPACE_ROOT, f"scratch\\ValidatorUserData_{role}_{desc_suffix}"),
        "workerCwd": os.path.join(WORKSPACE_ROOT, f"scratch\\WorkerCwd_{role}_{desc_suffix}"),
        "validatorCwd": os.path.join(WORKSPACE_ROOT, f"scratch\\ValidatorCwd_{role}_{desc_suffix}"),
        "capabilityBoundary": "LOCAL_SANDBOXED",
        "issuedAtUtc": "2026-10-12T00:00:00.0000000Z",
        "expectedContentProfileFingerprint": "B" * 64,
        "expectedPackagePolicyDeclaration": {
            "schemaVersion": "WE-PACKAGE-POLICY-V1",
            "policyId": f"qa.R29.policy.{desc_suffix}",
            "revision": "29",
            "admittedPackageIds": ["ludeon.rimworld", "example.qa.normal"]
        }
    }
    return json.dumps(cfg, separators=(',', ':'), ensure_ascii=False)


# Define 6 cases
cases_def = [
    {
        "case_index": 1,
        "case_id": "PLAIN_PLAIN",
        "pair_id": "WE-PAIR-DEV-R29-PLAIN-PLAIN-01",
        "parent_origin": "qa.R29.parent.origin.plain",
        "parent_plan": "qa.R29.parent.plan.plain",
        "child_origin": "qa.R29.child.origin.plain",
        "child_plan": "qa.R29.child.plan.plain",
        "desc_suffix": "plain"
    },
    {
        "case_index": 2,
        "case_id": "OPAQUE_OPAQUE",
        "pair_id": "WE-PAIR-DEV-R29-OPAQUE-OPAQUE-02",
        "parent_origin": "  qa.R29.parent.origin.opaque.Ω  ",
        "parent_plan": "  qa.R29.parent.plan.opaque.Ω  ",
        "child_origin": "  qa.R29.child.origin.opaque.Ω  ",
        "child_plan": "  qa.R29.child.plan.opaque.Ω  ",
        "desc_suffix": "opaque"
    },
    {
        "case_index": 3,
        "case_id": "PLAIN_OPAQUE_PADDED",
        "pair_id": "WE-PAIR-DEV-R29-PLAIN-OPAQUE-03",
        "parent_origin": "qa.R29.parent.origin.plain3",
        "parent_plan": "qa.R29.parent.plan.plain3",
        "child_origin": "  qa.R29.child.origin.opaque3.Ω  ",
        "child_plan": "  qa.R29.child.plan.opaque3.Ω  ",
        "desc_suffix": "mixed_po"
    },
    {
        "case_index": 4,
        "case_id": "OPAQUE_PLAIN_PADDED",
        "pair_id": "WE-PAIR-DEV-R29-OPAQUE-PLAIN-04",
        "parent_origin": "  qa.R29.parent.origin.opaque4.Ω  ",
        "parent_plan": "  qa.R29.parent.plan.opaque4.Ω  ",
        "child_origin": "qa.R29.child.origin.plain4",
        "child_plan": "qa.R29.child.plan.plain4",
        "desc_suffix": "mixed_op"
    },
    {
        "case_index": 5,
        "case_id": "PAIR_ID_WITH_EQUALS",
        "pair_id": "WE=PAIR=DEV=R29=EQUALS=05",
        "parent_origin": "qa.R29.parent.origin.eq",
        "parent_plan": "qa.R29.parent.plan.eq",
        "child_origin": "qa.R29.child.origin.eq",
        "child_plan": "qa.R29.child.plan.eq",
        "desc_suffix": "case5_eq"
    },
    {
        "case_index": 6,
        "case_id": "UNICODE_BACKSLASH_QUOTE_EQUALS",
        "pair_id": "WE-PAIR-DEV-R29-Ω-\"QUOTE\"=\\BACKSLASH\\-06",
        "parent_origin": "qa.R29.parent.origin.Ω-\"quoted\"=\\path\\-06",
        "parent_plan": "qa.R29.parent.plan.Ω-\"quoted\"=\\path\\-06",
        "child_origin": "qa.R29.child.origin.Ω-\"quoted\"=\\path\\-06",
        "child_plan": "qa.R29.child.plan.Ω-\"quoted\"=\\path\\-06",
        "desc_suffix": "case6_special"
    }
]

# Write all config files
specs = []
for c in cases_def:
    idx = c["case_index"]
    p_cfg_path = os.path.join(FIXTURES_DIR, f"parent_config_{idx:02d}.json")
    c_cfg_path = os.path.join(FIXTURES_DIR, f"child_config_{idx:02d}.json")
    
    p_json = make_config(f"qa.R29.parent.cfg.{idx}", "SIMULATION", c["desc_suffix"])
    c_json = make_config(f"qa.R29.child.cfg.{idx}", "READ_ONLY", c["desc_suffix"])
    
    p_bytes = p_json.encode('utf-8')
    c_bytes = c_json.encode('utf-8')
    
    with open(p_cfg_path, "wb") as f:
        f.write(p_bytes)
    with open(c_cfg_path, "wb") as f:
        f.write(c_bytes)
        
    p_sha = hashlib.sha256(p_bytes).hexdigest().upper()
    c_sha = hashlib.sha256(c_bytes).hexdigest().upper()
    
    p_decl = {
        "originId": c["parent_origin"],
        "expectedConfigId": f"qa.R29.parent.cfg.{idx}",
        "expectedRole": "SIMULATION",
        "expectedCapabilityBoundary": "LOCAL_SANDBOXED",
        "launchPlanId": c["parent_plan"],
        "expectedConfigPath": p_cfg_path,
        "expectedConfigSha256": p_sha
    }
    
    c_decl = {
        "originId": c["child_origin"],
        "expectedConfigId": f"qa.R29.child.cfg.{idx}",
        "expectedRole": "READ_ONLY",
        "expectedCapabilityBoundary": "LOCAL_SANDBOXED",
        "launchPlanId": c["child_plan"],
        "expectedConfigPath": c_cfg_path,
        "expectedConfigSha256": c_sha
    }
    
    case_out_dir = os.path.join(PUBLISHED_DIR, f"case_{idx:02d}")
    os.makedirs(case_out_dir, exist_ok=True)
    
    spec = {
        "case_index": idx,
        "case_id": c["case_id"],
        "operatorPairId": c["pair_id"],
        "parentDeclaration": p_decl,
        "childDeclaration": c_decl,
        "parentConfigPath": p_cfg_path,
        "childConfigPath": c_cfg_path,
        "outputDir": case_out_dir,
        "bundleFilename": "operator_startup_pair.json"
    }
    spec_path = os.path.join(case_out_dir, "publish_spec.json")
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
        
    specs.append({
        "spec_path": spec_path,
        "case_info": c,
        "parentConfigPath": p_cfg_path,
        "childConfigPath": c_cfg_path,
        "parentSha": p_sha,
        "childSha": c_sha,
        "outputDir": case_out_dir
    })

print(f"Materialized {len(specs)} fixture pairs and publish specs.")

# Run publisher for each case via subprocess, capturing full telemetry
evidence = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "publisher_script": PUBLISHER_SCRIPT,
    "publisher_sha256": hashlib.sha256(open(PUBLISHER_SCRIPT, "rb").read()).hexdigest().upper(),
    "python_executable": sys.executable,
    "total_cases": len(specs),
    "cases": []
}

for s in specs:
    spec_path = s["spec_path"]
    t0 = time.perf_counter()
    cmd = [sys.executable, PUBLISHER_SCRIPT, "--spec", spec_path]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE_ROOT)
    t1 = time.perf_counter()
    duration_sec = t1 - t0
    
    if proc.returncode != 0:
        raise RuntimeError(f"Publisher failed on {spec_path} with code {proc.returncode}: {proc.stderr}")
        
    pub_result = json.loads(proc.stdout)
    bundle_path = pub_result["bundlePath"]
    bundle_bytes = open(bundle_path, "rb").read()
    bundle_sha = hashlib.sha256(bundle_bytes).hexdigest().upper()
    
    case_record = {
        "case_index": s["case_info"]["case_index"],
        "case_id": s["case_info"]["case_id"],
        "operatorPairId": s["case_info"]["pair_id"],
        "exit_code": proc.returncode,
        "duration_seconds": round(duration_sec, 6),
        "argv": cmd,
        "cwd": WORKSPACE_ROOT,
        "bundle_file": {
            "path": bundle_path,
            "sha256": bundle_sha,
            "bytes": len(bundle_bytes)
        },
        "provenance_manifest": pub_result["manifestPath"],
        "parent_config": {
            "path": s["parentConfigPath"],
            "sha256": s["parentSha"]
        },
        "child_config": {
            "path": s["childConfigPath"],
            "sha256": s["childSha"]
        },
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip()
    }
    evidence["cases"].append(case_record)
    print(f"Case {s['case_info']['case_index']} ({s['case_info']['case_id']}): Published successfully in {duration_sec:.4f}s. Bundle SHA: {bundle_sha}")

evidence_path = os.path.join("Dispatcher", "A_TASKS", "WE-A-ENGINE-GATE05-R29-STARTUP-PAIR-20261012-DIRECT-46f60e2a", "PRODUCER_PUBLICATION_EVIDENCE.json")
with open(evidence_path, "w", encoding="utf-8") as f:
    json.dump(evidence, f, indent=2, ensure_ascii=False)

print(f"\nPRODUCER_PUBLICATION_EVIDENCE.json written to {evidence_path}.")
