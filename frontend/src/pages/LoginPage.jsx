import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";
import toast from "react-hot-toast";

export default function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate("/dashboard");
      toast.success("Welcome back!");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const s = { background:"#161b22",border:"1px solid #30363d",borderRadius:"8px",color:"#e6edf3",padding:"8px 12px",width:"100%",fontSize:"14px",marginTop:"6px",boxSizing:"border-box" };

  return (
    <div style={{minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center",background:"#0f1117"}}>
      <div style={{background:"#161b22",border:"1px solid #30363d",borderRadius:"12px",padding:"40px",width:"100%",maxWidth:"400px"}}>
        <div style={{fontSize:"24px",fontWeight:"700",color:"#58a6ff",marginBottom:"8px"}}>⚡ DocGen AI</div>
        <h2 style={{color:"#e6edf3",marginBottom:"24px",fontSize:"18px"}}>Sign in to your account</h2>
        <form onSubmit={handleSubmit}>
          <div style={{marginBottom:"16px"}}>
            <label style={{color:"#8b949e",fontSize:"13px"}}>Email</label>
            <input style={s} type="email" value={form.email} onChange={(e)=>setForm({...form,email:e.target.value})} placeholder="you@example.com" required />
          </div>
          <div style={{marginBottom:"24px"}}>
            <label style={{color:"#8b949e",fontSize:"13px"}}>Password</label>
            <input style={s} type="password" value={form.password} onChange={(e)=>setForm({...form,password:e.target.value})} placeholder="••••••••" required />
          </div>
          <button type="submit" disabled={loading} style={{background:"#58a6ff",color:"#000",border:"none",borderRadius:"6px",padding:"10px",width:"100%",fontSize:"15px",fontWeight:"600",cursor:"pointer"}}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
        <p style={{marginTop:"20px",textAlign:"center",color:"#8b949e",fontSize:"13px"}}>
          Don't have an account? <Link to="/register" style={{color:"#58a6ff"}}>Sign up</Link>
        </p>
      </div>
    </div>
  );
}
