import { useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { projectsApi, documentsApi } from "../api/client";

const STATUS_COLOR = { completed:"#3fb950", pending:"#d29922", processing:"#58a6ff", failed:"#f85149" };

export default function ProjectPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const { data: project } = useQuery({ queryKey: ["project", projectId], queryFn: () => projectsApi.get(projectId).then((r) => r.data) });
  const { data: documents = [], isLoading } = useQuery({ queryKey: ["documents", projectId], queryFn: () => documentsApi.list(projectId).then((r) => r.data) });

  return (
    <div>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"24px"}}>
        <div>
          <h1 style={{fontSize:"24px",color:"#e6edf3"}}>{project?.name || "Loading..."}</h1>
          {project?.description && <p style={{color:"#8b949e",marginTop:"4px"}}>{project.description}</p>}
        </div>
        <button onClick={()=>navigate(`/projects/${projectId}/documents/new`)} style={{background:"#58a6ff",color:"#000",border:"none",borderRadius:"6px",padding:"8px 16px",cursor:"pointer",fontWeight:"600"}}>+ Generate Doc</button>
      </div>

      {isLoading ? <p style={{color:"#8b949e"}}>Loading...</p> : documents.length === 0 ? (
        <div style={{textAlign:"center",padding:"80px",color:"#8b949e"}}>
          <div style={{fontSize:"48px",marginBottom:"16px"}}>📄</div>
          <h3 style={{color:"#e6edf3",marginBottom:"8px"}}>No documents yet</h3>
          <p>Generate your first documentation with Claude AI</p>
        </div>
      ) : (
        <div style={{display:"flex",flexDirection:"column",gap:"8px"}}>
          {documents.map((doc)=>(
            <div key={doc.id} onClick={()=>navigate(`/projects/${projectId}/documents/${doc.id}`)} style={{background:"#161b22",border:"1px solid #30363d",borderRadius:"8px",padding:"16px",cursor:"pointer",display:"flex",alignItems:"center",gap:"16px"}} onMouseEnter={(e)=>e.currentTarget.style.borderColor="#58a6ff"} onMouseLeave={(e)=>e.currentTarget.style.borderColor="#30363d"}>
              <div style={{flex:1}}>
                <div style={{color:"#e6edf3",fontWeight:"500"}}>{doc.title}</div>
                <div style={{color:"#8b949e",fontSize:"12px",marginTop:"2px"}}>{doc.doc_type}</div>
              </div>
              <span style={{color:STATUS_COLOR[doc.status]||"#8b949e",fontSize:"12px",background:"#21262d",padding:"2px 8px",borderRadius:"20px"}}>{doc.status}</span>
              <span style={{color:"#8b949e",fontSize:"12px"}}>{new Date(doc.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
