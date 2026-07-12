"""Skill Loader - dynamically loads and manages installed skills"""
import importlib.util
import sys
import os
from pathlib import Path
from typing import Any, Callable

class SkillLoader:
    def __init__(self, skills_dir: str = "agents/skills"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_skills = {}

    def save_skill(self, skill_id: str, code: str) -> bool:
        """Save skill code to file"""
        try:
            skill_file = self.skills_dir / f"{skill_id}.py"
            with open(skill_file, 'w') as f:
                f.write(code)
            return True
        except Exception as e:
            print(f"Error saving skill {skill_id}: {e}")
            return False

    def load_skill(self, skill_id: str) -> Any:
        """Load skill from file"""
        try:
            skill_file = self.skills_dir / f"{skill_id}.py"
            if not skill_file.exists():
                return None

            spec = importlib.util.spec_from_file_location(skill_id, skill_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[skill_id] = module
            spec.loader.exec_module(module)

            self.loaded_skills[skill_id] = module
            return module

        except Exception as e:
            print(f"Error loading skill {skill_id}: {e}")
            return None

    def unload_skill(self, skill_id: str) -> bool:
        """Unload skill from memory"""
        try:
            if skill_id in self.loaded_skills:
                del self.loaded_skills[skill_id]
            if skill_id in sys.modules:
                del sys.modules[skill_id]
            return True
        except Exception as e:
            print(f"Error unloading skill {skill_id}: {e}")
            return False

    def execute_skill(self, skill_id: str, function_name: str = "execute",
                     *args, **kwargs) -> Any:
        """Execute function from loaded skill"""
        try:
            module = self.loaded_skills.get(skill_id)
            if not module:
                module = self.load_skill(skill_id)

            if not module:
                return {"error": f"Skill {skill_id} not found"}

            if not hasattr(module, function_name):
                return {"error": f"Function {function_name} not found in {skill_id}"}

            func = getattr(module, function_name)
            result = func(*args, **kwargs)
            return result

        except Exception as e:
            return {"error": str(e)}

    def list_installed_skills(self) -> list:
        """List all installed skill files"""
        try:
            skills = []
            for skill_file in self.skills_dir.glob("*.py"):
                if skill_file.name != "__init__.py":
                    skill_id = skill_file.stem
                    skills.append({
                        "skill_id": skill_id,
                        "file": str(skill_file),
                        "loaded": skill_id in self.loaded_skills
                    })
            return skills
        except Exception as e:
            print(f"Error listing skills: {e}")
            return []

    def get_skill_info(self, skill_id: str) -> dict:
        """Get metadata about skill"""
        try:
            skill_file = self.skills_dir / f"{skill_id}.py"
            if not skill_file.exists():
                return {"error": "Skill not found"}

            module = self.loaded_skills.get(skill_id)
            if not module:
                module = self.load_skill(skill_id)

            functions = []
            if module:
                for name in dir(module):
                    if not name.startswith('_'):
                        obj = getattr(module, name)
                        if callable(obj):
                            functions.append(name)

            return {
                "skill_id": skill_id,
                "file": str(skill_file),
                "file_size": skill_file.stat().st_size,
                "functions": functions,
                "loaded": skill_id in self.loaded_skills
            }

        except Exception as e:
            return {"error": str(e)}

    def validate_skill_file(self, skill_file_path: str) -> tuple[bool, str]:
        """Validate Python code in skill file"""
        try:
            with open(skill_file_path, 'r') as f:
                code = f.read()

            compile(code, skill_file_path, 'exec')
            return True, "Valid Python code"

        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, str(e)

    def rollback_skill(self, skill_id: str, backup_file: str = None) -> bool:
        """Rollback skill to previous version"""
        try:
            skill_file = self.skills_dir / f"{skill_id}.py"

            if backup_file and Path(backup_file).exists():
                # Restore from backup
                with open(backup_file, 'r') as f:
                    backup_code = f.read()
                with open(skill_file, 'w') as f:
                    f.write(backup_code)
                self.unload_skill(skill_id)
                return True
            else:
                # Just unload
                return self.unload_skill(skill_id)

        except Exception as e:
            print(f"Error rolling back skill {skill_id}: {e}")
            return False

    def backup_skill(self, skill_id: str) -> bool:
        """Create backup of skill before updating"""
        try:
            skill_file = self.skills_dir / f"{skill_id}.py"
            backup_file = self.skills_dir / f"{skill_id}.py.backup"

            if skill_file.exists():
                with open(skill_file, 'r') as f:
                    code = f.read()
                with open(backup_file, 'w') as f:
                    f.write(code)
                return True
            return False

        except Exception as e:
            print(f"Error backing up skill {skill_id}: {e}")
            return False
