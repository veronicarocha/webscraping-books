import logging
import json
import time
import os
from flask import request, g
from datetime import datetime, timezone

class StructuredLogger:
    def __init__(self, testing=False):
        self.logger = logging.getLogger('book_api')
        
        if self.logger.handlers:
            return
            
        self.logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": %(message)s}'
        )
        
        if not testing:
            # Handler para arquivo - apenas se não for teste
            try:
                log_dir = 'logs'
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                log_file = os.path.join(log_dir, 'api_monitor.log')
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                print(f" Não foi possível criar arquivo de log: {e}")
        
        # Handler pro consle (sempre ativo)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log_request(self, response=None):
        """Log para todas as requisições"""
        try:
            from flask import request, g

            request_time = getattr(g, 'request_time', None)
            processing_time = time.time() - request_time if request_time else 0

            log_data = {
                "method": request.method if request else "UNKNOWN",
                "endpoint": request.endpoint if request else "UNKNOWN",
                "path": request.path if request else "UNKNOWN",
                "status_code": response.status_code if response else None,
                "processing_time_seconds": round(processing_time, 3),
                "user_agent": request.user_agent.string if request and request.user_agent else None,
                "ip_address": request.remote_addr if request else None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            self.logger.info(json.dumps(log_data))
        
        except Exception as e:
            print(f" Erro no logging: {e}")

        return response

api_logger = StructuredLogger()