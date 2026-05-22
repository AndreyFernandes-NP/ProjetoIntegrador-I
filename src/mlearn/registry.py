from src.mlearn.supervised import LinearRegressionModel, KNNRegressorModel, SVRModel, DecisionTreeRegressorModel, RandomForestRegressorModel

SUPERVISED_MODEL_REGISTRY = {
    "LinearRegression": LinearRegressionModel,
    "KNNRegressor": KNNRegressorModel,
    "SVR": SVRModel,
    "DecisionTreeRegressor": DecisionTreeRegressorModel,
    "RandomForestRegressor": RandomForestRegressorModel,
}

def create_supervised_model(model_cfg: dict, global_config: dict | None = None):
    model_name = model_cfg.get("nome")
    model_type = model_cfg.get("tipo", "").strip()
    
    if not model_type:
        print(f"[Aviso] Modelo '{model_name}' sem campo obrigatório 'tipo'.")

    model_class = SUPERVISED_MODEL_REGISTRY.get(model_type, None)

    if model_class is None:
        print(f"[Erro] Tipo de modelo supervisionado desconhecido: {model_type}")
        return None

    return model_class(name=model_name, tipo=model_type, config=model_cfg, global_config=global_config)