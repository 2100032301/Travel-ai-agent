// frontend/script.js
function sendRequest() {
    const userInput = document.getElementById("userInput").value;
    if (!userInput) return;

    // Display the user's request in the chat box
    const chatBox = document.getElementById("chatBox");
    chatBox.innerHTML += `<p class="user"><strong>You:</strong> ${userInput}</p>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    // Clear the input field
    document.getElementById("userInput").value = "";

    // Show loading indicator
    const loadingDiv = document.getElementById("loading");
    loadingDiv.style.display = "block";

    // Send the task to the server
    fetch("/api/plan", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ task: userInput }),
    })
        .then((response) => response.json())
        .then((data) => {
            // Hide loading indicator
            loadingDiv.style.display = "none";

            if (data.error) {
                chatBox.innerHTML += `<p class="agent"><strong>Error:</strong> ${data.error}</p>`;
            } else {
                // Process each agent's response
                data.responses.forEach((msg) => {
                    // Parse the itinerary into sections and steps
                    let formattedResponse = formatItinerary(msg.response);
                    chatBox.innerHTML += `<div class="agent"><strong>${msg.agent}:</strong>${formattedResponse}</div>`;

                    // Add event listeners for collapsible sections
                    addSectionToggleListeners();
                });
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch((error) => {
            // Hide loading indicator on error
            loadingDiv.style.display = "none";
            chatBox.innerHTML += `<p class="agent"><strong>Error:</strong> ${error.message}</p>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        });
}

// Function to format the itinerary into sections and steps
function formatItinerary(response) {
    // Split the response into lines
    const lines = response.split('\n').filter(line => line.trim() !== '');
    let html = '';
    let currentSection = null;
    let sectionContent = '';

    lines.forEach((line, index) => {
        // Check for section headers (e.g., **Morning:**, **Midday:**)
        const sectionMatch = line.match(/\*\*(.*?):\*\*/);
        if (sectionMatch) {
            // Close the previous section if it exists
            if (currentSection) {
                html += `
                    <div class="section">
                        <div class="section-header">
                            ${currentSection} <i class="fas fa-chevron-down toggle-icon"></i>
                        </div>
                        <div class="section-content">
                            ${sectionContent}
                        </div>
                    </div>`;
            }
            // Start a new section
            currentSection = sectionMatch[1];
            sectionContent = '';
        } else if (line.trim() === '---') {
            // Add a separator
            sectionContent += '<hr>';
        } else if (currentSection) {
            // Format steps within the section
            let stepText = line
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold text
                .trim();
            if (stepText) {
                // Add an icon based on the content (e.g., clock for time, fork for food)
                let iconClass = 'fa-clock';
                if (stepText.toLowerCase().includes('lunch') || stepText.toLowerCase().includes('dinner') || stepText.toLowerCase().includes('breakfast')) {
                    iconClass = 'fa-utensils';
                } else if (stepText.toLowerCase().includes('drive') || stepText.toLowerCase().includes('boat')) {
                    iconClass = 'fa-car';
                }
                sectionContent += `
                    <div class="step">
                        <i class="fas ${iconClass}"></i>
                        <div class="step-text">${stepText}</div>
                    </div>`;
            }
        } else {
            // For non-section content (e.g., intro or tips), treat as plain text
            let plainText = line
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .trim();
            if (plainText) {
                html += `<p>${plainText}</p>`;
            }
        }
    });

    // Close the last section
    if (currentSection) {
        html += `
            <div class="section">
                <div class="section-header">
                    ${currentSection} <i class="fas fa-chevron-down toggle-icon"></i>
                </div>
                <div class="section-content">
                    ${sectionContent}
                </div>
            </div>`;
    }

    return html;
}

// Function to add toggle functionality to section headers
function addSectionToggleListeners() {
    document.querySelectorAll('.section-header').forEach(header => {
        header.addEventListener('click', () => {
            const content = header.nextElementSibling;
            const icon = header.querySelector('.toggle-icon');
            if (content.style.display === 'block') {
                content.style.display = 'none';
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
            } else {
                content.style.display = 'block';
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-up');
            }
        });
    });
}

// Allow pressing Enter to send the request
document.getElementById("userInput").addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
        sendRequest();
    }
});