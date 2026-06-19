const functionSelect = document.getElementById("function-select");
const styleSelect = document.getElementById("style-select");
const assistantForm = document.getElementById("assistant-form");
const userInput = document.getElementById("user-input");
const generateBtn = document.getElementById("generate-btn");
const loading = document.getElementById("loading");
const responseCard = document.getElementById("response-card");
const responseOutput = document.getElementById("response-output");
const feedbackSection = document.getElementById("feedback-section");
const feedbackMessage = document.getElementById("feedback-message");
const copyBtn = document.getElementById("copy-btn");

let lastRequest = null;

function populatePromptStyles() {
    const selectedFunction = functionSelect.value;
    const styles = window.PROMPT_STYLES[selectedFunction] || {};

    styleSelect.innerHTML = "";
    Object.entries(styles).forEach(([value, label]) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = label;
        styleSelect.appendChild(option);
    });
}

function setLoading(isLoading) {
    generateBtn.disabled = isLoading;
    loading.classList.toggle("hidden", !isLoading);
}

function showResponse(message, isError = false) {
    responseCard.classList.remove("hidden");
    responseOutput.textContent = message;
    responseOutput.classList.toggle("error", isError);
    feedbackSection.classList.toggle("hidden", isError);
    feedbackMessage.textContent = "";
}

assistantForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
        function: functionSelect.value,
        prompt_style: styleSelect.value,
        user_input: userInput.value.trim(),
    };

    if (!payload.user_input) {
        showResponse("Please enter text before generating a response.", true);
        return;
    }

    lastRequest = payload;
    setLoading(true);
    showResponse("Preparing your response...");
    feedbackSection.classList.add("hidden");

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to generate a response.");
        }

        showResponse(data.response);
    } catch (error) {
        showResponse(error.message, true);
    } finally {
        setLoading(false);
    }
});

document.querySelectorAll(".feedback-btn").forEach((button) => {
    button.addEventListener("click", async () => {
        if (!lastRequest) {
            feedbackMessage.textContent = "Generate a response before sending feedback.";
            return;
        }

        const payload = {
            function: lastRequest.function,
            prompt_style: lastRequest.prompt_style,
            feedback: button.dataset.feedback,
        };

        try {
            const response = await fetch("/feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Unable to save feedback.");
            }

            feedbackMessage.textContent = data.message;
        } catch (error) {
            feedbackMessage.textContent = error.message;
        }
    });
});

copyBtn.addEventListener("click", async () => {
    const text = responseOutput.textContent.trim();
    if (!text) {
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        copyBtn.textContent = "Copied";
        setTimeout(() => {
            copyBtn.textContent = "Copy";
        }, 1600);
    } catch {
        copyBtn.textContent = "Copy failed";
        setTimeout(() => {
            copyBtn.textContent = "Copy";
        }, 1600);
    }
});

functionSelect.addEventListener("change", populatePromptStyles);
populatePromptStyles();
