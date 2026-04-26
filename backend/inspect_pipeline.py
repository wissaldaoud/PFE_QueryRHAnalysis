"""Inspect pipeline_turnover.pkl features"""
import joblib
from pathlib import Path

model_path = Path(r"C:\Users\wdaoud\Documents\Models\pipeline_turnover.pkl")
pipeline = joblib.load(model_path)

print("=" * 80)
print("PIPELINE STRUCTURE")
print("=" * 80)
print(f"Pipeline steps: {pipeline.named_steps.keys() if hasattr(pipeline, 'named_steps') else 'Not a pipeline'}")
print()

if hasattr(pipeline, 'named_steps'):
    for step_name, step in pipeline.named_steps.items():
        print(f"Step: {step_name}")
        print(f"  Type: {type(step).__name__}")
        
        if hasattr(step, 'feature_names_in_'):
            print(f"  Features IN: {list(step.feature_names_in_)}")
        
        if hasattr(step, 'get_feature_names_out'):
            try:
                print(f"  Features OUT: {list(step.get_feature_names_out())}")
            except:
                pass
        
        if hasattr(step, 'transformers_'):
            print(f"  Column Transformer:")
            for name, trans, cols in step.transformers_:
                print(f"    - {name}: {type(trans).__name__} on {cols}")
        print()

print("=" * 80)
