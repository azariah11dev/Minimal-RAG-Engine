document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");

    setupUploadHandler(uploadForm, fileInput);

    const responseBox = document.getElementById("responseBox");
    const queryButton = document.getElementById("queryButton");
    const queryInput = document.getElementById("queryInput");
});


 // -----------------------------
// Query Handler (under construction ignore for now)
// -----------------------------
async function streamResponse(query) {
    queryButton.addEventListener("click", async () => {
        const query = queryInput.value.trim();
        if (!query) {
            alert("Please enter a query.");
            return;
        }

        try {
            const res = await fetch("http://localhost:8000/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query })
            });

            const data = await res.json();
            responseBox.style.display = "block";
            responseBox.innerText = JSON.stringify(data, null, 2);

        } catch (err) {
            responseBox.style.display = "block";
            responseBox.innerText = "Error: " + err;
        }
    });
}

// -----------------------------
// File Upload Handler
// -----------------------------
async function setupUploadHandler(uploadForm, fileInput) {
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            alert("Please select a file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("http://localhost:8000/document_uploader/upload", {
                method: "POST",
                body: formData
            });

            const data = await res.json();

            if (res.ok) {
                alert("Document uploaded successfully!");
            } else {
                alert(data.detail || "Upload failed");
            }

        } catch (err) {
            console.error("Upload error:", err);
            alert("Error uploading document");
        }
    });
}