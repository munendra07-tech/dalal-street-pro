import { useState, useEffect } from "react";
import { api } from "./services/api";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) api.me().then(setUser).catch(() => localStorage.removeItem("token")).finally(() => setLoading(false));
    else setLoading(false);
  }, []);
  if (loading) return <div style={{display:"flex",alignItems:"center",justifyContent:"center",height:"100vh",background:"#0a0d14",color:"#fff"}}>Loading...</div>;
  return user
    ? <Dashboard user={user} onLogout={() => { localStorage.removeItem("token"); setUser(null); }} />
    : <Login onLogin={(u, t) => { localStorage.setItem("token", t); setUser(u); }} />;
}