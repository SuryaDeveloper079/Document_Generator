import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { documentsApi } from "../api/client";
import axios from "axios";
import toast from "react-hot-toast";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const DOC_TYPES = ["readme","api_reference","architecture","changelog","guide","custom"];

export default function DocumentPage() {
  const { projectId, docId } = useParams();
  const navigate = useNavigate();
  const isNew = docId === "new";
  const pollRef = useRef(null);
  const fileRef = useRef(null);

  const [form, setForm] = useState({ title:"", doc_type:"readme", source_type:"zip", github_url:"", prompt_extras:"" });
  const [zipFile, setZipFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [tab, setTab] = useState("preview");

  const { data: doc, refetch } = useQuery({
    queryKey: ["document", projectId, docId],
    queryFn: () => documentsApi.get(projectId, docId).then((r) => r.data),
    enabled: !isNew,
  });

  useEffect(() => {
    if (!doc || !["pending","processing"].includes(doc.status)) return;
    pollRef.current = setInterval(async () => {
      try {
        const { data: s } = await documentsApi.taskStatus(projectId, docId);
        if (["SUCCESS","FAILURE"].includes(s.status)) {
          clearInterval(pollRef.current);
          refetch();
          if (s.status === "SUCCESS") toast.success("Documentation generated!");
          else toast.error("Generation failed.");
        }
      } catch {}
    }, 3000);
    return () => clearInterval(pollRef.current);
  }, [doc?.status]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) { toast.error("Enter a document title"); return; }
    if (form.source_type === "zip" && !zipFile) { toast.error("Please select a ZIP file"); return; }
    if (form.source_type === "github" && !form.github_url.trim()) { toast.error("Enter a GitHub URL"); return; }

    setUploading(true);
    try {
      let sourceCode = "";

      if (form.source_type === "github") {
        const url = form.github_url.trim();
        const parts = url.replace("https://github.com/","").split("/");
        const owner = parts[0];
        const repo = parts[1]?.split("#")[0]?.split("?")[0];
        if (owner && repo) {
          try {
            toast("Fetching GitHub repo...");
            const [apiRes, readmeRes] = await Promise.all([
              axios.get(`https://api.github.com/repos/${owner}/${repo}`),
              axios.get(`https://api.github.com/repos/${owner}/${repo}/readme`, { headers:{ Accept:"application/vnd.github.raw" } }).catch(()=>({ data:"" })),
            ]);
            sourceCode = `Repository: ${apiRes.data.full_name}
Description: ${apiRes.data.description || "No description"}
Language: ${apiRes.data.language || "Unknown"}
Stars: ${apiRes.data.stargazers_count}
URL: ${apiRes.data.html_url}

README:
${readmeRes.data}`;
          } catch { sourceCode = `GitHub Repository: ${url}`; }
        }
      } else {
        sourceCode = `Generating documentation from uploaded file: ${zipFile?.name}`;
      }

      const createRes = await documentsApi.create(projectId, {
        title: form.title,
        doc_type: form.doc_type,
        source_code: sourceCode,
        source_url: form.source_type === "github" ? form.github_url : undefined,
        prompt_extras: form.prompt_extras || undefined,
        generate_diagrams: false,
        diagram_types: [],
      });

      const newDocId = createRes.data.id;

      if (form.source_type === "zip" && zipFile) {
        const formData = new FormData();
        formData.append("file", zipFile);
        try {
          await axios.post(`${API_URL}/api/v1/projects/${projectId}/documents/${newDocId}/upload-source`, formData, { headers:{ "Content-Type":"multipart/form-data" } });
        } catch {}
      }

      toast.success("Generation started!");
      navigate(`/projects/${projectId}/documents/${newDocId}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to start generation");
    } finally {
      setUploading(false);
    }
  };

  const inp = { background:"#21262d",border:"1px solid #30363d",borderRadius:"6px",color:"#e6edf3",padding:"10px 14px",width:"100%",fontSize:"14px",boxSizing:"border-box",outline:"none" };

  if (isNew) return (
    <div style={{maxWidth:"800px"}}>
      <button onClick={()=>navigate(`/projects/${projectId}`)} style={{background:"transparent",border:"none",color:"#8b949e",cursor:"pointer",marginBottom:"20px",padding:"0",fontSize:"14px"}}>← Back to Project</button>
      <h1 style={{color:"#e6edf3",marginBottom:"24px",fontSize:"22px",display:"flex",alignItems:"center",gap:"8px"}}>⚡ Generate Documentation</h1>

      <form onSubmit={handleSubmit} style={{background:"#161b22",border:"1px solid #30363d",borderRadius:"10px",padding:"28px",display:"flex",flexDirection:"column",gap:"20px"}}>

        {/* Title */}
        <div>
          <label style={{color:"#8b949e",fontSize:"13px",display:"block",marginBottom:"6px"}}>Document Title *</label>
          <input style={inp} value={form.title} onChange={(e)=>setForm({...form,title:e.target.value})} placeholder="e.g. API Reference for My Project" required />
        </div>

        {/* Doc Type */}
        <div>
          <label style={{color:"#8b949e",fontSize:"13px",display:"block",marginBottom:"8px"}}>Documentation Type</label>
          <div style={{display:"flex",flexWrap:"wrap",gap:"8px"}}>
            {DOC_TYPES.map((t)=>(
              <button key={t} type="button" onClick={()=>setForm({...form,doc_type:t})}
                style={{background:form.doc_type===t?"rgba(88,166,255,0.15)":"#21262d",border:`1px solid ${form.doc_type===t?"#58a6ff":"#30363d"}`,color:form.doc_type===t?"#58a6ff":"#8b949e",borderRadius:"6px",padding:"6px 16px",cursor:"pointer",fontSize:"13px",fontWeight:form.doc_type===t?"600":"400"}}>
                {t.replace(/_/g," ")}
              </button>
            ))}
          </div>
        </div>

        {/* Source Toggle */}
        <div>
          <label style={{color:"#8b949e",fontSize:"13px",display:"block",marginBottom:"8px"}}>Source</label>
          <div style={{display:"flex",borderRadius:"8px",overflow:"hidden",border:"1px solid #30363d",width:"fit-content"}}>
            {[["zip","📦 Upload ZIP"],["github","🔗 GitHub Link"]].map(([val,label])=>(
              <button key={val} type="button" onClick={()=>setForm({...form,source_type:val})}
                style={{background:form.source_type===val?"#58a6ff":"#21262d",color:form.source_type===val?"#000":"#8b949e",border:"none",padding:"10px 24px",cursor:"pointer",fontSize:"13px",fontWeight:form.source_type===val?"700":"400",transition:"all 0.15s"}}>
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* ZIP Upload */}
        {form.source_type === "zip" && (
          <div>
            <div
              onClick={()=>fileRef.current?.click()}
              onDragOver={(e)=>{e.preventDefault();setDragging(true);}}
              onDragLeave={()=>setDragging(false)}
              onDrop={(e)=>{e.preventDefault();setDragging(false);const f=e.dataTransfer.files[0];if(f?.name.endsWith(".zip"))setZipFile(f);else toast.error("Please drop a .zip file");}}
              style={{border:`2px dashed ${dragging?"#58a6ff":zipFile?"#3fb950":"#30363d"}`,borderRadius:"10px",padding:"48px 24px",textAlign:"center",cursor:"pointer",background:dragging?"rgba(88,166,255,0.05)":"#21262d",transition:"all 0.15s"}}>
              {zipFile ? (
                <div>
                  <div style={{fontSize:"40px",marginBottom:"10px"}}>📦</div>
                  <div style={{color:"#3fb950",fontWeight:"600",fontSize:"15px"}}>{zipFile.name}</div>
                  <div style={{color:"#8b949e",fontSize:"12px",marginTop:"4px"}}>{(zipFile.size/1024/1024).toFixed(2)} MB</div>
                  <button type="button" onClick={(e)=>{e.stopPropagation();setZipFile(null);fileRef.current.value="";}}
                    style={{marginTop:"12px",background:"transparent",border:"1px solid #f85149",color:"#f85149",borderRadius:"6px",padding:"4px 16px",cursor:"pointer",fontSize:"12px"}}>Remove</button>
                </div>
              ) : (
                <div>
                  <div style={{fontSize:"40px",marginBottom:"10px"}}>📁</div>
                  <div style={{color:"#e6edf3",fontSize:"15px",marginBottom:"6px",fontWeight:"500"}}>Drop your project ZIP here</div>
                  <div style={{color:"#8b949e",fontSize:"13px"}}>or click to browse files</div>
                  <div style={{color:"#8b949e",fontSize:"12px",marginTop:"8px"}}>Supports .zip files up to 10 MB</div>
                </div>
              )}
              <input ref={fileRef} type="file" accept=".zip" style={{display:"none"}} onChange={(e)=>{const f=e.target.files?.[0];if(f)setZipFile(f);}} />
            </div>
          </div>
        )}

        {/* GitHub URL */}
        {form.source_type === "github" && (
          <div>
            <label style={{color:"#8b949e",fontSize:"13px",display:"block",marginBottom:"6px"}}>GitHub Repository URL *</label>
            <input style={inp} type="url" value={form.github_url} onChange={(e)=>setForm({...form,github_url:e.target.value})} placeholder="https://github.com/username/repository" />
            <div style={{color:"#8b949e",fontSize:"12px",marginTop:"6px"}}>Example: https://github.com/facebook/react</div>
          </div>
        )}

        {/* Extra Instructions */}
        <div>
          <label style={{color:"#8b949e",fontSize:"13px",display:"block",marginBottom:"6px"}}>Additional Instructions (optional)</label>
          <textarea style={{...inp,minHeight:"80px",resize:"vertical"}} value={form.prompt_extras} onChange={(e)=>setForm({...form,prompt_extras:e.target.value})}
            placeholder="Focus on authentication, target audience is beginners, include deployment steps..." />
        </div>

        <button type="submit" disabled={uploading}
          style={{background:uploading?"#30363d":"#58a6ff",color:uploading?"#8b949e":"#000",border:"none",borderRadius:"8px",padding:"14px 28px",cursor:uploading?"not-allowed":"pointer",fontWeight:"700",fontSize:"15px",transition:"all 0.15s",width:"fit-content"}}>
          {uploading ? "⏳ Processing..." : "⚡ Generate with Claude AI"}
        </button>
      </form>
    </div>
  );

  if (!doc) return <p style={{color:"#8b949e",padding:"40px"}}>Loading...</p>;

  const STATUS_COLOR = { completed:"#3fb950",pending:"#d29922",processing:"#58a6ff",failed:"#f85149" };

  return (
    <div>
      <button onClick={()=>navigate(`/projects/${projectId}`)} style={{background:"transparent",border:"none",color:"#8b949e",cursor:"pointer",marginBottom:"16px",padding:"0",fontSize:"14px"}}>← Back to Project</button>

      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:"24px",flexWrap:"wrap",gap:"12px"}}>
        <div>
          <h1 style={{color:"#e6edf3",fontSize:"22px",marginBottom:"8px"}}>{doc.title}</h1>
          <div style={{display:"flex",gap:"12px",alignItems:"center",flexWrap:"wrap"}}>
            <span style={{color:STATUS_COLOR[doc.status],fontSize:"13px",fontWeight:"600"}}>● {doc.status}</span>
            <span style={{color:"#8b949e",fontSize:"13px"}}>{doc.doc_type.replace(/_/g," ")}</span>
            {doc.tokens_used > 0 && <span style={{color:"#8b949e",fontSize:"13px"}}>{doc.tokens_used.toLocaleString()} tokens</span>}
            {doc.generation_time_ms > 0 && <span style={{color:"#8b949e",fontSize:"13px"}}>{(doc.generation_time_ms/1000).toFixed(1)}s</span>}
          </div>
        </div>
        {doc.status === "completed" && (
          <div style={{display:"flex",gap:"8px"}}>
            <button onClick={()=>{const b=new Blob([doc.content_markdown||""],{type:"text/markdown"});const u=URL.createObjectURL(b);const a=document.createElement("a");a.href=u;a.download=`${doc.title.replace(/\s+/g,"-")}.md`;a.click();}}
              style={{background:"transparent",border:"1px solid #30363d",color:"#e6edf3",borderRadius:"6px",padding:"8px 16px",cursor:"pointer",fontSize:"13px"}}>⬇ Download .md</button>
            <button onClick={()=>{navigator.clipboard.writeText(doc.content_markdown||"");toast.success("Copied!");}}
              style={{background:"transparent",border:"1px solid #30363d",color:"#e6edf3",borderRadius:"6px",padding:"8px 16px",cursor:"pointer",fontSize:"13px"}}>📋 Copy</button>
          </div>
        )}
      </div>

      {["pending","processing"].includes(doc.status) && (
        <div style={{textAlign:"center",padding:"80px",background:"#161b22",borderRadius:"10px",border:"1px solid #30363d"}}>
          <div style={{fontSize:"40px",marginBottom:"16px"}}>⚡</div>
          <h3 style={{color:"#e6edf3",marginBottom:"8px",fontSize:"18px"}}>Claude is generating your documentation...</h3>
          <p style={{color:"#8b949e"}}>Usually takes 20–40 seconds. Page updates automatically.</p>
        </div>
      )}

      {doc.status === "failed" && (
        <div style={{textAlign:"center",padding:"60px",background:"#161b22",borderRadius:"10px",border:"1px solid #f85149"}}>
          <div style={{fontSize:"32px",marginBottom:"12px"}}>❌</div>
          <h3 style={{color:"#f85149",marginBottom:"8px"}}>Generation failed</h3>
          <p style={{color:"#8b949e"}}>{doc.error_message || "Unknown error"}</p>
          <button onClick={()=>navigate(`/projects/${projectId}/documents/new`)}
            style={{marginTop:"16px",background:"#58a6ff",color:"#000",border:"none",borderRadius:"6px",padding:"8px 20px",cursor:"pointer",fontWeight:"600"}}>Try Again</button>
        </div>
      )}

      {doc.status === "completed" && (
        <div>
          <div style={{display:"flex",borderBottom:"1px solid #30363d",marginBottom:"20px"}}>
            {[["preview","👁 Preview"],["source","📝 Source"]].map(([t,l])=>(
              <button key={t} onClick={()=>setTab(t)}
                style={{background:"transparent",border:"none",borderBottom:`2px solid ${tab===t?"#58a6ff":"transparent"}`,color:tab===t?"#58a6ff":"#8b949e",padding:"10px 20px",cursor:"pointer",fontSize:"14px",marginBottom:"-1px"}}>
                {l}
              </button>
            ))}
          </div>
          {tab === "preview" ? (
            <div className="markdown-preview" style={{background:"#161b22",border:"1px solid #30363d",borderRadius:"10px",padding:"32px",lineHeight:"1.7",color:"#e6edf3"}}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{doc.content_markdown || ""}</ReactMarkdown>
            </div>
          ) : (
            <pre style={{background:"#161b22",border:"1px solid #30363d",borderRadius:"10px",padding:"24px",overflow:"auto",color:"#e6edf3",fontSize:"13px",lineHeight:"1.6",whiteSpace:"pre-wrap",maxHeight:"600px"}}>
              {doc.content_markdown}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
