"""ApexRig-AI process engine. Gemini advises; local safety checks decide."""
import json, os, urllib.request, psutil
from pathlib import Path
from datetime import datetime

APP_DIR=Path(os.getenv("LOCALAPPDATA",str(Path.home())))/"ApexRigAI"
APP_DIR.mkdir(parents=True,exist_ok=True)
LOG_FILE=APP_DIR/"apexrig.log"
PROTECTED={"system","system idle process","registry","secure system","memory compression","smss.exe","csrss.exe","wininit.exe","services.exe","lsass.exe","svchost.exe","winlogon.exe","explorer.exe","dwm.exe","fontdrvhost.exe","audiodg.exe","spoolsv.exe","taskhostw.exe","sihost.exe","ctfmon.exe","searchhost.exe","securityhealthservice.exe","msmpeng.exe","mpdefendercoreprocess.exe","smartscreen.exe","nvcontainer.exe","nvdisplay.container.exe","armourycrate.exe","asusappservice.exe","asusoptimization.exe","ghelper.exe","rtkauduservice64.exe","intelaudioservice.exe","python.exe","pythonw.exe","cmd.exe","powershell.exe","conhost.exe"}

def log(message):
    line=f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}"
    with LOG_FILE.open("a",encoding="utf-8") as f: f.write(line+"\n")
    return line

def scan_processes(min_mb=35):
    rows=[]
    for p in psutil.process_iter(["pid","name","memory_info","cpu_percent","username","status"]):
        try:
            i=p.info; name=i.get("name") or "Unknown"
            if name.lower() in PROTECTED: continue
            mem=i.get("memory_info"); mb=mem.rss/1048576 if mem else 0
            if mb>=min_mb: rows.append({"pid":i["pid"],"name":name,"ram_mb":round(mb,1),"cpu_pct":round(i.get("cpu_percent") or 0,1),"status":i.get("status") or ""})
        except (psutil.NoSuchProcess,psutil.AccessDenied,psutil.ZombieProcess): pass
    return sorted(rows,key=lambda x:x["ram_mb"],reverse=True)

def ask_gemini(processes,api_key,model=None):
    if not api_key:
        raise ValueError("Gemini API key missing")
    snapshot=processes[:80]
    prompt=("You are a cautious Windows performance advisor. Recommend only clearly idle, nonessential user apps. "
      "Never recommend Windows components, security software, drivers, audio/input, active games, sync/backup, "
      "remote access, accessibility or unknown processes. RAM use alone does not prove idleness. "
      "Return JSON {\"recommendations\":[{\"pid\":123,\"reason\":\"...\"}]}; only use PIDs in snapshot.\n"+
      json.dumps(snapshot))
    body={"contents":[{"parts":[{"text":prompt}]}],
          "generationConfig":{"responseMimeType":"application/json","temperature":0.1}}

    def generate(model_name):
        url=f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req=urllib.request.Request(url,data=json.dumps(body).encode(),
                                   headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=45) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            detail=exc.read().decode("utf-8","replace")[:1200]
            raise RuntimeError(f"Gemini API HTTP {exc.code} for {model_name}: {detail}") from exc

    # Model availability differs by Google AI Studio project and API lifecycle.
    # Discover models supported by this key instead of assuming a hard-coded model ID.
    if model:
        data=generate(model)
    else:
        list_url=f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        try:
            with urllib.request.urlopen(list_url,timeout=20) as response:
                catalog=json.loads(response.read())
        except urllib.error.HTTPError as exc:
            detail=exc.read().decode("utf-8","replace")[:1200]
            raise RuntimeError(f"Gemini model discovery failed (HTTP {exc.code}): {detail}") from exc
        candidates=[]
        for entry in catalog.get("models",[]):
            methods=entry.get("supportedGenerationMethods",[])
            name=entry.get("name","")
            if "generateContent" in methods and name.startswith("models/"):
                short=name.split("/",1)[1]
                if "gemini" in short.lower():
                    candidates.append(short)
        if not candidates:
            raise RuntimeError("This Gemini API key has no models supporting generateContent. Check the Google AI Studio project, API access and key restrictions.")
        # Prefer Flash for speed and cost; fall back to another available Gemini model.
        candidates.sort(key=lambda name: (
            0 if "flash" in name.lower() else 1,
            0 if "latest" in name.lower() else 1,
            name
        ))
        last_error=None
        data=None
        for candidate in candidates:
            try:
                data=generate(candidate)
                break
            except RuntimeError as exc:
                last_error=exc
                if "HTTP 404" not in str(exc):
                    raise
        if data is None:
            raise last_error or RuntimeError("No listed Gemini model could generate content.")

    try:
        result=json.loads(data["candidates"][0]["content"]["parts"][0]["text"])
    except (KeyError,IndexError,TypeError,ValueError) as exc:
        raise RuntimeError(f"Gemini returned an unexpected response: {json.dumps(data)[:1200]}") from exc
    valid={p["pid"] for p in processes}
    return [x for x in result.get("recommendations",[])
            if isinstance(x.get("pid"),int) and x["pid"] in valid]

def close_pid(pid,name,force=False):
    try:
        p=psutil.Process(int(pid))
        if p.name().lower()!=name.lower(): return False,"PID identity changed; skipped."
        if name.lower() in PROTECTED or p.pid==os.getpid(): return False,"Protected process; skipped."
        p.terminate()
        try: p.wait(5); return True,f"Closed {name} (PID {pid}) gracefully."
        except psutil.TimeoutExpired:
            if not force: return False,"Graceful close timed out; force termination disabled."
            p.kill(); p.wait(3); return True,f"Force-closed {name} (PID {pid})."
    except psutil.NoSuchProcess: return True,"Already exited."
    except psutil.Error as e: return False,f"Could not close: {e}"

def hardware_snapshot():
    v=psutil.virtual_memory(); f=psutil.cpu_freq()
    d={"ram_used_gb":round((v.total-v.available)/1073741824,1),"ram_total_gb":round(v.total/1073741824,1),"ram_percent":v.percent,"cpu_percent":psutil.cpu_percent(.2),"cpu_mhz":round(f.current) if f else None,"gpu":"Not detected"}
    try:
        import subprocess
        out=subprocess.check_output(["nvidia-smi","--query-gpu=name,temperature.gpu,utilization.gpu,clocks.gr","--format=csv,noheader"],text=True,timeout=3,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        d["gpu"]=out.strip().splitlines()[0]
    except Exception: pass
    return d
