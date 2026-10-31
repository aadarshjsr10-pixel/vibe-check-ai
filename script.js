
const form = document.getElementById("vibeForm");

if (form) {
    form.addEventListener("submit", async function(event) {
        event.preventDefault();

        const button = document.getElementById("analyzeBtn");
        const error = document.getElementById("errorMessage");

        error.textContent = "";
        button.disabled = true;
        button.textContent = "ANALYZING... ✨";

        const data = {
            name: document.getElementById("name").value.trim(),
            username: document.getElementById("username").value.trim(),
            hobby: document.getElementById("hobby").value.trim(),
            personality: document.getElementById("personality").value,
            mood: document.getElementById("mood").value,
            consent: document.getElementById("consent").checked
        };

        try {
            const response = await fetch("/analyze", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Something went wrong");
            }

            const fields = {
                resultName: result.name,
                resultUsername: result.username,
                resultVibe: result.vibe,
                resultScore: result.score,
                resultFunny: result.funny,
                resultCompliment: result.compliment,
                resultRoast: result.roast,
                resultCute: result.cute,
                resultVerdict: result.verdict
            };

            for (const [id, value] of Object.entries(fields)) {
                document.getElementById(id).textContent = value;
            }

            document.getElementById("resultSection")
                .classList.remove("hidden");

            document.getElementById("resultSection")
                .scrollIntoView({ behavior: "smooth" });

        } catch (err) {
            error.textContent = err.message;
        } finally {
            button.disabled = false;
            button.textContent = "✨ ANALYZE MY VIBE";
        }
    });
}


// Share report
const shareButton = document.getElementById("shareBtn");

if (shareButton) {
    shareButton.addEventListener("click", async function() {
        const text =
            "✨ MY VIBE CHECK REPORT ✨\n" +
            "Name: " + document.getElementById("resultName").textContent +
            "\nVibe: " + document.getElementById("resultVibe").textContent +
            "\nScore: " + document.getElementById("resultScore").textContent +
            "/100";

        try {
            if (navigator.share) {
                await navigator.share({
                    title: "My Vibe Check",
                    text: text
                });
            } else {
                await navigator.clipboard.writeText(text);
                alert("Result copied!");
            }
        } catch (err) {
            if (err.name !== "AbortError") {
                alert("Could not share result.");
            }
        }
    });
}


// Try again
const againButton = document.getElementById("againBtn");

if (againButton) {
    againButton.addEventListener("click", function() {
        form.reset();
        document.getElementById("resultSection")
            .classList.add("hidden");

        window.scrollTo({ top: 0, behavior: "smooth" });
    });
}

