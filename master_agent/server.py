"""Master Agent HTTP Server - listens for requests from VPS agents"""
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify
from master_agent.skill_manager import SkillManager
from master_agent.skill_generator import SkillGenerator
from master_agent.safety import SkillValidator

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize managers
skill_manager = SkillManager()
skill_generator = SkillGenerator()
validator = SkillValidator()

# Authentication token (from environment or config)
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
    """Authenticate all requests"""
    if not request.path.startswith('/health'):
        if not check_auth():
            return jsonify({"error": "Unauthorized"}), 401

# ==================== HEALTH ENDPOINT ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "OK",
        "service": "Master Agent",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200

# ==================== SKILL REQUEST ENDPOINTS ====================

@app.route('/api/request_skill', methods=['POST'])
def request_skill():
    """VPS Agent requests a skill"""
    data = request.json
    agent_id = data.get('agent_id')
    issue = data.get('issue')
    skill_type = data.get('skill_type', 'python_function')

    if not agent_id or not issue:
        return jsonify({"error": "Missing agent_id or issue"}), 400

    # Check if similar skill already exists
    existing_skills = skill_manager.list_all_skills()
    for skill in existing_skills:
        if skill.get('purpose', '').lower() == issue.lower():
            skill_data = skill_manager.get_skill_for_vps(skill['skill_id'])
            return jsonify({
                "status": "found",
                "skill": skill_data,
                "message": "Existing skill found"
            }), 200

    # Generate new skill
    try:
        if skill_type == 'healing':
            error_log = data.get('error_log')
            generated = skill_generator.generate_healing_skill(agent_id, issue, error_log)
        elif skill_type == 'optimization':
            current = data.get('current_value', 0)
            target = data.get('target_value', 0)
            generated = skill_generator.generate_optimization_skill(issue, current, target)
        else:
            generated = skill_generator.generate_python_skill(
                f"skill_{agent_id}_{int(datetime.now().timestamp())}",
                issue,
                data.get('context')
            )

        if not generated:
            return jsonify({"error": "Failed to generate skill"}), 500

        # Validate generated code
        if generated['type'] == 'python_function':
            valid, msg = validator.validate_python_code(generated['code'])
            if not valid:
                return jsonify({
                    "status": "validation_failed",
                    "error": msg,
                    "skill": generated
                }), 400

        # Register skill
        skill_data = skill_manager.create_python_skill(
            generated['skill_id'],
            generated['code'],
            generated.get('dependencies', [])
        )

        return jsonify({
            "status": "generated",
            "skill": skill_data,
            "message": "New skill generated and registered"
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/skill/<skill_id>', methods=['GET'])
def get_skill(skill_id):
    """Get specific skill for installation"""
    skill = skill_manager.get_skill_for_vps(skill_id)
    if not skill:
        return jsonify({"error": "Skill not found"}), 404

    return jsonify(skill), 200

@app.route('/api/skills', methods=['GET'])
def list_skills():
    """List all available skills"""
    skills = skill_manager.list_all_skills()
    return jsonify({
        "total": len(skills),
        "skills": [{"skill_id": s["skill_id"], "type": s["type"]} for s in skills]
    }), 200

# ==================== INSTALLATION REPORTING ====================

@app.route('/api/report_installation', methods=['POST'])
def report_installation():
    """Agent reports skill installation result"""
    data = request.json
    agent_id = data.get('agent_id')
    skill_id = data.get('skill_id')
    success = data.get('success', False)
    message = data.get('message')

    if not agent_id or not skill_id:
        return jsonify({"error": "Missing agent_id or skill_id"}), 400

    report = skill_manager.install_skill_report(agent_id, skill_id, success, message)

    return jsonify({
        "status": "recorded",
        "report": report
    }), 200

# ==================== CAPABILITY ENDPOINTS ====================

@app.route('/api/agent/<agent_id>/capabilities', methods=['GET'])
def get_agent_capabilities(agent_id):
    """Get all skills installed on agent"""
    capabilities = skill_manager.get_agent_capabilities(agent_id)
    return jsonify(capabilities), 200

@app.route('/api/agent/<agent_id>/status', methods=['GET'])
def get_agent_status(agent_id):
    """Get agent status"""
    capabilities = skill_manager.get_agent_capabilities(agent_id)
    return jsonify({
        "agent_id": agent_id,
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "capabilities": capabilities
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
    port = int(os.getenv("MASTER_AGENT_PORT", 8888))
    host = os.getenv("MASTER_AGENT_HOST", "127.0.0.1")

    print(f"🚀 Master Agent Server starting on {host}:{port}")
    print(f"Auth Token: {AUTH_TOKEN[:10]}...")
    print(f"Skill registry: data/skills.json")

    app.run(host=host, port=port, debug=False)
