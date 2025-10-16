from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from datetime import datetime, timedelta
import json
import base64

app = Flask(__name__)
CORS(app)

# Configure OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')

# User session management
user_sessions = {}
user_chat_histories = {}
user_reminders = {}
user_drawings = {}
user_uploaded_files = {}

class UserSession:
    def __init__(self, username):
        self.username = username
        self.login_time = datetime.now()
        self.questions_asked = 0
        self.topics_covered = set()
        self.quiz_scores = {}
        self.last_activity = datetime.now()
        self.theme_preference = "light"
    
    def update_activity(self):
        self.last_activity = datetime.now()
        self.questions_asked += 1
    
    def add_topic(self, topic):
        self.topics_covered.add(topic)
    
    def add_quiz_score(self, topic, score, total):
        self.quiz_scores[topic] = {"score": score, "total": total}
    
    def set_theme(self, theme):
        self.theme_preference = theme

# Enhanced knowledge base
knowledge_base = {
    "photosynthesis": "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to produce oxygen and energy in the form of sugar.",
    "python": "Python is a high-level, interpreted programming language known for its simple syntax and versatility. It's great for beginners!",
    "gravity": "Gravity is a force that attracts objects toward each other. On Earth, it gives weight to physical objects and causes them to fall toward the ground.",
    "mitosis": "Mitosis is a process of cell division that results in two identical daughter cells. It has phases: prophase, metaphase, anaphase, and telophase.",
    "algebra": "Algebra is a branch of mathematics dealing with symbols and the rules for manipulating those symbols to solve equations.",
    "water cycle": "The water cycle describes how water evaporates from the surface, rises into the atmosphere, cools and condenses into clouds, and falls back as precipitation.",
    "france": "The capital of France is Paris, known for the Eiffel Tower and rich cultural history.",
}

def get_ai_response(question):
    """Get response from AI"""
    try:
        question_lower = question.lower()
        
        greetings = ["hello", "hi", "hey", "greetings"]
        if any(greeting in question_lower for greeting in greetings):
            return "Hello! I'm your AI Tutoring Bot, here to help you learn and explore various subjects. I can assist with science, math, programming, history, and much more. What would you like to learn about today?"
        
        # Check knowledge base first
        for topic, answer in knowledge_base.items():
            if topic in question_lower:
                return f"**{topic.title()}**: {answer}\n\nWould you like me to explain any specific aspect of {topic} in more detail?"
        
        # Enhanced subject detection
        subjects = {
            "math": ["math", "mathematics", "algebra", "geometry", "calculus"],
            "science": ["science", "physics", "chemistry", "biology"],
            "programming": ["programming", "coding", "python", "javascript", "java"],
            "history": ["history", "historical", "past events"],
            "geography": ["geography", "countries", "capitals"]
        }
        
        for subject, keywords in subjects.items():
            if any(keyword in question_lower for keyword in keywords):
                return f"I'd be happy to help you with {subject}! Could you be more specific about what you'd like to learn? For example, you could ask about specific concepts, theories, or applications in {subject}."
        
        return f"Thank you for your question about '{question}'. I'm designed to help students learn various subjects. I can provide explanations, examples, and guidance on topics like:\n\n• Mathematics (algebra, geometry, calculus)\n• Science (physics, chemistry, biology)\n• Programming (Python, web development)\n• History and social studies\n• Language arts\n\nCould you tell me which subject area you're most interested in, or ask me a more specific question?"
        
    except Exception as e:
        print(f"Error in AI response: {e}")
        return "I apologize, but I'm having trouble processing your question right now. Please try again with a different question about your learning topic."

# ============================================
# STUDY REMINDERS ENDPOINTS
# ============================================

@app.route("/reminders/<username>", methods=["GET"])
def get_reminders(username):
    """Get all reminders for a user"""
    if username not in user_reminders:
        user_reminders[username] = []
    
    # Filter out past reminders
    current_time = datetime.now()
    active_reminders = [r for r in user_reminders[username] if datetime.fromisoformat(r['datetime']) > current_time]
    user_reminders[username] = active_reminders
    
    return jsonify({"reminders": active_reminders})

