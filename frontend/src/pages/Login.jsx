import { useState } from "react";
import { api } from "../services/api";

export default function Login({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [f, setF] = useState({ username:"", email:"", password:"", phone:"", pan_number:"", risk_profile:"MODERATE" });
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const set = k => e => setF(p => ({ ...p, [k]: e.target.value }));

  const submit = async () => {
    setErr(""); setLoading(true);
    try {
      const data = mode === "login" ? await api.login(f.username, f.password) : await api.register(f);
      localStorage.setItem("token", data.access_token); const me = await api.me();
      onLogin(me, data.access_token);
    } catch(e) { setErr(e.message); }
    finally { setLoading(false); }
  };

  const inp = { width:"100%", padding:"10px 12px", background:"#1f2937", border:"1px solid #374151", borderRadius:8, color:"#f9fafb", fontSize:13, outline:"none", boxSizing:"border-box", marginBottom:14 };
  const btn = { width:"100%", padding:12, background:"linear-gradient(135deg,#6366f1,#8b5cf6)", border:"none", borderRadius:8, color:"#fff", fontWeight:600, fontSize:14, cursor:"pointer", marginTop:4 };

  return (
    <div style={{minHeight:"100vh",background:"#0a0d14",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:"system-ui"}}>
      <div style={{background:"#111827",border:"1px solid #1f2937",borderRadius:16,padding:36,width:360,boxShadow:"0 25px 60px rgba(0,0,0,.6)"}}>
        <div style={{fontSize:32,marginBottom:8}}>ðŸ“ˆ</div>
        <div style={{fontSize:22,fontWeight:600,color:"#f9fafb",marginBottom:4}}>Dalal Street Pro</div>
        <div style={{fontSize:13,color:"#6b7280",marginBottom:24}}>NSE Â· BSE Â· MCX Â· Mutual Funds Â· IPO</div>
        <div style={{fontSize:12,color:"#9ca3af",marginBottom:5}}>USERNAME</div>
        <input style={inp} value={f.username} onChange={set("username")} placeholder="arjun_kapoor" />
        {mode === "register" && <>
          <div style={{fontSize:12,color:"#9ca3af",marginBottom:5}}>EMAIL</div>
          <input style={inp} value={f.email} onChange={set("email")} placeholder="you@example.com" />
          <div style={{fontSize:12,color:"#9ca3af",marginBottom:5}}>PHONE</div>
          <input style={inp} value={f.phone} onChange={set("phone")} placeholder="9876543210" />
          <div style={{fontSize:12,color:"#9ca3af",marginBottom:5}}>PAN NUMBER (optional)</div>
          <input style={inp} value={f.pan_number} onChange={set("pan_number")} placeholder="ABCDE1234F" />
          <div style={{fontSize:12,color:"#9ca3af",marginBottom:5}}>RISK PROFILE</div>
          <select style={{...inp,appearance:"none"}} value={f.risk_profile} onChange={set("risk_profile")}>
            <option>CONSERVATIVE</option><option>MODERATE</option><option>AGGRESSIVE</option>
          </select>
        </>}
        <div style={{fontSize:12,color:"#9ca3af",marginBottom:5}}>PASSWORD</div>
        <input style={inp} type="password" value={f.password} onChange={set("password")} placeholder="â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢" />
        {err && <div style={{color:"#f87171",fontSize:12,marginBottom:10}}>{err}</div>}
        <button style={btn} onClick={submit} disabled={loading}>{loading ? "Please wait..." : mode === "login" ? "Login to Portfolio" : "Create Account"}</button>
        <div style={{textAlign:"center",marginTop:12,fontSize:12,color:"#6b7280"}}>
          {mode === "login" ? "New user? " : "Have account? "}
          <button style={{color:"#6366f1",background:"none",border:"none",cursor:"pointer",fontSize:12}} onClick={() => setMode(m => m==="login"?"register":"login")}>
            {mode === "login" ? "Register free" : "Sign in"}
          </button>
        </div>
        <div style={{display:"flex",gap:6,marginTop:14,flexWrap:"wrap"}}>
          {["SEBI Compliant","NSE/BSE","JWT Secured","SIP Tracker","IPO Tracker"].map(t => (
            <span key={t} style={{fontSize:10,padding:"2px 8px",borderRadius:99,background:"#1f2937",color:"#6b7280"}}>{t}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
