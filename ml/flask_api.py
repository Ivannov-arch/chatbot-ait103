# ============================================================================
# chatbot/flask_api.py
#
# Flask REST API - connect your Python backend to the HTML frontend
#
# This allows your existing HTML frontend to communicate with the
# Python NLP pipeline via HTTP requests.
#
# Usage:
#   python flask_api.py --csv knowledge_base.csv --port 5000
#
# Then update your HTML to POST to http://localhost:5000/api/chat
# ============================================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import argparse
import os

from chatbot_main import XMUMChatbot, ResponseFormatter


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Global chatbot instance (initialized on startup)
chatbot = None


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint.
    
    Request body (JSON):
        {
            "message": "What is the library hours?",
            "debug": true  # optional, default false
        }
    
    Response (JSON):
        {
            "answer": "The library is open Monday-Friday 8am-8pm...",
            "confidence": 0.85,
            "matched_question": "When does the library open?",
            "module": "campus_life",
            "sub_intent": "library",
            "entities": {"facility": ["library"]},
            "debug": "[Module] campus_life | [Confidence] 2.5 | ..."
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' field"}), 400
        
        user_message = data['message'].strip()
        debug = data.get('debug', False)
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Process through chatbot pipeline
        response = chatbot.process_message(user_message, debug=debug)
        
        # Return as JSON
        return jsonify(ResponseFormatter.to_dict(response)), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """
    Get quick suggestion questions for the UI.
    
    Query parameters:
        module: The module to get suggestions for (default: all modules)
        limit: Max number of suggestions (default: 10)
    
    Response (JSON):
        {
            "suggestions": [
                "Who founded XMUM?",
                "When does the library open?",
                ...
            ]
        }
    """
    try:
        module = request.args.get('module')
        limit = int(request.args.get('limit', 10))
        
        suggestions = []
        
        if module:
            suggestions = chatbot.get_module_suggestions(module, limit)
        else:
            # Get from all modules (mix different types)
            all_suggestions = []
            for mod in ['admin_directory', 'campus_life', 'academic_navigation']:
                all_suggestions.extend(
                    chatbot.get_module_suggestions(mod, limit // 3)
                )
            suggestions = all_suggestions[:limit]
        
        return jsonify({"suggestions": suggestions}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "chatbot": "ready",
        "knowledge_base_size": len(chatbot.retriever.knowledge_base)
    }), 200


@app.route('/', methods=['GET'])
def index():
    """
    Simple landing page with API documentation.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>XMUMC Chatbot API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f4f8; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
            h1 { color: #1a3a5c; }
            code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
            pre { background: #f5f5f5; padding: 12px; border-left: 3px solid #1a3a5c; overflow-x: auto; }
            .endpoint { margin: 20px 0; padding: 15px; border-left: 3px solid #2e6da4; background: #f9fbfc; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 XMUMC Campus Assistant API</h1>
            <p>Backend API for the XMUMC chatbot. Connect your HTML frontend via HTTP requests.</p>
            
            <h2>Endpoints</h2>
            
            <div class="endpoint">
                <h3>POST /api/chat</h3>
                <p>Send a user message and get a chatbot response.</p>
                <pre>{
  "message": "What is the library hours?",
  "debug": true
}</pre>
                <p><strong>Response:</strong></p>
                <pre>{
  "answer": "The library is open...",
  "confidence": 0.85,
  "matched_question": "When does the library open?",
  "module": "campus_life",
  "sub_intent": "library",
  "entities": {"facility": ["library"]},
  "debug": "..."
}</pre>
            </div>
            
            <div class="endpoint">
                <h3>GET /api/suggestions</h3>
                <p>Get quick suggestions for the UI.</p>
                <p>Query params: <code>module</code>, <code>limit</code></p>
                <pre>GET /api/suggestions?module=campus_life&limit=5</pre>
            </div>
            
            <div class="endpoint">
                <h3>GET /api/health</h3>
                <p>Health check endpoint.</p>
            </div>
            
            <h2>Integration Example</h2>
            <p>In your HTML frontend (JavaScript):</p>
            <pre>// Send to backend
fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: userInput,
    debug: true
  })
})
.then(r => r.json())
.then(data => {
  console.log(data.answer);
  console.log('Confidence:', data.confidence);
  console.log('Module:', data.module);
});</pre>
        </div>
    </body>
    </html>
    """, 200


def initialize_chatbot():
    """Initialize the global chatbot instance."""
    global chatbot
    
    try:
        chatbot = XMUMChatbot()
        print(f" Chatbot initialized with Supabase")
        print(f"  Loaded {len(chatbot.retriever.knowledge_base)} knowledge items")
    except Exception as e:
        print(f" Error initializing chatbot: {e}")
        raise


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="XMUMC Chatbot Flask API (Supabase)")
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run on (default: 5000)'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host to bind to (default: localhost)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run Flask in debug mode'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize chatbot (loads from Supabase)
        initialize_chatbot()
        
        # Start Flask server
        print(f"\n Starting server on http://{args.host}:{args.port}")
        print(f" API Docs: http://{args.host}:{args.port}/")
        print("\nPress CTRL+C to stop.\n")
        
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    
    except Exception as e:
        print(f" Error: {e}")
        exit(1)
    except KeyboardInterrupt:
        print("\n\n Shutting down...")
        exit(0)


if __name__ == '__main__':
    main()
