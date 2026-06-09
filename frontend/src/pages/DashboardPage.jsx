import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { projectsApi } from "../api/client";
import toast from "react-hot-toast";

export default function DashboardPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", language: "python", visibility: "private" });

  const { data: projects = [], isLoading } = useQuery({ queryKey: ["projects"], queryFn: () => projectsApi.list().then((r) => r.data) });

  const createMutation = useMutation({
    mutationFn: (data) => projectsApi.create(data),
    onSuccess: (res) => { qc.invalidateQueries(["projects"]); toast.success("Project created!"); setShowForm(false); navigate(`/projects/${res.data.id}`); },
    onError: (e) => toast.error(e.response?.data?.detail || "Failed"),
  });

  const inp = { background:"#21262d",border:"1px solid #30363d",borderRadius:"6px",color:"#e6edf3",padding:"8px 12px",width:"100%",fontSize:"14px",boxSizing:"border-box" };

  return (
    <div>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"24px"}}>
        <h1 style={{fontSize:"24px",color:"#e6edf3"}}>My Projects</h1>
        <button onClick={()=>setShowForm(true)} style={{background:"#58a6ff",color:"#000",border:"none",borderRadius:"6px",padding:"8px 16px",cursor:"pointer",fontWeight:"600"}}>+ New Project</button>
      </div>

      {showForm && (
        <div style={{position:"fixed",inset:0,background:"rgba(0,0,0,0.7)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:100}} onClick={()=>setShowForm(false)}>
          <div style={{background:"#161b22",border:"1px solid #30363d",borderRadius:"12px",padding:"32px",width:"100%",maxWidth:"480px"}} onClick={(e)=>e.stopPropagation()}>
            <h2 style={{color:"#e6edf3",marginBottom:"24px"}}>Create Project</h2>
            <form onSubmit={(e)=>{e.preventDefault();createMutation.mutate(form);}}>
              {[["Project Name","name","text","My API"],["Description","description","text","What does it do?"]].map(([l,k,t,p])=>(
                <div key={k} style={{marginBottom:"16px"}}>
                  <label style={{color:"#8b949e",fontSize:"13px",display:"block",marginBottom:"6px"}}>{l}</label>
                  <input style={inp} type={t} value={form[k]} onChange={(e)=>setForm({...form,[k]:e.target.value})} placeholder={p} required={k==="name"} />
                </div>
              ))}
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"12px",marginBottom:"24px"}}>
                <div>
                  <label style={{color:"#8b949e",fontSize:"13px",display:"block",marginBottom:"6px"}}>Language</label>
                  <select style={inp} value={form.language} onChange={(e)=>setForm({...form,language:e.target.value})}>
                    {["python","javascript","typescript","go","rust","java","other"].map(l=><option key={l} value={l}>{l}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{color:"#8b949e",fontSize:"13px",display:"block",marginBottom:"6px"}}>Visibility</label>
                  <select style={inp} value={form.visibility} onChange={(e)=>setForm({...form,visibility:e.target.value})}>
                    <option value="private">Private</option>
                    <option value="public">Public</option>
                  </select>
                </div>
              </div>
              <div style={{display:"flex",gap:"12px",justifyContent:"flex-end"}}>
                <button type="button" onClick={()=>setShowForm(false)} style={{background:"transparent",border:"1px solid #30363d",color:"#8b949e",padding:"8px 16px",borderRadius:"6px",cursor:"pointer"}}>Cancel</button>
                <button type="submit" disabled={createMutation.isPending} style={{background:"#58a6ff",color:"#000",border:"none",borderRadius:"6px",padding:"8px 16px",cursor:"pointer",fontWeight:"600"}}>{createMutation.isPending?"Creating...":"Create"}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {isLoading ? <p style={{color:"#8b949e"}}>Loading...</p> : projects.length === 0 ? (
        <div style={{textAlign:"center",padding:"80px",color:"#8b949e"}}>
          <div style={{fontSize:"48px",marginBottom:"16px"}}>📁</div>
          <h3 style={{color:"#e6edf3",marginBottom:"8px"}}>No projects yet</h3>
          <p>Create your first project to start generating docs</p>
        </div>
      ) : (
        <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(280px,1fr))",gap:"16px"}}>
          {projects.map((p)=>(
            <div key={p.id} onClick={()=>navigate(`/projects/${p.id}`)} style={{background:"#161b22",border:"1px solid #30363d",borderRadius:"8px",padding:"20px",cursor:"pointer",transition:"border-color 0.15s"}} onMouseEnter={(e)=>e.currentTarget.style.borderColor="#58a6ff"} onMouseLeave={(e)=>e.currentTarget.style.borderColor="#30363d"}>
              <h3 style={{color:"#e6edf3",marginBottom:"8px"}}>{p.name}</h3>
              {p.description && <p style={{color:"#8b949e",fontSize:"13px",marginBottom:"12px"}}>{p.description}</p>}
              <div style={{display:"flex",gap:"8px",alignItems:"center"}}>
                <span style={{background:"#21262d",border:"1px solid #30363d",borderRadius:"4px",padding:"2px 8px",fontSize:"12px",color:"#8b949e"}}>{p.language}</span>
                <span style={{fontSize:"12px",color:"#8b949e"}}>{p.document_count} docs</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
