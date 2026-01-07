import mlflow
import argparse
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def promote_model(model_name, version, stage):
    """
    Promote a model version to a specific stage.
    """
    client = mlflow.tracking.MlflowClient()
    
    try:
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage,
            archive_existing_versions=True
        )
        logger.info(f"Successfully promoted {model_name} version {version} to {stage}")
    except Exception as e:
        logger.error(f"Error promoting model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Promote MLflow model to stage")
    parser.add_argument("--model-name", required=True, help="Name of the registered model")
    parser.add_argument("--version", required=True, help="Version number to promote")
    parser.add_argument("--stage", required=True, choices=["Staging", "Production", "Archived"], help="Target stage")
    
    args = parser.parse_args()
    
    promote_model(args.model_name, args.version, args.stage)
