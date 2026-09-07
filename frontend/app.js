document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");

    streamResponse(uploadForm, fileInput);

    const responseBox = document.getElementById("responseBox");
    const queryButton = document.getElementById("queryButton");
    const queryInput = document.getElementById("queryInput");

    streamResponse(queryInput, queryButton, responseBox)
});


 // -----------------------------
// Query Handler
// -----------------------------
async function streamResponse(queryInput, queryButton, responseBox) {
    queryButton.addEventListener("click", async () => {
        const query = queryInput.value.trim();
        if (!query) {
            alert("Please enter a query.");
            return;
        }

        responseBox.style.display = "block";
        responseBox.innerText = ""; // clear previous output

        try {
            const res = await fetch("http://localhost:8000/response_generation/answer", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: query })
            });

            // DO NOT USE res.json() — it breaks streaming
            const reader = res.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                responseBox.innerText += decoder.decode(value);   // append streamed text
            }

        } catch (err) {
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