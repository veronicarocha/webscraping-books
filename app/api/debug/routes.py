from flask import request, make_response, jsonify
from flask_restful import Resource
import os
import json

class DebugLogs(Resource):
    def get(self):
        """
        Endpoint para recuperar logs da API
        ---
        tags:
          - Debug
        parameters:
          - name: limit
            in: query
            type: integer
            required: false
            description: Número máximo de logs a retornar (padrão=1000)
          - name: level
            in: query
            type: string
            required: false
            description: Filtrar por nível (INFO, ERROR, WARNING)
          - name: format
            in: query
            type: string
            required: false
            description: Formato de retorno (json ou text)
        responses:
          200:
            description: Logs recuperados com sucesso
          404:
            description: Arquivo de logs não encontrado
          500:
            description: Erro ao ler logs
        """
        try:
            # Possíveis localizações do arquivo de log
            possible_paths = [
                os.path.join('logs', 'api_monitor.log'),
                os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs', 'api_monitor.log'),
                os.path.join(os.getcwd(), 'logs', 'api_monitor.log'),
                '/app/logs/api_monitor.log',  
            ]
            
            log_file_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    log_file_path = path
                    break
            
            if not log_file_path:
                return {
                    'error': 'Arquivo de logs não encontrado',
                    'searched_paths': possible_paths
                }, 404
            
            # Parâmetros da requisição
            limit = int(request.args.get('limit', 1000))
            level_filter = request.args.get('level', '').upper()
            format_type = request.args.get('format', 'json')
            
            logs = []
            with open(log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            log_data = json.loads(line.strip())
                            
                            # Aplicar filtro de nível se especificado
                            if level_filter and log_data.get('level') != level_filter:
                                continue
                                
                            logs.append(log_data)
                            
                            # Limitar número de logs
                            if len(logs) >= limit:
                                break
                                
                        except json.JSONDecodeError:
                            # Pular linhas inválidas
                            continue
            
            # Ordenar por timestamp (mais recentes primeiro)
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            if format_type == 'text':
                # Retornar como texto simples
                log_text = ""
                for log in logs:
                    timestamp = log.get('timestamp', '')
                    level = log.get('level', '')
                    module = log.get('module', '')
                    message = log.get('message', {})
                    
                    if isinstance(message, dict):
                        method = message.get('method', '')
                        path = message.get('path', '')
                        status_code = message.get('status_code', '')
                        log_text += f"{timestamp} | {level} | {module} | {method} {path} - {status_code}\n"
                    else:
                        log_text += f"{timestamp} | {level} | {module} | {message}\n"
                
                response = make_response(log_text)
                response.headers['Content-Type'] = 'text/plain; charset=utf-8'
                return response
            else:
                # Retornar como JSON
                return {
                    'total_logs': len(logs),
                    'logs': logs
                }
                
        except Exception as e:
            return {
                'error': f'Erro ao ler logs: {str(e)}'
            }, 500