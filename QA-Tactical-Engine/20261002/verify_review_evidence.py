import pathlib,json,re,hashlib
root=pathlib.Path(__file__).resolve().parent
read=lambda name:json.loads((root/name).read_text(encoding="utf-8-sig"))
core=read("run-results.json");multi=read("multi-map-results-v2.json");dep=read("dependency-results.json");cap=read("capacity-results.json");sem=read("semantic-audit.json");protect=read("protection-after.json")
tests={}
tests["A_noninteractive_actual_process"]=core["tests"]["launch_Independent1"]["visible_windows"]==[] and "RimWorld 1.6.4871" in core["tests"]["launch_Independent1"]["hello"]
tests["B_original_save_load"]="STATE: Playing, Maps=1, TicksGame=1823" in core["tests"]["load1"]["state"]
tests["C_actual_tick1000"]="StartTick=1823, EndTick=2823" in core["tests"]["tick1000"]["response"]
tests["D_native_export"]=core["tests"]["export1"]["response"].startswith("SAVED:") and (root/"Independent1/Saves/IndependentExport.rws").exists()
tests["E_fresh_process_reload"]=core["tests"]["launch_Independent1"]["pid"]!=core["tests"]["launch_Independent2"]["pid"] and "TicksGame=2823" in core["tests"]["load2"]["state"]
tests["F_bounded_pawn_key_fields"] = all(set(v)<= {"needs"} for v in sem["roundtrip"]["human_field_diffs"].values())
tests["F_full_graph_asserted"]=False
tests["non_target_map_progression_reproduced"]=all(x["changed_needs"] and x["changed_jobs"] and x["pos_before"]!=x["pos_after"] for x in sem["multi_map_changes"]["1"])
tests["world_progression_evidence"]=bool(sem["world_changed_components"])
tests["required_def_loss_reproduced"]=dep["tests"]["required_dependency_native"]["custom_item_count"]==1 and dep["tests"]["missing_effect"]["custom_item_count"]==0 and "STATE: Playing" in dep["tests"]["absent_load"]["last_status"]
tests["two_loaded_workers_simulate_and_export"]=all(cap["tests"]["simultaneous_burst"]["responses"][n]["response"].startswith("OK: Ran 10000") for n in ("worker1","worker2")) and cap["tests"]["export1"]["response"].startswith("SAVED:") and cap["tests"]["export2"]["response"].startswith("SAVED:")
tests["original_save_protected"]=core["tests"]["original_after"]["unchanged"] and protect["ExternalChangedCount"]==0
tests["production_requirements_unchanged"]=protect["ChangedCount"]==0 and protect["InputCount"]==55
tests["cleanup"]=protect["AnyRimWorldProcess"]==[] and protect["TemporaryFixtureJunctionAbsent"]
out={"work_package":"WP-QA-TAC-ENGINE-01","date":"2026-10-02 Asia/Seoul","core_engine_verdict":"PASS within bounded one-map simple-save scope; semantic roundtrip PARTIAL","architecture_invariants_verdict":"FAIL: non-target map/world progression and required-Def data loss reproduced","recommended_master_option":"OPTION 2","recommended_ADR002_status":"PROVISIONALLY ACCEPTED","required_followup":"POC-TAC-ENGINE-02","tests":tests,"GUI_control_performed":False,"production_modified":False,"ordinary_real_time_1x_cadence":"NOT TESTED","complex_graph":"NOT TESTED","selective_tick_adapter":"NOT TESTED; static hook candidates only"}
(root/"review-verification.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(out,ensure_ascii=False,indent=2))

