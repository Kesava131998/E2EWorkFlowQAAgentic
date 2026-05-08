import os
import json
import requests
from mcp.server.fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("postman")

@mcp.tool()
def create_postman_collection(collection_json: dict, workspace_id: str) -> str:
    """
    Uploads a Postman collection JSON to a specific workspace.
    
    Args:
        collection_json: The Postman Collection v2.1 object (as a dictionary).
        workspace_id: The ID of the Postman workspace to upload to.
    """
    api_key = os.environ.get("POSTMAN_API_KEY")
    if not api_key:
        return "Error: POSTMAN_API_KEY environment variable is not set."
        
    url = f"https://api.getpostman.com/collections?workspace={workspace_id}"
    
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Postman API requires the payload to be wrapped in a "collection" object
    payload = {"collection": collection_json}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in (200, 201):
        return f"Successfully created Postman collection. Response: {json.dumps(response.json())}"
    else:
        return f"Failed to create collection. Status code: {response.status_code}, Error: {response.text}"

if __name__ == "__main__":
    mcp.run_stdio()