@app.route("/reminders/<username>/add", methods=["POST"])
def add_reminder(username):
    """Add a new study reminder"""
    try:
        data = request.get_json()
        title = data.get("title", "")
        subject = data.get("subject", "")
        datetime_str = data.get("datetime", "")
        notes = data.get("notes", "")
        
        if not title or not datetime_str:
            return jsonify({"error": "Title and datetime are required"}), 400
        
        # Validate datetime format
        try:
            reminder_datetime = datetime.fromisoformat(datetime_str)
        except:
            return jsonify({"error": "Invalid datetime format"}), 400
        
        if username not in user_reminders:
            user_reminders[username] = []
        
        reminder = {
            "id": len(user_reminders[username]) + 1,
            "title": title,
            "subject": subject,
            "datetime": datetime_str,
            "notes": notes,
            "created_at": datetime.now().isoformat()
        }
        
        user_reminders[username].append(reminder)
        
        return jsonify({
            "status": "reminder added",
            "reminder": reminder
        })
        
    except Exception as e:
        print(f"Error adding reminder: {e}")
        return jsonify({"error": "Failed to add reminder"}), 500

@app.route("/reminders/<username>/delete/<int:reminder_id>", methods=["DELETE"])
def delete_reminder(username, reminder_id):
    """Delete a specific reminder"""
    if username not in user_reminders:
        return jsonify({"error": "No reminders found"}), 404
    
    user_reminders[username] = [r for r in user_reminders[username] if r['id'] != reminder_id]
    
    return jsonify({"status": "reminder deleted"})

# ============================================
# DRAWING BOARD ENDPOINTS
# ============================================

@app.route("/drawings/<username>/save", methods=["POST"])
def save_drawing(username):
    """Save a drawing"""
    try:
        data = request.get_json()
        drawing_data = data.get("drawing", "")
        title = data.get("title", "Untitled Drawing")
        subject = data.get("subject", "")
        
        if not drawing_data:
            return jsonify({"error": "Drawing data is required"}), 400
        
        if username not in user_drawings:
            user_drawings[username] = []
        
        drawing = {
            "id": len(user_drawings[username]) + 1,
            "title": title,
            "subject": subject,
            "data": drawing_data,
            "created_at": datetime.now().isoformat()
        }
        
        user_drawings[username].append(drawing)
        
        return jsonify({
            "status": "drawing saved",
            "drawing": {
                "id": drawing["id"],
                "title": drawing["title"],
                "subject": drawing["subject"],
                "created_at": drawing["created_at"]
            }
        })
        
    except Exception as e:
        print(f"Error saving drawing: {e}")
        return jsonify({"error": "Failed to save drawing"}), 500

@app.route("/drawings/<username>", methods=["GET"])
def get_drawings(username):
    """Get all drawings for a user"""
    if username not in user_drawings:
        user_drawings[username] = []
    
    # Return without full drawing data (too large)
    drawings_list = [{
        "id": d["id"],
        "title": d["title"],
        "subject": d["subject"],
        "created_at": d["created_at"]
    } for d in user_drawings[username]]
    
    return jsonify({"drawings": drawings_list})

@app.route("/drawings/<username>/<int:drawing_id>", methods=["GET"])
def get_drawing(username, drawing_id):
    """Get a specific drawing with full data"""
    if username not in user_drawings:
        return jsonify({"error": "No drawings found"}), 404
    
    drawing = next((d for d in user_drawings[username] if d['id'] == drawing_id), None)
    
    if not drawing:
        return jsonify({"error": "Drawing not found"}), 404
    
    return jsonify({"drawing": drawing})

@app.route("/drawings/<username>/<int:drawing_id>", methods=["DELETE"])
def delete_drawing(username, drawing_id):
    """Delete a specific drawing"""
    if username not in user_drawings:
        return jsonify({"error": "No drawings found"}), 404
    
    user_drawings[username] = [d for d in user_drawings[username] if d['id'] != drawing_id]
    
    return jsonify({"status": "drawing deleted"})

