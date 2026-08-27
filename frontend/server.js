import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const app = express();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
console.log("Server file located at:", __dirname);
console.log("Static root:", path.join(__dirname));

// Print the folder Express will serve
console.log("Static root:", path.join(__dirname));

// Serve the entire frontend folder
app.use(express.static(path.join(__dirname)));

app.listen(3000, () => {
  console.log("Frontend running at http://localhost:3000");
});