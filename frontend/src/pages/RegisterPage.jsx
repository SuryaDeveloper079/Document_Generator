import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";
import toast from "react-hot-toast";

export default function RegisterPage() {
  const navigate = useNavigate();
  const register = useAuthStore((s) => s.register);
  const [form, setForm] = useState({ email: "", username: "", password: "", full_name: "" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(form);
      toast.success("Account created! Please sign in.");
      navigate("/login");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const s = { background:"#161b22",border:"1px solid #30363d",borderRadius:"8px",color:"#e6edf3",padding:"8px 12px",width:"100%",fontSize:"14px",marginTop:"6px",boxSizing:"border-box" };

  return (
    <div style={{minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center",background:"#0f1117"}}>
      <div style={{background:"#161b22",border:"1px solid #30363d",borderRadius:"12px",padding:"40px",width:"100%",maxWidth:"400px"}}>
        <div style={{fontSize:"24px",fontWeight:"700",color:"#58a6ff",marginBottom:"8px"}}>⚡ DocGen AI</div>
        <h2 style={{color:"#e6edf3",marginBottom:"24px",fontSize:"18px"}}>Create an account</h2>
        <form onSubmit={handleSubmit}>
          {[["Full Name (optional)","full_name","text","Jane Doe"],["Email","email","email","you@example.com"],["Username","username","text","janedoe"],["Password (min 8, 1 uppercase, 1 digit)","password","password","••••••••"]].map(([label,key,type,ph])=>(
            <div key={key} style={{marginBottom:"16px"}}>
              <label style={{color:"#8b949e",fontSize:"13px"}}>{label}</label>
              <input style={s} type={type} value={form[key]} onChange={(e)=>setForm({...form,[key]:e.target.value})} placeholder={ph} required={key!=="full_name"} />
            </div>
          ))}
          <button type="submit" disabled={loading} style={{background:"#58a6ff",color:"#000",border:"none",borderRadius:"6px",padding:"10px",width:"100%",fontSize:"15px",fontWeight:"600",cursor:"pointer"}}>
            {loading ? "Creating..." : "Create Account"}
          </button>
        </form>
        <p style={{marginTop:"20px",textAlign:"center",color:"#8b949e",fontSize:"13px"}}>
          Already have an account? <Link to="/login" style={{color:"#58a6ff"}}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