# ============================================
# FILE UPLOAD ENDPOINTS
# ============================================

@app.route("/files/<username>/upload", methods=["POST"])
def upload_file(username):
    """Upload a file and get AI help"""
    try:
        data = request.get_json()
        file_data = data.get("file", "")
        file_name = data.get("fileName", "")
        file_type = data.get("fileType", "")
        question = data.get("question", "")
        
        if not file_data or not file_name:
            return jsonify({"error": "File data and name are required"}), 400
        
        if username not in user_uploaded_files:
            user_uploaded_files[username] = []
        
        file_record = {
            "id": len(user_uploaded_files[username]) + 1,
            "fileName": file_name,
            "fileType": file_type,
            "data": file_data,
            "question": question,
            "uploaded_at": datetime.now().isoformat()
        }
        
        user_uploaded_files[username].append(file_record)
        
        # Generate response based on file type
        if file_type.startswith('image/'):
            response = f"I can see you've uploaded an image: '{file_name}'. "
            if question:
                response += f"Regarding your question '{question}', I'll help you analyze this image. "
            response += "Please describe what you need help with in the image, such as:\n\n"
            response += "• Solving a math problem shown in the image\n"
            response += "• Understanding a diagram or concept\n"
            response += "• Analyzing a chart or graph\n"
            response += "• Getting help with handwritten notes\n\n"
            response += "The more specific you are, the better I can assist you!"
        else:
            response = f"I've received your file: '{file_name}'. "
            if question:
                response += f"You asked: '{question}'. "
            response += "I'm analyzing your file. Please provide more details about what you need help with!"
        
        return jsonify({
            "status": "file uploaded",
            "fileId": file_record["id"],
            "response": response
        })
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        return jsonify({"error": "Failed to upload file"}), 500

@app.route("/files/<username>", methods=["GET"])
def get_uploaded_files(username):
    """Get all uploaded files for a user"""
    if username not in user_uploaded_files:
        user_uploaded_files[username] = []
    
    # Return without full file data
    files_list = [{
        "id": f["id"],
        "fileName": f["fileName"],
        "fileType": f["fileType"],
        "question": f["question"],
        "uploaded_at": f["uploaded_at"]
    } for f in user_uploaded_files[username]]
    
    return jsonify({"files": files_list})

# ============================================
# EXISTING ENDPOINTS
# ============================================

@app.route("/session/<username>", methods=["GET"])
def get_session(username):
    if username in user_sessions:
        session = user_sessions[username]
        return jsonify({
            "username": session.username,
            "questions_asked": session.questions_asked,
            "topics_covered": list(session.topics_covered),
            "quiz_scores": session.quiz_scores,
            "theme_preference": session.theme_preference,
            "session_duration": str(datetime.now() - session.login_time)
        })
    return jsonify({"error": "Session not found"}), 404

@app.route("/session/<username>/update", methods=["POST"])
def update_session(username):
    data = request.get_json()
    topic = data.get("topic", "")
    
    if username in user_sessions:
        session = user_sessions[username]
        session.update_activity()
        if topic:
            session.add_topic(topic)
        return jsonify({"status": "updated"})
    
    user_sessions[username] = UserSession(username)
    session = user_sessions[username]
    session.update_activity()
    if topic:
        session.add_topic(topic)
    return jsonify({"status": "created and updated"})

@app.route("/session/<username>/quiz", methods=["POST"])
def add_quiz_score(username):
    data = request.get_json()
    topic = data.get("topic", "")
    score = data.get("score", 0)
    total = data.get("total", 1)
    
    if username in user_sessions:
        session = user_sessions[username]
        session.add_quiz_score(topic, score, total)
        return jsonify({"status": "quiz score added"})
    
    user_sessions[username] = UserSession(username)
    session = user_sessions[username]
    session.add_quiz_score(topic, score, total)
    return jsonify({"status": "session created and quiz score added"})

