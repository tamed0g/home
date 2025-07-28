from flask import Flask, request, jsonify
import asyncio
import re

def create_flask_app(yandex_station) -> Flask:
    """Flask приложение с поддержкой навыка Алисы"""
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    
    @app.route('/', methods=['GET'])
    def home():
        """Главная страница"""
        return jsonify({
            "name": "Smart Home System",
            "station": yandex_station.name,
            "status": "connected" if yandex_station.is_connected else "disconnected",
            "endpoints": {
                "GET /": "Информация",
                "GET /status": "Статус станции", 
                "POST /command": "Выполнить команду",
                "POST /play": "Включить музыку",
                "POST /stop": "Остановить",
                "POST /volume": "Громкость",
                "POST /say": "Сказать текст",
                "POST /alice": "Webhook для навыка Алисы"
            },
            "alice_webhook": "POST /alice - для интеграции с навыком Алисы"
        })
    
    @app.route('/status', methods=['GET'])
    def get_status():
        """Статус станции"""
        try:
            status = asyncio.run(yandex_station.get_status())
            return jsonify({"status": "success", "data": status})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    @app.route('/command', methods=['POST'])
    def execute_command():
        """Выполнить команду"""
        try:
            data = request.get_json() or {}
            command = data.get('command')
            params = data.get('params', {})
            
            if not command:
                return jsonify({"error": "Command required"}), 400
            
            result = asyncio.run(yandex_station.send_command(command, params))
            return jsonify({"success": True, "result": result})
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # 🎤 WEBHOOK ДЛЯ НАВЫКА АЛИСЫ
    @app.route('/alice', methods=['POST'])
    def alice_webhook():
        """Webhook для навыка Алисы"""
        try:
            data = request.get_json()
            
            # Простая структура ответа для Алисы
            def create_alice_response(text, end_session=False):
                return {
                    "response": {
                        "text": text,
                        "tts": text,
                        "end_session": end_session
                    },
                    "version": "1.0"
                }
            
            # Получаем команду от пользователя
            user_text = data.get("request", {}).get("original_utterance", "").lower()
            
            # Простой парсер команд
            response_text = "Не понимаю команду"
            
                       
            if "включи музыку" in user_text or "включить музыку" in user_text:
                genre = "популярная музыка"
                if "рок" in user_text:
                    genre = "рок"
                elif "джаз" in user_text:
                    genre = "джаз"
                elif "классика" in user_text:
                    genre = "классическая музыка"
                
                result = asyncio.run(yandex_station.send_command('play', {'query': genre}))
                response_text = f"Включаю {genre}"
            
            elif "выключи музыку" in user_text or "стоп" in user_text:
                result = asyncio.run(yandex_station.send_command('stop'))
                response_text = "Останавливаю музыку"
            
            elif "температур" in user_text:
                # Ищем число в команде
                numbers = re.findall(r'\d+', user_text)
                temp = int(numbers[0]) if numbers else 22
                
                result = asyncio.run(yandex_station.send_command('climate', {'temperature': temp, 'action': 'set_temp'}))
                response_text = f"Устанавливаю температуру {temp} градусов"
            
            elif "время" in user_text or "сколько время" in user_text:
                result = asyncio.run(yandex_station.send_command('time'))
                response_text = result.get('speech', 'Не могу определить время')
            
                       
            elif "погода" in user_text:
                result = asyncio.run(yandex_station.send_command('weather'))
                response_text = result.get('speech', 'Погода хорошая')
            
            elif "помощь" in user_text or "что умеешь" in user_text:
                response_text = """Я умею управлять умным домом:
                Управлять музыкой,
                Настраивать температуру,
                Говорить время и погоду.
                Попробуйте сказать: погода"""
            
            else:
                response_text = "Извините, не понимаю эту команду. Скажите 'помощь' чтобы узнать что я умею"
            
            return jsonify(create_alice_response(response_text))
            
        except Exception as e:
            return jsonify(create_alice_response("Произошла ошибка, попробуйте еще раз"))
    
    # Остальные endpoints
    @app.route('/play', methods=['POST'])
    def play():
        """Включить музыку"""
        try:
            data = request.get_json() or {}
            query = data.get('query', 'музыка')
            result = asyncio.run(yandex_station.send_command('play', {'query': query}))
            return jsonify({"success": True, "result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/stop', methods=['POST'])
    def stop():
        """Остановить"""
        try:
            result = asyncio.run(yandex_station.send_command('stop'))
            return jsonify({"success": True, "result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/volume', methods=['POST'])
    def volume():
        """Установить громкость"""
        try:
            data = request.get_json() or {}
            level = data.get('level', 50)
            result = asyncio.run(yandex_station.send_command('volume', {'level': level}))
            return jsonify({"success": True, "result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/say', methods=['POST'])
    def say():
        """Сказать текст"""
        try:
            data = request.get_json() or {}
            text = data.get('text', 'Привет!')
            result = asyncio.run(yandex_station.send_command('say', {'text': text}))
            return jsonify({"success": True, "result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/lights', methods=['POST'])
    def lights():
        """Управление светом"""
        try:
            data = request.get_json() or {}
            action = data.get('action', 'toggle')
            room = data.get('room', 'дом')
            result = asyncio.run(yandex_station.send_command('lights', {'action': action, 'room': room}))
            return jsonify({"success": True, "result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return app