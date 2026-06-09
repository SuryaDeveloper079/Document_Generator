import { Outlet, NavLink } from "react-router-dom";

export default function Layout() {
  return (
    <div style={{display:"flex",minHeight:"100vh",background:"#0f1117",color:"#e6edf3"}}>
      <aside style={{width:"220px",background:"#161b22",borderRight:"1px solid #30363d",padding:"20px",display:"flex",flexDirection:"column"}}>
        <div style={{fontSize:"20px",fontWeight:"700",color:"#58a6ff",marginBottom:"32px"}}>⚡ DocGen AI</div>
        <NavLink to="/dashboard" style={({isActive})=>({display:"block",padding:"8px 12px",borderRadius:"6px",color:isActive?"#58a6ff":"#8b949e",textDecoration:"none",background:isActive?"#21262d":"transparent"})}>
          📁 Dashboard
        </NavLink>
      </aside>
      <main style={{flex:1,padding:"32px",overflow:"auto"}}>
        <Outlet />
      </main>
    </div>
  );
}
