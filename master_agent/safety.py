"""Safety validation for generated skills before installation"""
import ast
import re

DANGEROUS_IMPORTS = {
    'subprocess', 'os.system', 'eval', 'exec',
    'socket', 'http.server', 'paramiko', 'fabric'
}

DANGEROUS_FUNCTIONS = {
    'system', 'popen', 'spawnl', 'execl',
    'eval', 'exec', 'compile', '__import__'
}

class SkillValidator:
    @staticmethod
    def validate_python_code(code: str) -> tuple[bool, str]:
        """Validate Python skill code for safety"""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(danger in alias.name for danger in DANGEROUS_IMPORTS):
                        return False, f"Dangerous import: {alias.name}"

            if isinstance(node, ast.ImportFrom):
                if node.module and any(danger in node.module for danger in DANGEROUS_IMPORTS):
                    return False, f"Dangerous import from: {node.module}"

            # Check function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in DANGEROUS_FUNCTIONS:
                        return False, f"Dangerous function call: {node.func.id}"

        return True, "Valid"

    @staticmethod
    def validate_systemd_service(content: str) -> tuple[bool, str]:
        """Validate systemd service file"""
        required_sections = ['[Unit]', '[Service]', '[Install]']
        for section in required_sections:
            if section not in content:
                return False, f"Missing required section: {section}"

        # Check for RestartSec
        if 'Restart=' not in content:
            return False, "Must have Restart= directive"

        return True, "Valid"

    @staticmethod
    def validate_json_schema(data: dict) -> tuple[bool, str]:
        """Validate skill registration schema"""
        required_fields = ['skill_id', 'type', 'created_at']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"

        if data['type'] not in ['python_function', 'systemd_service', 'bash_script']:
            return False, f"Invalid type: {data['type']}"

        return True, "Valid"
