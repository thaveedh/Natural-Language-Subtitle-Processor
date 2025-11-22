// login
function login() {
    const user = document.getElementById("username").value;
    const pass = document.getElementById("password").value;
    const msg = document.getElementById("login-msg");
    if(user === "admin" && pass === "1234"){
        document.querySelector(".login-container").style.display = "none";
        document.querySelector(".main-ui").style.display = "block";
    } else {
        msg.textContent = "Invalid credentials!";
    }
}

// upload & show subtitles
document.getElementById("uploadBtn").addEventListener("click", async () => {
    const file = document.getElementById("videoInput").files[0];
    if(!file) return alert("Select video first!");

    const formData = new FormData();
    formData.append("video", file);

    const res = await fetch("/process-video", { method:"POST", body: formData });
    const data = await res.json();

    const player = document.getElementById("videoPlayer");
    player.src = `/uploads/${data.video_filename}`;

    const output = document.getElementById("output");
    output.innerHTML = "";

    data.data.segments.forEach(seg => {
        const div = document.createElement("div");
        div.className = "segment";
        div.innerHTML = `<div class="time">[${seg.start.toFixed(2)}s - ${seg.end.toFixed(2)}s]</div>
                         <div>${seg.tamil_text}</div>`;
        output.appendChild(div);
    });
});
