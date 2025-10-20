const BASE = (window.BASE_API_URL) ? window.BASE_API_URL : "http://127.0.0.1:8000";

async function postStructured(payload){
  const res = await fetch(BASE + "/recommend/structured", {
    method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload)
  });
  if(!res.ok) throw new Error("Server error " + res.status);
  return await res.json();
}

async function postChat(text){
  const res = await fetch(BASE + "/recommend/chat", {
    method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({text})
  });
  if(!res.ok) throw new Error("Server error " + res.status);
  return await res.json();
}

async function uploadCV(file){
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(BASE + "/upload_cv", {method:"POST", body: fd});
  if(!res.ok) throw new Error("Upload failed " + res.status);
  return await res.json();
}

function renderResults(results, containerId="results"){
  const container = document.getElementById(containerId);
  container.innerHTML = "";
  if(!results || results.length === 0){
    container.innerHTML = "<div class='card'>No recommendations found.</div>";
    return;
  }
  results.forEach(job => {
    const el = document.createElement("div");
    el.className = "job-card";
    el.innerHTML = `
      <h3>${job.title}</h3>
      <div class="small">${job.company || ""} • ${job.location || ""}</div>
      <p>${job.description ? (job.description.slice(0,300) + (job.description.length>300 ? "..." : "")) : ""}</p>
      <div class="small">Skills: ${job.skills || "N/A"}</div>
      <div style="margin-top:8px"><strong>Match:</strong> ${job.match_score}%</div>
      ${job.link ? `<div style="margin-top:8px"><a href="${job.link}" target="_blank">Open on LinkedIn / Source</a></div>` : ""}
    `;
    container.appendChild(el);
  });
}
