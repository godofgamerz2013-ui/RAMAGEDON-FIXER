"""ApexRig-AI desktop dashboard (Windows 10/11)."""
import os,sys,time,threading,tkinter as tk
from tkinter import ttk,messagebox,simpledialog
try: import keyring
except Exception: keyring=None
from engine import scan_processes,ask_gemini,close_pid,hardware_snapshot,log,APP_DIR

class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title("ApexRig-AI | PC Performance"); self.geometry("1050x720"); self.configure(bg="#0b1020")
  self.key=(keyring.get_password("ApexRig-AI","gemini") if keyring else None) or ""; self.active=False; self.last_ai=0; self.last_scan=0; self.rows=[]
  self.style=ttk.Style(self); self.style.theme_use("clam"); self.style.configure("Treeview",background="#131b2e",foreground="#e8eefc",fieldbackground="#131b2e",rowheight=27); self.style.configure("Treeview.Heading",background="#202d49",foreground="white")
  head=tk.Frame(self,bg="#0b1020"); head.pack(fill="x",padx=22,pady=18)
  tk.Label(head,text="APEXRIG",font=("Segoe UI",24,"bold"),fg="white",bg="#0b1020").pack(side="left")
  tk.Label(head,text=" AI",font=("Segoe UI",24,"bold"),fg="#55d6be",bg="#0b1020").pack(side="left")
  self.status=tk.Label(head,text="● PAUSED",fg="#ffbd69",bg="#0b1020"); self.status.pack(side="right")
  tabs=ttk.Notebook(self); tabs.pack(fill="both",expand=True,padx=20,pady=8)
  self.over=tk.Frame(tabs,bg="#0b1020"); self.proc=tk.Frame(tabs,bg="#0b1020"); self.ai=tk.Frame(tabs,bg="#0b1020"); self.hw=tk.Frame(tabs,bg="#0b1020")
  for f,n in [(self.over,"Overview"),(self.proc,"RAM & Processes"),(self.ai,"Gemini AI"),(self.hw,"Hardware")]: tabs.add(f,text=n)
  self.build_over(); self.build_proc(); self.build_ai(); self.build_hw(); self.refresh(); self.after(1000,self.tick)
 def button(self,p,t,fn): return tk.Button(p,text=t,command=fn,bg="#263653",fg="white",activebackground="#55d6be",relief="flat",padx=14,pady=9)
 def build_over(self):
  tk.Label(self.over,text="Your PC, intelligently managed.",bg="#0b1020",fg="white",font=("Segoe UI",18,"bold")).pack(anchor="w",padx=20,pady=20)
  self.metrics=tk.Label(self.over,text="Loading system metrics…",bg="#131b2e",fg="#e8eefc",font=("Segoe UI",16),justify="left",padx=20,pady=20); self.metrics.pack(fill="x",padx=20)
  row=tk.Frame(self.over,bg="#0b1020"); row.pack(anchor="w",padx=20,pady=16)
  self.start=self.button(row,"START SMART MONITORING",self.toggle); self.start.pack(side="left",padx=4)
  self.button(row,"SCAN NOW",self.refresh).pack(side="left",padx=4); self.button(row,"SET GEMINI KEY",self.set_key).pack(side="left",padx=4)
  self.auto=tk.BooleanVar(value=False); tk.Checkbutton(self.over,text="Enable automatic cleanup of validated Gemini suggestions (OFF by default)",variable=self.auto,bg="#0b1020",fg="white",selectcolor="#131b2e").pack(anchor="w",padx=24)
  tk.Label(self.over,text="ACTIVITY LOG",bg="#0b1020",fg="#91a2c4").pack(anchor="w",padx=20,pady=(20,5))
  self.logbox=tk.Text(self.over,bg="#131b2e",fg="#e8eefc",height=12,relief="flat",state="disabled"); self.logbox.pack(fill="both",expand=True,padx=20,pady=10)
 def build_proc(self):
  tk.Label(self.proc,text="Memory consumers",bg="#0b1020",fg="white",font=("Segoe UI",17,"bold")).pack(anchor="w",padx=20,pady=16)
  self.tree=ttk.Treeview(self.proc,columns=("pid","name","ram","cpu","status"),show="headings")
  for c,t,w in [("pid","PID",80),("name","Process",300),("ram","RAM MB",120),("cpu","CPU %",100),("status","Status",150)]: self.tree.heading(c,text=t); self.tree.column(c,width=w)
  self.tree.pack(fill="both",expand=True,padx=20,pady=10)
  row=tk.Frame(self.proc,bg="#0b1020"); row.pack(anchor="w",padx=20,pady=10)
  self.button(row,"REFRESH",self.refresh).pack(side="left",padx=4); self.button(row,"CLOSE SELECTED (CONFIRM)",self.close_selected).pack(side="left",padx=4)
  tk.Label(self.proc,text="Windows, security, driver and ApexRig processes are protected. Save work before closing apps.",bg="#0b1020",fg="#ffbd69").pack(anchor="w",padx=20)
 def build_ai(self):
  tk.Label(self.ai,text="Gemini intelligence",bg="#0b1020",fg="white",font=("Segoe UI",17,"bold")).pack(anchor="w",padx=20,pady=16)
  tk.Label(self.ai,text="Gemini only recommends. Local Python rechecks the exact PID and executable before any close. AI analysis is throttled to 40 minutes.",bg="#0b1020",fg="#91a2c4",wraplength=900).pack(anchor="w",padx=20)
  row=tk.Frame(self.ai,bg="#0b1020"); row.pack(anchor="w",padx=20,pady=12)
  self.button(row,"ANALYSE NOW",self.analyse).pack(side="left",padx=4); self.button(row,"SET API KEY",self.set_key).pack(side="left",padx=4)
  self.recs=tk.Text(self.ai,bg="#131b2e",fg="#e8eefc",relief="flat"); self.recs.pack(fill="both",expand=True,padx=20,pady=10)
 def build_hw(self):
  tk.Label(self.hw,text="Hardware telemetry & tuning",bg="#0b1020",fg="white",font=("Segoe UI",17,"bold")).pack(anchor="w",padx=20,pady=16)
  self.hwtext=tk.Label(self.hw,text="",bg="#131b2e",fg="#e8eefc",font=("Consolas",12),justify="left",anchor="nw",padx=20,pady=20); self.hwtext.pack(fill="x",padx=20)
  tk.Label(self.hw,text="Read-only CPU/GPU telemetry in this release. No voltage, BIOS, power-limit or clock changes are made; use manufacturer-supported tuning utilities and stability tests.",bg="#0b1020",fg="#ffbd69",wraplength=900,justify="left").pack(anchor="w",padx=20,pady=16)
 def say(self,msg):
  line=log(msg); self.logbox.config(state="normal"); self.logbox.insert("end",line+"\n"); self.logbox.see("end"); self.logbox.config(state="disabled")
 def set_key(self):
  k=simpledialog.askstring("Gemini API key","Paste Google Gemini API key:",show="*")
  if k:
   if not keyring: messagebox.showerror("Secure storage unavailable","Install keyring to store the key in Windows Credential Manager."); return
   keyring.set_password("ApexRig-AI","gemini",k); self.key=k; self.say("Gemini key saved to OS credential manager.")
 def toggle(self):
  self.active=not self.active; self.start.config(text="PAUSE MONITORING" if self.active else "START SMART MONITORING"); self.status.config(text="● ACTIVE" if self.active else "● PAUSED",fg="#55d6be" if self.active else "#ffbd69"); self.say("Monitoring "+("started" if self.active else "paused"))
  if self.active: self.last_ai=time.time(); self.last_scan=time.time()
 def refresh(self):
  self.rows=scan_processes()
  for x in self.tree.get_children(): self.tree.delete(x)
  for p in self.rows: self.tree.insert("","end",values=(p["pid"],p["name"],p["ram_mb"],p["cpu_pct"],p["status"]))
  h=hardware_snapshot(); self.metrics.config(text=f"RAM  {h['ram_used_gb']} / {h['ram_total_gb']} GB  ({h['ram_percent']}%)\nCPU  {h['cpu_percent']}%    Clock {h['cpu_mhz'] or 'N/A'} MHz\nGPU  {h['gpu']}\nCandidates  {len(self.rows)}")
  self.hwtext.config(text=f"CPU utilization: {h['cpu_percent']}%\nCPU clock: {h['cpu_mhz'] or 'N/A'} MHz\nRAM: {h['ram_used_gb']} / {h['ram_total_gb']} GB ({h['ram_percent']}%)\nGPU: {h['gpu']}\n\nTelemetry only — no overclock changes applied.")
  self.last_scan=time.time()
 def close_selected(self):
  s=self.tree.selection()
  if not s: return
  pid,name,*_=self.tree.item(s[0],"values")
  if messagebox.askyesno("Confirm",f"Close {name} (PID {pid})? Save work first."):
   ok,msg=close_pid(int(pid),name); self.say(msg); messagebox.showinfo("ApexRig-AI",msg); self.refresh()
 def analyse(self):
  if not self.key: self.set_key()
  if not self.key: return
  self.last_ai=time.time(); self.say("Gemini analysis started…")
  def work():
   try:
    rows=scan_processes(); result=ask_gemini(rows,self.key)
    self.after(0,lambda:self.show_results(rows,result))
   except Exception as e: self.after(0,lambda:self.say("Gemini error: "+str(e)))
  threading.Thread(target=work,daemon=True).start()
 def show_results(self,rows,result):
  names={p["pid"]:p["name"] for p in rows}; self.recs.delete("1.0","end")
  for r in result: self.recs.insert("end",f"PID {r['pid']}  {names.get(r['pid'],'?')}\n{r.get('reason','')}\n\n")
  if not result: self.recs.insert("end","No safe cleanup suggestions.")
  self.say(f"Gemini returned {len(result)} recommendation(s).")
  if self.auto.get():
   for r in result:
    name=names.get(r["pid"])
    if name:
     ok,msg=close_pid(r["pid"],name); self.say(msg)
 def tick(self):
  if self.active:
   now=time.time()
   if now-self.last_scan>=1200: self.refresh(); self.say("20-minute process scan completed.")
   if self.key and now-self.last_ai>=2400: self.analyse()
  self.after(1000,self.tick)

if __name__=="__main__":
 app=App(); app.mainloop()