@app.route("/session/<username>/theme", methods=["POST"])
def update_theme(username):
    data = request.get_json()
    theme = data.get("theme", "light")
    
    if username in user_sessions:
        session = user_sessions[username]
        session.set_theme(theme)
        return jsonify({"status": "theme updated", "theme": theme})
    return jsonify({"error": "Session not found"}), 404

@app.route("/session/create", methods=["POST"])
def create_session():
    data = request.get_json()
    username = data.get("username", "")
    
    if username:
        user_sessions[username] = UserSession(username)
        if username not in user_chat_histories:
            user_chat_histories[username] = []
        return jsonify({"status": "session created"})
    return jsonify({"error": "Username required"}), 400

@app.route("/chat/<username>/history", methods=["GET"])
def get_chat_history(username):
    if username in user_chat_histories:
        return jsonify({
            "history": user_chat_histories[username],
            "count": len(user_chat_histories[username])
        })
    return jsonify({"history": [], "count": 0})

@app.route("/chat/<username>/save", methods=["POST"])
def save_chat_message(username):
    data = request.get_json()
    message = data.get("message", "")
    sender = data.get("sender", "user")
    timestamp = data.get("timestamp", datetime.now().isoformat())
    
    if username not in user_chat_histories:
        user_chat_histories[username] = []
    
    chat_entry = {
        "message": message,
        "sender": sender,
        "timestamp": timestamp
    }
    
    user_chat_histories[username].append(chat_entry)
    
    if len(user_chat_histories[username]) > 100:
        user_chat_histories[username] = user_chat_histories[username][-100:]
    
    return jsonify({"status": "message saved", "count": len(user_chat_histories[username])})

@app.route("/chat/<username>/clear", methods=["POST"])
def clear_chat_history(username):
    if username in user_chat_histories:
        user_chat_histories[username] = []
        return jsonify({"status": "chat history cleared"})
    return jsonify({"error": "User not found"}), 404

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "AI Tutoring Bot Backend is running",
        "version": "4.0",
        "features": [
            "Enhanced responses",
            "Multiple subjects",
            "Interactive learning",
            "Session management",
            "Quiz system",
            "Chat history",
            "Theme support",
            "Study reminders",
            "Drawing board",
            "File upload"
        ]
    })

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        question = data.get("question", "").strip()
        username = data.get("username", "")
        
        if not question:
            return jsonify({"answer": "Please ask a question! I'm here to help you learn."}), 400
        
        print(f"Question received from {username}: {question}")
        
        answer = get_ai_response(question)
        print(f"Answer: {answer}")
        
        if username:
            if username not in user_chat_histories:
                user_chat_histories[username] = []
            
            user_chat_histories[username].append({
                "message": question,
                "sender": "user",
                "timestamp": datetime.now().isoformat()
            })
            
            user_chat_histories[username].append({
                "message": answer,
                "sender": "bot",
                "timestamp": datetime.now().isoformat()
            })
            
            if len(user_chat_histories[username]) > 100:
                user_chat_histories[username] = user_chat_histories[username][-100:]
        
        return jsonify({
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print("Error:", e)
        return jsonify({
            "answer": "I apologize, but I encountered an error while processing your question. Please try again in a moment.",
            "error": True
        }), 500

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "operational",
        "model": "AI Tutoring Bot v4.0",
        "subjects_supported": ["Math", "Science", "Programming", "History", "Geography"],
        "active_sessions": len(user_sessions),
        "users_with_chat_history": len(user_chat_histories),
        "total_reminders": sum(len(r) for r in user_reminders.values()),
        "total_drawings": sum(len(d) for d in user_drawings.values()),
        "total_files": sum(len(f) for f in user_uploaded_files.values()),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Enhanced AI Tutoring Bot Backend Starting...")
    print("="*60)
    print("📚 Server running on: http://localhost:5000")
    print("🎯 Enhanced features activated")
    print("📖 Multiple subjects supported")
    print("💤 Session management enabled")
    print("📝 Quiz system ready")
    print("💬 Chat history system active")
    print("🌙 Dark mode support added")
    print("⏰ Study reminders enabled")
    print("🎨 Drawing board available")
    print("📁 File upload system ready")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)