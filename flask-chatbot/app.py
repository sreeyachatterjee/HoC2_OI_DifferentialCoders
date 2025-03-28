from flask import Flask, render_template, request, jsonify, session
import os
from werkzeug.utils import secure_filename
import openai
from dotenv import load_dotenv
import datetime
import base64
import logging
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def analyze_image_with_gpt4(image_data):
    """Analyze injury image using GPT-4 Vision"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """Analyze this injury and:
1. Identify the type of injury
2. Assess severity (mild/moderate/severe)
3. Provide immediate first aid steps
4. Suggest when to seek professional help
Be concise but thorough."""},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{image_data}",
                        },
                    ],
                }
            ],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return None

def generate_chat_response(messages):
    """Generate dynamic response using GPT-3.5-turbo"""
    try:
        # System message defines the assistant's behavior
        system_message = {
            "role": "system",
            "content": """You are a professional first aid assistant. Follow these rules:
1. Always respond to the user's input - never ignore it
2. Provide accurate first aid guidance
3. Ask relevant follow-up questions when needed
4. For emergencies, clearly state "EMERGENCY" and provide immediate steps
5. Be concise but thorough
6. Format steps clearly with numbers
7. Always recommend professional care when appropriate"""
        }

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[system_message] + messages,
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating chat response: {str(e)}")
        return "I'm having trouble processing your request. Please try again or call emergency services if this is urgent."

@app.route('/')
def home():
    # Initialize new conversation
    session.clear()
    session['conversation'] = []
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.form.get('user_message', '').strip()
        image_file = request.files.get('image')
        
        if not user_message and not image_file:
            return jsonify({"error": "Please describe your injury or upload an image"})
        
        # Initialize conversation if new
        if 'conversation' not in session:
            session['conversation'] = []
        
        # Process image if provided
        image_analysis = None
        image_url = None
        if image_file and allowed_file(image_file.filename):
            # Save image and get analysis
            image_bytes = image_file.read()
            image_data = base64.b64encode(image_bytes).decode('utf-8')
            image_analysis = analyze_image_with_gpt4(image_data)
            
            # Save thumbnail for display
            img = Image.open(io.BytesIO(image_bytes))
            img.thumbnail((300, 300))
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"thumb_{timestamp}.jpg"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img.save(save_path, 'JPEG', quality=85)
            image_url = f"uploads/{filename}"
            
            # Add image analysis to conversation
            if image_analysis:
                session['conversation'].append({
                    "role": "user",
                    "content": f"[Image uploaded] {image_analysis}"
                })
        
        # Add text message to conversation
        if user_message:
            session['conversation'].append({
                "role": "user",
                "content": user_message
            })
        
        # Generate response - ensure we always get one
        bot_response = generate_chat_response(session['conversation'])
        if not bot_response:
            bot_response = "Let me help with that. Please describe your injury in more detail."
        
        # Add bot response to conversation
        session['conversation'].append({
            "role": "assistant",
            "content": bot_response
        })
        
        return jsonify({
            "bot_response": bot_response,
            "image_url": image_url
        })
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": "We're experiencing technical difficulties",
            "bot_response": "I'm having trouble responding. For immediate help, please call emergency services if this is urgent."
        })

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)