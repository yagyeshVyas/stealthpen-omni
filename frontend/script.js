let lastInput = "";

document.getElementById('humanizeBtn').addEventListener('click', handleHumanize);
document.getElementById('rewriteBtn').addEventListener('click', handleRewrite);

async function handleHumanize() {
    const input = document.getElementById('inputText').value.trim();
    const outputArea = document.getElementById('outputText');
    const statusDiv = document.getElementById('status');
    const rewriteBtn = document.getElementById('rewriteBtn');
    const gradeBadge = document.getElementById('bypassGrade');

    if (!input) {
        alert("Please enter some text!");
        return;
    }

    statusDiv.textContent = "🧠 Humanizing...";
    statusDiv.className = "mt-3 text-sm text-yellow-400";
    gradeBadge.className = "text-xs px-2 py-1 rounded bg-yellow-600 text-white";
    gradeBadge.textContent = "Processing...";

    try {
        const response = await fetch('http://localhost:5000/humanize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: input })
        });

        if (response.status === 429) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const result = await response.json();

        if (result.humanized) {
            outputArea.value = result.humanized;
            lastInput = input;
            rewriteBtn.classList.remove('hidden');
            rewriteBtn.disabled = false;

            statusDiv.textContent = "✅ Done! AI detection bypassed.";
            statusDiv.className = "mt-3 text-sm text-green-400";
            gradeBadge.className = "text-xs px-2 py-1 rounded bg-green-600 text-white";
            gradeBadge.textContent = result.bypass_grade || "A";

            updateDashboardStats();
        } else {
            throw new Error(result.error || "Unknown error");
        }
    } catch (err) {
        statusDiv.textContent = "❌ " + err.message;
        statusDiv.className = "mt-3 text-sm text-red-400";
        gradeBadge.className = "text-xs px-2 py-1 rounded bg-red-600 text-white";
        gradeBadge.textContent = "Error";
    }
}

async function handleRewrite() {
    await handleHumanize();
}

async function updateDashboardStats() {
    try {
        const dbRes = await fetch('http://localhost:5000/last_updated');
        const dbData = await dbRes.json();
        document.getElementById('lastUpdated').textContent = dbData.last_updated || "Loading...";
    } catch (e) {
        console.log("Stats update failed:", e);
    }
}

updateDashboardStats();