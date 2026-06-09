require("dotenv").config();
const express = require("express");
const helmet = require("helmet");
const morgan = require("morgan");
const rateLimit = require("express-rate-limit");

const app = express();
const PORT = process.env.PORT || 3001;
const API_KEY = process.env.NODE_SERVICE_API_KEY || "node-service-internal-key";

app.use(helmet());
app.use(morgan("combined"));
app.use(express.json({ limit: "2mb" }));
app.use(rateLimit({ windowMs: 60000, max: 100 }));

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "diagram-renderer", uptime: Math.floor(process.uptime()) });
});

app.post("/render", (req, res) => {
  const key = req.headers["x-api-key"];
  if (!key || key !== API_KEY) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  const { code, tool, type } = req.body;
  if (!code) return res.status(400).json({ error: "code is required" });
  res.json({
    svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200"><rect width="400" height="200" fill="#1a1a2e"/><text x="200" y="100" text-anchor="middle" fill="#58a6ff" font-size="16">${type} diagram</text></svg>`,
    tool,
    type,
    render_time_ms: 10,
  });
});

app.listen(PORT, () => {
  console.log(`[DiagramService] Running on port ${PORT}`);
});
