import json
import os
from src.api.main import app

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')

os.makedirs(DOCS_DIR, exist_ok=True)

def generate_openapi():
    openapi_schema = app.openapi()
    with open(os.path.join(DOCS_DIR, 'openapi.json'), 'w') as f:
        json.dump(openapi_schema, f, indent=2)
        
    print("OpenAPI schema generated at docs/openapi.json")
    
    # Simple Postman Collection Generation
    postman_collection = {
        "info": {
            "name": "Nifty 100 API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }
    
    base_url = "http://localhost:8000"
    
    for path, path_item in openapi_schema.get('paths', {}).items():
        for method in path_item:
            if method.lower() == 'get':
                # Just mock some params
                req_path = path.replace('{ticker}', 'TCS').replace('{sector}', 'IT').replace('{group_name}', 'IT Giants')
                item = {
                    "name": f"{method.upper()} {path}",
                    "request": {
                        "method": method.upper(),
                        "url": {
                            "raw": f"{base_url}{req_path}",
                            "host": ["http://localhost:8000"],
                            "path": req_path.strip('/').split('/')
                        }
                    }
                }
                postman_collection["item"].append(item)
                
    with open(os.path.join(DOCS_DIR, 'postman_collection.json'), 'w') as f:
        json.dump(postman_collection, f, indent=2)
        
    print("Postman collection generated at docs/postman_collection.json")

if __name__ == '__main__':
    generate_openapi()
