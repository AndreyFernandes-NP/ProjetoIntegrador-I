from src.mlearn.supervised import (LinearRegressionModel, KNNRegressorModel, 
                                   SVRModel, DecisionTreeRegressorModel, 
                                   RandomForestRegressorModel, GradientBoostingRegressorModel,
                                   LassoModel, RidgeModel, ExtraTreesRegressorModel, 
                                   HistGradientBoostingRegressorModel, BaseSupervisedModel)
from src.mlearn.unsupervised import (KMeansModel, DBSCANModel, 
                                     MeanShiftModel, AgglomerativeClusteringModel, 
                                     GaussianMixtureModel, BaseUnsupervisedModel)

UNSUPERVISED_MODEL_REGISTRY = {
    "KMeans": KMeansModel,
    "DBSCAN": DBSCANModel,
    "MeanShift": MeanShiftModel,
    "AgglomerativeClustering": AgglomerativeClusteringModel,
    "GaussianMixture": GaussianMixtureModel
}

SUPERVISED_MODEL_REGISTRY = {
    "LinearRegression": LinearRegressionModel,
    "KNNRegressor": KNNRegressorModel,
    "SVR": SVRModel,
    "DecisionTreeRegressor": DecisionTreeRegressorModel,
    "RandomForestRegressor": RandomForestRegressorModel,
    "GradientBoostingRegressor": GradientBoostingRegressorModel,
    "Lasso": LassoModel,
    "Ridge": RidgeModel,
    "ExtraTreesRegressor": ExtraTreesRegressorModel,
    "HistGradientBoostingRegressor": HistGradientBoostingRegressorModel,
}

def create_supervised_model(model_cfg: dict, global_config: dict | None = None) -> BaseSupervisedModel | None:
    model_name = model_cfg.get("nome")
    model_type = model_cfg.get("tipo", "").strip()
    
    if not model_type:
        print(f"[Aviso] Modelo '{model_name}' sem campo obrigatório 'tipo'.")
        return None

    model_class = SUPERVISED_MODEL_REGISTRY.get(model_type, None)

    if model_class is None:
        valid_models = ", ".join(SUPERVISED_MODEL_REGISTRY.keys())
        print(f"[Erro] Tipo de modelo supervisionado desconhecido: {model_type}")
        print(f"Tipos válidos são: {valid_models}")
        return None

    return model_class(model_name=model_name, model_type=model_type, config=model_cfg, global_config=global_config)

def create_unsupervised_model(model_cfg: dict, global_config: dict | None = None) -> BaseUnsupervisedModel | None:
    model_name = model_cfg.get("nome")
    model_type = model_cfg.get("tipo", "").strip()
    
    if not model_type:
        print(f"[Aviso] Modelo '{model_name}' sem campo obrigatório 'tipo'.")
        return None

    model_class = UNSUPERVISED_MODEL_REGISTRY.get(model_type, None)

    if model_class is None:
        valid_models = ", ".join(UNSUPERVISED_MODEL_REGISTRY.keys())
        print(f"[Erro] Tipo de modelo não supervisionado desconhecido: {model_type}")
        print(f"Tipos válidos são: {valid_models}")
        return None

    return model_class(model_name=model_name, model_type=model_type, config=model_cfg, global_config=global_config)
