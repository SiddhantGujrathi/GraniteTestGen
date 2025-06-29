import yaml
import json
from typing import Dict, List, Any

class SpecParser:
    @staticmethod
    def parse_openapi_spec(file_content: str, file_type: str) -> Dict[str, Any]:
        try:
            if file_type.lower() in ['yaml', 'yml']:
                spec = yaml.safe_load(file_content)
            else:
                spec = json.loads(file_content)
            
            return SpecParser._extract_api_info(spec)
        except Exception as e:
            raise ValueError(f"Failed to parse specification: {str(e)}")
    
    @staticmethod
    def _extract_api_info(spec: Dict) -> Dict[str, Any]:
        info = {
            'title': spec.get('info', {}).get('title', 'API'),
            'version': spec.get('info', {}).get('version', '1.0'),
            'description': spec.get('info', {}).get('description', ''),
            'base_url': spec.get('servers', [{}])[0].get('url', ''),
            'endpoints': []
        }
        
        paths = spec.get('paths', {})
        components = spec.get('components', {})
        schemas = components.get('schemas', {})
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    endpoint_info = {
                        'path': path,
                        'method': method.upper(),
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'parameters': details.get('parameters', []),
                        'request_body': details.get('requestBody', {}),
                        'responses': details.get('responses', {}),
                        'tags': details.get('tags', [])
                    }
                    info['endpoints'].append(endpoint_info)
        
        info['schemas'] = schemas
        return info
