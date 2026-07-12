# 🚀 MASTER AGENT SYSTEM — Full Autonomous Infrastructure

**Status:** ✅ READY FOR DEPLOYMENT  
**Date:** 2026-07-12  
**Version:** 1.0.0

---

## 📋 SYSTEM OVERVIEW

**Two-Part Architecture:**

```
┌─────────────────────────────────┐
│   MAC / LAPTOP (Your Machine)   │
│                                 │
│  Master Agent Server (Port 8888)│
│  ├─ API Endpoints               │
│  ├─ Skill Manager               │
│  ├─ Skill Generator (Claude API)│
│  └─ Safety Validator            │
└────────────┬────────────────────┘
             │ HTTP API
             │ Port 8888
             ↓
┌─────────────────────────────────┐
│   VPS PRODUCTION (193.104.33.29)│
│                                 │
│  Three Autonomous Agents:       │
│  1. Health Monitor (every 60s)  │
│  2. Agent Status (every 5min)   │
│  3. Log Analyzer (every 10min)  │
│                                 │
│  VPS API Server (Port 9000)     │
│  ├─ Receives skills             │
│  ├─ Installs skills             │
│  └─ Executes skills             │
└─────────────────────────────────┘
```

---

## 🎯 HOW IT WORKS

### Step 1: Agent Detects Problem
```
VPS Agent (Health Monitor)
  ↓
  Detects: Connection timeout to /health endpoint
  ↓
  Logs: Event with timestamp and error details
```

### Step 2: Agent Requests Skill
```
VPS Agent sends:
  POST http://127.0.0.1:8888/api/request_skill
  {
    "agent_id": "health_monitor",
    "issue": "Health endpoint responding slow",
    "skill_type": "healing",
    "error_log": "Connection timeout after 5 seconds"
  }
```

### Step 3: Master Analyzes & Generates
```
Master Agent on Mac:
  1. Checks skill registry (data/skills.json)
  2. If not found: Calls Claude API
  3. Claude generates Python code for fix
  4. Validates code (no dangerous imports)
  5. Saves skill to data/skills/
  6. Registers skill in registry
```

### Step 4: Master Sends Skill
```
Master responds:
  {
    "status": "generated",
    "skill": {
      "skill_id": "heal_health_timeout_001",
      "type": "python_function",
      "code": "def execute()...",
      "dependencies": [],
      "auto_activate": true
    }
  }
```

### Step 5: VPS Agent Installs & Executes
```
VPS Agent:
  1. Receives skill
  2. Saves to agents/skills/heal_health_timeout_001.py
  3. Loads skill module
  4. Executes the fix
  5. Reports success/failure to Master
```

### Step 6: VPS Continues Autonomously
```
Agent recovers from error and continues monitoring
  ↓
If problem persists: Request next skill
  ↓
If solved: Add skill to permanent capability set
  ↓
Mac can go offline → VPS continues 24/7
```

---

## 🚀 SETUP & ACTIVATION

### Part 1: Start Master Agent (on your Mac)

```bash
# Install dependencies
pip install -r requirements_agents.txt

# Set environment variables (optional, defaults included)
export MASTER_AGENT_HOST=127.0.0.1
export MASTER_AGENT_PORT=8888
export MASTER_AGENT_TOKEN=unitplast_master_key_2026
export ANTHROPIC_API_KEY=your_key_here

# Start Master Agent Server
python master_agent/server.py
```

**Expected output:**
```
🚀 Master Agent Server starting on 127.0.0.1:8888
Auth Token: unitplast_...
Skill registry: data/skills.json
```

### Part 2: Deploy Code to VPS

```bash
# On your machine, push latest changes
git add -A
git commit -m "Add master agent system and autonomous agent framework"
git push origin main
```

### Part 3: Update VPS Code

```bash
# SSH into VPS
ssh unitplast@193.104.33.29

# Pull latest code
cd /var/www/unitplast_bot
git pull origin main

# Install/update dependencies
pip install -r requirements_agents.txt
```

### Part 4: Start VPS Agents

```bash
# On VPS, start each agent in background

# 1. Health Monitor
python -m agents.health_monitor &

# 2. Agent Status
python -m agents.agent_status &

# 3. Log Analyzer
python -m agents.log_analyzer &

# 4. VPS API Server
python agents/vps_api_server.py &

# Check all running
ps aux | grep "agents"
```

### Part 5: Verify Connection

```bash
# Test Master Agent health
curl http://127.0.0.1:8888/health

# Test VPS API health
curl http://193.104.33.29:9000/health
```

---

## 📊 WHAT EACH AGENT DOES

### Health Monitor
```
Every 60 seconds:
  ✅ Checks http://127.0.0.1:5000/health
  ✅ Records response time
  ✅ Logs successful/failed checks
  
When problem detected (3 consecutive failures):
  🔧 Requests healing skill from Master
  🔧 Installs skill
  🔧 Attempts auto-fix
  🔧 Reports result
```

### Agent Status
```
Every 5 minutes:
  ✅ Checks systemd service statuses
  ✅ Verifies all agents running
  ✅ Records enabled/disabled states
  
When service down (2 consecutive failures):
  🔧 Requests remediation skill
  🔧 Attempts automatic restart
  🔧 Installs healing skill if needed
  🔧 Reports recovery
```

### Log Analyzer
```
Every 10 minutes:
  ✅ Analyzes health monitor logs
  ✅ Detects anomalies vs baseline
  ✅ Makes predictions about failures
  ✅ Calculates performance trends
  
When anomaly detected:
  🔧 Requests optimization skill
  🔧 Installs performance improvement
  🔧 Monitors impact
  🔧 Learns and adapts
```

