import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.models import (
    Evaluation,
    Dataset,
    EvaluatorConfiguration,
    ConnectionType,
)

from azure.ai.evaluation import (
    RelevanceEvaluator, 
    GroundednessEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator,    
)

async def run_evaluation():
    try:
        
        _ = load_dotenv() 
        
        az_ai_deployment_name =  os.environ.get("AZURE_DEPLOYMENT_NAME")
        az_ai_api_version = os.environ.get("AZURE_OPENAI_API_VERSION")    
        az_ai_sub_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
        az_ai_ws_rg_name = os.environ.get("AZURE_WORKSPACE_RG_NAME")
        az_ai_ws_name = os.environ.get("AZURE_WORKSPACE_NAME")
        az_ai_ws_endpoint = os.environ.get("AZURE_WORKSPACE_ENDPOINT")

        az_ai_conn_str = f'{az_ai_ws_endpoint};{az_ai_sub_id};{az_ai_ws_rg_name};{az_ai_ws_name}'
        
        logger.info("----------------------------------------------------------------")
        logger.info("Process Started")
            
        project_client = AIProjectClient.from_connection_string(credential=DefaultAzureCredential(), conn_str=az_ai_conn_str)
        az_conn = await project_client.connections.get_default(connection_type=ConnectionType.AZURE_OPEN_AI)
        model_config = az_conn.to_evaluator_model_config(deployment_name=az_ai_deployment_name, api_version=az_ai_api_version)
        
        logger.info("----------------------------------------------------------------")
        logger.info("Prepare evaluators")
        data_mapping = {
            "response": "${data.response}", 
            "context": "${data.context}", 
            "query": "${data.query}",
        }

        evaluators={
            "coherence": EvaluatorConfiguration(
                id=CoherenceEvaluator.id,
                init_params={"model_config": model_config},
                data_mapping=data_mapping
            ),
            "relevance": EvaluatorConfiguration(
                id=RelevanceEvaluator.id,
                init_params={"model_config": model_config},
                data_mapping=data_mapping
            ),
            "fluency": EvaluatorConfiguration(
                id=FluencyEvaluator.id,
                init_params={"model_config": model_config},
                data_mapping=data_mapping
            ),
            "groundedness": EvaluatorConfiguration(
                id=GroundednessEvaluator.id,
                init_params={"model_config": model_config},
                data_mapping=data_mapping
            )
        }

        logger.info("----------------------------------------------------------------")
        logger.info("Upload File")
        
        data_id, _ = project_client.upload_file("./data.jsonl")
        evaluation_name="eval-cloud-via-sdk-"+str(datetime.now())

        evaluation = Evaluation(
            display_name=evaluation_name,
            description=evaluation_name,
            data=Dataset(id=data_id),
            evaluators=evaluators,
        )
            
        logger.info("----------------------------------------------------------------")
        logger.info("Create evaluation")
        
        response = await project_client.evaluations.create(evaluation=evaluation) 
        
        evaluation_id = response.id
        eval_status = response.status
        logger.info(f"Evaluation ID: {response.id}")
        logger.info(f"Status: {response.status}") #NotStarted, Queued, Running, Completed, Failed

        retry = 0
        max_retry = 30
        sleep_seconds = 15

        while eval_status not in ["Completed", "Failed"] and retry < max_retry:
            
            await asyncio.sleep(sleep_seconds)
            # Get evaluation status
            response = await project_client.evaluations.get(evaluation_id)
            eval_status = response.status
            retry += 1 

            logger.info("----------------------------------------------------------------")
            logger.info(f"Evaluation ID: {response.id}")
            logger.info(f"Status: {response.status}")
            logger.info(f"Retry: {retry}")

        logger.info(response)
        logger.info("Process Finished ")
        logger.info("----------------------------------------------------------------")
    except Exception as ex:
        logger.info(ex)


if __name__ == "__main__":    
    asyncio.run(run_evaluation())