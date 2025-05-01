import os
import joblib

MODEL_DIR = os.path.dirname(__file__) 

def predict_on_last_document(df):
    try:
        classifier_path = os.path.join(MODEL_DIR, 'dog_behavior_classifier.joblib')
        encoder_path = os.path.join(MODEL_DIR, 'label_encoder.joblib')
        
        rf_classifier = joblib.load(classifier_path)
        label_encoder = joblib.load(encoder_path)
    except Exception as e:
        raise Exception(
            f"Error al cargar modelos: {str(e)}\n"
            f"Ruta esperada del clasificador: {classifier_path}\n"
            f"Archivos en {MODEL_DIR}: {os.listdir(MODEL_DIR)}"
        )       
    required_features = rf_classifier.feature_names_in_
    missing_features = set(required_features) - set(df.columns)
    
    if missing_features:
        raise ValueError(f"Missing features in csv document: {missing_features}")

    X = df[required_features]
    
    try:
        numeric_preds = rf_classifier.predict(X)
        text_preds = label_encoder.inverse_transform(numeric_preds)
        
        df['comp_pred'] = text_preds
        
        if hasattr(rf_classifier, 'predict_proba'):
            probas = rf_classifier.predict_proba(X)
            for i, class_name in enumerate(label_encoder.classes_):
                df[f'prob_{class_name}'] = probas[:, i]
                
        return df
    
    except Exception as e:
        print(f"Prediction failed: {str(e)}")
        return None



"""
result_df = predict_on_last_document(data_with_orientation)
if result_df is not None:
    print("Successfully processed last document with predictions:")
    print(result_df[['perro', 'timestamp', 'comp_pred']].head(20000))
else:
    print("Failed to process document")"
"""