---

## 🧠 SKILL TYPES

### 1. Healing Skills
```
Purpose: Fix specific problems
Example: "Health endpoint responding slow"
Generated: Claude creates code to optimize response
Executed: When problem detected
Result: Service recovers automatically
```

### 2. Optimization Skills
```
Purpose: Improve performance metrics
Example: "Reduce response time 50%→30ms"
Generated: Claude creates optimization code
Executed: When trends show degradation
Result: Performance improves, logged for analysis
```

### 3. Detection Skills
```
Purpose: Identify new issue types
Example: "Detect memory leaks"
Generated: Claude creates detection logic
Executed: Continuously monitoring
Result: Early warning before system failure
```

### 4. Scaling Skills
```
Purpose: Handle increased load
Example: "Scale to handle 10x traffic"
Generated: Claude creates scaling recommendations
Executed: When load metrics spike
Result: System capacity increases
```

---

## 🔒 SAFETY GUARANTEES

```
✅ Code Validation
   - Only Claude-generated code accepted
   - AST parsing for dangerous operations
   - No subprocess, eval, exec, or dangerous imports

✅ Sandboxing
   - Skills tested before activation
   - Rollback available if skill fails
   - No system-wide permissions

✅ Rate Limiting
   - Max 1 skill request per 5 minutes per agent
   - Max skill execution timeout: 30 seconds
   - Failed attempts logged

✅ Audit Trail
   - All skill requests logged
   - Installation reports saved
   - Success/failure metrics tracked

✅ Human Override
   - Can disable agents anytime
   - Can manually review generated skills
   - Can rollback any installation
```

---

## 📈 EXPECTED TIMELINE

### Day 1
```
✅ Agents start running
✅ Health baseline established
✅ First skill generated (if problem found)
✅ 1,440 health checks collected
```

### Week 1
```
✅ 5-7 skills generated and installed
✅ Baseline patterns established
✅ Anomaly detection active
✅ First auto-fixes executed
✅ Performance trending calculated
```

### Month 1
```
✅ 20+ skills installed
✅ Fully autonomous operation
✅ Predictive maintenance working
✅ Self-healing active
✅ Mac can be offline 24/7
✅ VPS self-manages completely
```

---

## 🔄 UPDATING MASTER AGENT

If you want to add new functionality to Master Agent:

```bash
# Edit master_agent files locally
nano master_agent/skill_generator.py

# Test locally
python master_agent/server.py

# Restart server when ready
# (Agents will keep working during restart)

# No VPS restart needed
```

---

## 🐛 TROUBLESHOOTING

### Master Agent won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r requirements_agents.txt

# Check port not in use
lsof -i :8888

# Check API key
echo $ANTHROPIC_API_KEY
```

### VPS Agents not connecting
```bash
# Check network connection
ping 127.0.0.1:8888  # From VPS

# Check environment variables
echo $MASTER_URL
echo $MASTER_TOKEN

# Check logs
tail -f /var/www/unitplast_bot/logs/health_monitor.log
```

### Skill installation failed
```bash
# Check VPS API running
curl http://127.0.0.1:9000/health

# Check skill file
ls -la /var/www/unitplast_bot/agents/skills/

# Check installation reports
cat data/skill_installation_reports.jsonl
```

---

## 📞 MONITORING

### View Generated Skills
```bash
curl -H "Authorization: Bearer unitplast_master_key_2026" \
  http://127.0.0.1:8888/api/skills
```

### View Agent Capabilities
```bash
curl -H "Authorization: Bearer unitplast_master_key_2026" \
  http://127.0.0.1:8888/api/agent/health_monitor/capabilities
```

### View Recent Installation Reports
```bash
tail -50 data/skill_installation_reports.jsonl
```

### Check VPS Agent Status
```bash
curl http://193.104.33.29:9000/api/agent/status
```

---

## ✨ ADVANCED USAGE

### Custom Skill Generation
```python
from master_agent.skill_generator import SkillGenerator

generator = SkillGenerator()
skill = generator.generate_python_skill(
    skill_id="custom_skill_001",
    requirement="Monitor disk space and alert if >90%",
    context={"threshold": 0.9}
)
```

### Manual Skill Registration
```python
from master_agent.skill_manager import SkillManager

manager = SkillManager()
skill = manager.create_python_skill(
    skill_id="manual_skill",
    code="def execute(): return {'status': 'ok'}",
    dependencies=[]
)
```

### Skill Metrics
```bash
# Count generated skills
jq '.skills | length' data/skills.json

# View skill distribution by category
jq '.skills | group_by(.category) | map({key: .[0].category, count: length})' data/skills.json

# See installation success rate
jq -s 'group_by(.status) | map({status: .[0].status, count: length})' data/skill_installation_reports.jsonl
```

---

## 🎯 NEXT STEPS

1. **Start Master Agent** on your Mac
2. **Deploy code** to VPS
3. **Start VPS agents** (health_monitor, agent_status, log_analyzer)
4. **Monitor first 24 hours** for initial skill generation
5. **Review generated skills** to ensure quality
6. **Let it run** — agents will become increasingly autonomous

---

**Status:** ✅ COMPLETE AND READY  
**Autonomy Level:** 🤖 FULL (24/7 self-healing)  
**Mac Requirement:** ⏱️ Master Agent running (can be anywhere)  
**VPS Requirement:** 🖥️ All agents + VPS API server running
