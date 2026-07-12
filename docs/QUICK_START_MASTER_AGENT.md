# ⚡ QUICK START — Master Agent System

**Complete in 10 minutes**

---

## 🎯 What You're Getting

```
✅ Autonomous agents on VPS that self-heal
✅ Claude AI generates fixes automatically
✅ Works 24/7 even if your Mac is offline
✅ Constantly learns and improves
✅ Zero manual intervention needed
```

---

## 📋 STEP 1: Start Master Agent (on your Mac) — 2 min

```bash
# Terminal on your Mac

# Install dependencies
pip install -r requirements_agents.txt

# Run Master Agent
python master_agent/server.py
```

**Keep this terminal open.** Master Agent will listen on `http://127.0.0.1:8888`

---

## 📋 STEP 2: Deploy to VPS — 3 min

```bash
# Terminal 2 (still on your Mac)

git add -A
git commit -m "Add Master Agent system - full autonomous infrastructure"
git push origin main
```

---

## 📋 STEP 3: SSH to VPS and Update Code — 2 min

```bash
# SSH to VPS
ssh unitplast@193.104.33.29

# Update code
cd /var/www/unitplast_bot
git pull origin main

# Install dependencies
pip install -r requirements_agents.txt
```

---

## 📋 STEP 4: Start VPS Agents — 2 min

```bash
# Still on VPS

# Create directories
mkdir -p logs data
mkdir -p agents/skills

# Start agents in background
nohup python -m agents.health_monitor > logs/health_monitor.log 2>&1 &
nohup python -m agents.agent_status > logs/agent_status.log 2>&1 &
nohup python -m agents.log_analyzer > logs/log_analyzer.log 2>&1 &
nohup python agents/vps_api_server.py > logs/vps_api.log 2>&1 &

# Verify all running
ps aux | grep "agents\|vps_api"
```

---

## 📋 STEP 5: Test Connection — 1 min

```bash
# Back on your Mac

# Test 1: Master Agent is listening
curl http://127.0.0.1:8888/health

# Test 2: VPS agents are responding
curl http://193.104.33.29:9000/health
```

**Both should return `200 OK`**

---

## ✨ DONE! 🎉

Agents are now running autonomously:

```
Health Monitor    ✅ Checking every 60 seconds
Agent Status      ✅ Collecting every 5 minutes
Log Analyzer      ✅ Analyzing every 10 minutes
Master Agent      ✅ Ready to generate skills

Next: Wait for first anomaly, watch skill generation happen automatically
```

---

## 📊 Monitor What's Happening

### View health checks in real-time (on VPS)
```bash
tail -f /var/www/unitplast_bot/logs/health_monitor.log
```

### View generated skills (on Mac)
```bash
curl -H "Authorization: Bearer unitplast_master_key_2026" \
  http://127.0.0.1:8888/api/skills
```

### View what skills are installed on VPS
```bash
curl http://193.104.33.29:9000/api/skills
```

### Watch for anomalies being detected
```bash
tail -f /var/www/unitplast_bot/logs/log_analyzer.log
```

---

## 🎯 What Happens Next

### If no errors detected:
```
✅ Baseline patterns build
✅ System learning starts
✅ Agents monitor normally
→ No skills needed yet
```

### If error detected (e.g., timeout):
```
1. Agent logs: "Health endpoint timeout"
2. Agent requests: "healing_timeout_skill"
3. Master generates: Python code to fix
4. VPS receives: Skill installation
5. VPS installs: Code loaded and executed
6. Issue fixed: Service recovers
7. Agent reports: Success logged
→ Problem solved without you doing anything
```

---

## 🔑 Important Notes

```
⏱️  Master Agent must be running on Mac for skill generation
   (agents continue working independently even if Master goes down)

💾 Skills saved in: data/skills/ and data/skills.json

📊 Metrics tracked in: data/log_analysis.json (on VPS)

🔐 Auth token: unitplast_master_key_2026 (in environment)

🛑 To stop agents:
   killall python3
   
   or individually:
   pkill -f health_monitor
   pkill -f agent_status
   pkill -f log_analyzer
```

---

## 📚 For More Details

Read full documentation:
- `docs/MASTER_AGENT_SYSTEM.md` — Complete system architecture
- `docs/DEPLOY_AGENTS_VPS_INSTRUCTIONS.md` — Detailed VPS setup
- `master_agent/server.py` — API endpoints reference

---

**Status:** ✅ READY TO RUN  
**Time to autonomy:** < 10 minutes  
**Mac required:** While generating skills  
**VPS required:** Always (for production agents)
