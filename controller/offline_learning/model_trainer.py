"""
model_trainer.py
"""
import time
import pickle
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier
try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None
try:
    from lightgbm import LGBMClassifier
except ImportError:
    LGBMClassifier = None
try:
    from catboost import CatBoostClassifier
except ImportError:
    CatBoostClassifier = None

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from learning_schema import OfflineLearningError, ERROR_NO_VALID_MODEL

def train_and_evaluate(model_name, model_class, X_train, X_test, y_train, y_test):
    if model_class is None:
        return {"model": None, "accuracy": 0.0, "f1": 0.0, "precision": 0.0, "time": 0.0}
    
    start = time.time()
    try:
        model = model_class()
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="weighted")
        prec = precision_score(y_test, preds, average="weighted", zero_division=0)
    except Exception:
        return {"model": None, "accuracy": 0.0, "f1": 0.0, "precision": 0.0, "time": 0.0}
        
    elapsed = time.time() - start
    return {"model": model, "accuracy": acc, "f1": f1, "precision": prec, "time": elapsed}

def run_training_pipeline(X, y, output_models_dir):
    os.makedirs(output_models_dir, exist_ok=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    results = {}
    stats = {}
    
    models_to_train = {
        "rf": RandomForestClassifier,
        "xgb": XGBClassifier,
        "lgbm": LGBMClassifier,
        "cat": CatBoostClassifier
    }
    
    best_name = None
    best_f1 = -1.0
    best_prec = -1.0
    best_model = None
    
    for name, m_class in models_to_train.items():
        res = train_and_evaluate(name, m_class, X_train, X_test, y_train, y_test)
        if res["model"] is not None:
            model_path = os.path.join(output_models_dir, f"{name}.pkl")
            with open(model_path, "wb") as f:
                pickle.dump(res["model"], f)
                
            stats[name] = {"Accuracy": res["accuracy"], "F1": res["f1"], "Precision": res["precision"], "Time": res["time"]}
            
            if res["f1"] > best_f1 or (res["f1"] == best_f1 and res["precision"] > best_prec):
                best_f1 = res["f1"]
                best_prec = res["precision"]
                best_name = name
                best_model = res["model"]
        else:
            stats[name] = {"Accuracy": 0.0, "F1": 0.0, "Precision": 0.0, "Time": 0.0, "Status": "Failed/Missing Library"}
            
    # Minimal validation bound
    if best_model is None or best_f1 < 0.01:
        raise OfflineLearningError(ERROR_NO_VALID_MODEL, "All trained models failed minimum metric threshold.")
        
    prod_path = os.path.join(output_models_dir, "production_model.pkl")
    with open(prod_path, "wb") as f:
        pickle.dump(best_model, f)
        
    stats["Winner"] = best_name
    return best_model, stats
