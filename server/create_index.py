# file: create_index.py
from google.cloud import aiplatform
from config_manager import ConfigManager

# Get the single instance of the configuration
config = ConfigManager()

PROJECT_ID = config.PROJECT_ID
REGION = config.REGION
BUCKET_URI = config.BUCKET_URI
DIMENSIONS = config.DIMENSIONS

INDEX_DISPLAY_NAME = "cv-index"
DEPLOYED_INDEX_ID = "cv_index_1"

aiplatform.init(project=PROJECT_ID, location=REGION, staging_bucket=BUCKET_URI)

# Create the index (Tree-AH config; good default for text)
me_index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
    display_name=INDEX_DISPLAY_NAME,
    dimensions=DIMENSIONS,
    approximate_neighbors_count=150,
    distance_measure_type="DOT_PRODUCT_DISTANCE",
    index_update_method="STREAM_UPDATE",   # or "BATCH_UPDATE"
)

# Create endpoint and deploy the index
me_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
    display_name=f"{INDEX_DISPLAY_NAME}-endpoint",
    public_endpoint_enabled=True,  # use false + VPC if you want private only
)

me_endpoint = me_endpoint.deploy_index(
    index=me_index,
    deployed_index_id=DEPLOYED_INDEX_ID,
)

print("INDEX_ID:", me_index.resource_name.split("/")[-1])
print("ENDPOINT_ID:", me_endpoint.resource_name.split("/")[-1])
