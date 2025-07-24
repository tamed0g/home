from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

def create_flask_app():
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })
    
    @app.route('/info', methods=['GET'])
    def system_info():
        return jsonify({
            "app_name": "SmartHomeSystem",
            "version": "1.0.0",
            "environment": "development",
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route('/voice/command', methods=['POST'])
    def voice_command():
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({"error": "Missing 'text' field"}), 400
            
            text = data['text'].lower().strip()
            
            # Simple voice responses
            if "привет" in text or "hello" in text:
                response = "Привет! Как дела? Чем могу помочь?"
            elif "время" in text or "time" in text:
                response = f"Сейчас {datetime.now().strftime('%H:%M')}"
            elif "свет" in text and "включи" in text:
                response = "Включаю свет"
            elif "свет" in text and "выключи" in text:
                response = "Выключаю свет"
            else:
                response = "Извините, я не понял команду"
            
            return jsonify({
                "status": "success",
                "input": data['text'],
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return app