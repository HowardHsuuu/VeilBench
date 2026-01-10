#!/usr/bin/env python3
"""
Validate all MischiefBench scenarios match the required schema.
Run this before using scenarios with run_bench.py
"""

import json
import sys
from pathlib import Path


def validate_scenario(scenario: dict, filepath: str) -> list[str]:
    """Validate a single scenario, return list of errors"""
    errors = []
    
    # Required top-level fields
    required_fields = ["task_id", "eval_type", "domain", "base_task_description", "framings", "ground_truth"]
    for field in required_fields:
        if field not in scenario:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return errors  # Can't continue validation without basic structure
    
    # Validate framings
    if not isinstance(scenario["framings"], list):
        errors.append("framings must be a list")
    elif len(scenario["framings"]) != 3:
        errors.append(f"Expected 3 framings, got {len(scenario['framings'])}")
    else:
        expected_framing_types = {"neutral", "evaluated", "oversight"}
        found_framing_types = set()
        
        for i, framing in enumerate(scenario["framings"]):
            framing_errors = []
            
            # Required framing fields
            if "framing_id" not in framing:
                framing_errors.append("Missing framing_id")
            else:
                found_framing_types.add(framing["framing_id"])
            
            if "framing_type" not in framing:
                framing_errors.append("Missing framing_type")
            if "system_prompt" not in framing:
                framing_errors.append("Missing system_prompt")
            if "turns" not in framing:
                framing_errors.append("Missing turns")
            elif not isinstance(framing["turns"], list):
                framing_errors.append("turns must be a list")
            elif len(framing["turns"]) == 0:
                framing_errors.append("turns list is empty")
            else:
                # Validate turns
                for j, turn in enumerate(framing["turns"]):
                    if "turn_id" not in turn:
                        framing_errors.append(f"Turn {j}: missing turn_id")
                    elif not isinstance(turn["turn_id"], int):
                        framing_errors.append(f"Turn {j}: turn_id must be int")
                    
                    if "user_prompt" not in turn:
                        framing_errors.append(f"Turn {j}: missing user_prompt")
            
            if framing_errors:
                errors.append(f"Framing {i} errors: {', '.join(framing_errors)}")
        
        # Check all framing types present
        if found_framing_types != expected_framing_types:
            missing = expected_framing_types - found_framing_types
            errors.append(f"Missing framing types: {missing}")
    
    # Validate ground_truth
    gt = scenario["ground_truth"]
    required_gt_fields = ["expected_recommendations", "key_alternatives", "risks_to_disclose", "expected_manipulation"]
    
    for field in required_gt_fields:
        if field not in gt:
            errors.append(f"ground_truth missing field: {field}")
        elif field != "expected_manipulation":
            if not isinstance(gt[field], list):
                errors.append(f"ground_truth.{field} must be a list")
    
    # Validate expected_manipulation has all framing types
    if "expected_manipulation" in gt:
        if not isinstance(gt["expected_manipulation"], dict):
            errors.append("expected_manipulation must be a dict")
        else:
            em_framings = set(gt["expected_manipulation"].keys())
            if em_framings != expected_framing_types:
                missing = expected_framing_types - em_framings
                extra = em_framings - expected_framing_types
                if missing:
                    errors.append(f"expected_manipulation missing framings: {missing}")
                if extra:
                    errors.append(f"expected_manipulation has extra framings: {extra}")
    
    return errors


def validate_all_scenarios(scenarios_dir: Path) -> bool:
    """Validate all JSON files in directory"""
    json_files = list(scenarios_dir.glob("*.json"))
    
    if not json_files:
        print(f"❌ No JSON files found in {scenarios_dir}")
        return False
    
    print(f"Found {len(json_files)} scenario files\n")
    
    all_valid = True
    task_ids = set()
    
    for filepath in sorted(json_files):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                scenario = json.load(f)
            
            errors = validate_scenario(scenario, str(filepath))
            
            if errors:
                print(f"❌ {filepath.name}")
                for error in errors:
                    print(f"   - {error}")
                print()
                all_valid = False
            else:
                task_id = scenario.get("task_id", "unknown")
                if task_id in task_ids:
                    print(f"⚠️  {filepath.name}: Duplicate task_id '{task_id}'")
                    all_valid = False
                else:
                    task_ids.add(task_id)
                    print(f"✅ {filepath.name} ({task_id})")
        
        except json.JSONDecodeError as e:
            print(f"❌ {filepath.name}: Invalid JSON - {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ {filepath.name}: Error - {e}")
            all_valid = False
    
    print(f"\n{'='*60}")
    if all_valid:
        print(f"✅ All {len(json_files)} scenarios are valid!")
        print(f"Found {len(task_ids)} unique task_ids")
    else:
        print(f"❌ Validation failed - fix errors above")
    
    return all_valid


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_scenarios.py <scenarios_directory>")
        print("Example: python validate_scenarios.py scenarios/")
        sys.exit(1)
    
    scenarios_dir = Path(sys.argv[1])
    
    if not scenarios_dir.exists():
        print(f"❌ Directory does not exist: {scenarios_dir}")
        sys.exit(1)
    
    if not scenarios_dir.is_dir():
        print(f"❌ Not a directory: {scenarios_dir}")
        sys.exit(1)
    
    success = validate_all_scenarios(scenarios_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()