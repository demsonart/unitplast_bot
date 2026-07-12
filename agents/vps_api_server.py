"""VPS API Server - listens for commands from Master Agent"""
import json
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from agents.skill_loader import SkillLoader

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "agents" / "skills"

# Initialize skill loader
skill_loader = SkillLoader(str(SKILLS_DIR))

# Authentication token
AUTH_TOKEN = os.getenv("MASTER_AGENT_TOKEN", "unitplast_master_key_2026")

def check_auth():
    """Verify request authentication"""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '')
    if token != AUTH_TOKEN:
        return False
    return True

@app.before_request
def authenticate():
    """Authenticate all requests except health"""
    if not request.path.startswith('/health'):
        if not check_auth():
            return jsonify({"error": "Unauthorized"}), 401

# ==================== HEALTH ENDPOINT ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "OK",
        "service": "VPS Agent API",
        "timestamp": datetime.now().isoformat(),
        "skills_loaded": len(skill_loader.loaded_skills),
        "skills_available": len(skill_loader.list_installed_skills())
    }), 200

# ==================== SKILL INSTALLATION ====================

@app.route('/api/install_skill', methods=['POST'])
def install_skill():
    """Install skill sent from Master Agent"""
    data = request.json
    skill_id = data.get('skill_id')
    skill_type = data.get('type')

    if not skill_id:
        return jsonify({"error": "Missing skill_id"}), 400

    try:
        if skill_type == 'python_function':
            code = data.get('code')
            if not code:
                return jsonify({"error": "Missing code"}), 400

            # Save skill
            if skill_loader.save_skill(skill_id, code):
                return jsonify({
                    "status": "saved",
                    "skill_id": skill_id,
                    "message": "Skill saved, ready to load"
                }), 200
            else:
                return jsonify({"error": "Failed to save skill"}), 500

        elif skill_type == 'systemd_service':
            service_content = data.get('service_content')
            # Would be installed by systemd on VPS
            return jsonify({
                "status": "acknowledged",
                "skill_id": skill_id,
                "message": "Systemd service received"
            }), 200

        else:
            return jsonify({"error": f"Unknown type: {skill_type}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== SKILL EXECUTION ====================

@app.route('/api/execute_skill/<skill_id>', methods=['POST'])
def execute_skill(skill_id):
    """Execute installed skill"""
    try:
        data = request.json or {}
        function_name = data.get('function', 'execute')
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})

        result = skill_loader.execute_skill(
            skill_id,
            function_name,
            *args,
            **kwargs
        )

        return jsonify({
            "status": "executed",
            "skill_id": skill_id,
            "result": result
        }), 200

    except Exception as e:
        return jsonify({
            "status": "failed",
            "skill_id": skill_id,
            "error": str(e)
        }), 500

# ==================== SKILL MANAGEMENT ====================

@app.route('/api/skills', methods=['GET'])
def list_skills():
    """List all installed skills"""
    skills = skill_loader.list_installed_skills()
    return jsonify({
        "total": len(skills),
        "skills": skills
    }), 200

@app.route('/api/skill/<skill_id>/info', methods=['GET'])
def get_skill_info(skill_id):
    """Get skill metadata"""
    info = skill_loader.get_skill_info(skill_id)
    if 'error' in info:
        return jsonify(info), 404
    return jsonify(info), 200

@app.route('/api/skill/<skill_id>/unload', methods=['POST'])
def unload_skill(skill_id):
    """Unload skill from memory"""
    if skill_loader.unload_skill(skill_id):
        return jsonify({
            "status": "unloaded",
            "skill_id": skill_id
        }), 200
    else:
        return jsonify({"error": "Failed to unload"}), 500

@app.route('/api/skill/<skill_id>/rollback', methods=['POST'])
def rollback_skill(skill_id):
    """Rollback skill to previous version"""
    data = request.json or {}
    backup_file = data.get('backup_file')

    if skill_loader.rollback_skill(skill_id, backup_file):
        return jsonify({
            "status": "rolled_back",
            "skill_id": skill_id
        }), 200
    else:
        return jsonify({"error": "Rollback failed"}), 500

# ==================== AGENT STATUS ====================

@app.route('/api/agent/status', methods=['GET'])
def agent_status():
    """Get VPS agent status"""
    skills = skill_loader.list_installed_skills()
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "skills_count": len(skills),
        "skills": [s['skill_id'] for s in skills]
    }), 200

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    port = int(os.getenv("VPS_API_PORT", 9000))
    host = os.getenv("VPS_API_HOST", "127.0.0.1")

    print(f"🚀 VPS API Server starting on {host}:{port}")
    print(f"Skills directory: {SKILLS_DIR}")

    app.run(host=host, port=port, debug=False)
