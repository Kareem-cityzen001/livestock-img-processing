// Get DOM elements with checks
const imageInput = document.getElementById("imageInput");
const previewImage = document.getElementById("previewImage");
const placeholderText = document.getElementById("placeholderText");
const analyzeBtn = document.getElementById("analyzeBtn");
const result = document.getElementById("result");
const resultContainer = document.getElementById("resultContainer");
const searchDiseaseBtn = document.getElementById("searchDiseaseBtn");
const analyzeNewBtn = document.getElementById("analyzeNewBtn");
const reportBtn = document.getElementById("reportBtn");
const behaviorDescription = document.getElementById("behaviorDescription");
const chatWithVetBtn = document.getElementById("chatWithVetBtn");

// Debug: log if elements are found
console.log("[INIT] DOM Elements check:");
console.log("[INIT] imageInput:", imageInput ? "✓" : "✗ MISSING");
console.log("[INIT] previewImage:", previewImage ? "✓" : "✗ MISSING");
console.log("[INIT] analyzeBtn:", analyzeBtn ? "✓" : "✗ MISSING");
console.log("[INIT] result:", result ? "✓" : "✗ MISSING");

let selectedFile = null;
let currentDisease = null;
let currentAnalysisData = null;

// Warn if critical elements are missing
if (!imageInput || !previewImage || !analyzeBtn) {
    console.error("[INIT] ERROR: Critical DOM elements missing!");
}

// 1. PREVIEW IMAGE
if (imageInput) {
    imageInput.addEventListener("change", function () {
        console.log("[PREVIEW] Image input changed");

        selectedFile = this.files[0];

        if (!selectedFile) {
            console.warn("[PREVIEW] No file selected");
            previewImage.style.display = "none";
            placeholderText.innerHTML = "📷 No image selected";
            placeholderText.style.display = "block";
            result.innerHTML = "";
            return;
        }

        console.log(`[PREVIEW] File selected:`, {
            name: selectedFile.name,
            size: selectedFile.size,
            type: selectedFile.type
        });

        // Validate file type
        if (!selectedFile.type.startsWith('image/')) {
            console.error("[PREVIEW] Invalid file type:", selectedFile.type);
            result.innerHTML = "<span style='color: #f44336; font-weight: 600;'>❌ Please select a valid image file (JPG, PNG, GIF, etc.)</span>";
            placeholderText.innerHTML = "❌ Invalid image format";
            previewImage.style.display = "none";
            placeholderText.style.display = "block";
            return;
        }

        const reader = new FileReader();

        reader.onprogress = function (event) {
            if (event.lengthComputable) {
                const percentComplete = (event.loaded / event.total) * 100;
                console.log(`[PREVIEW] Loading: ${percentComplete.toFixed(1)}%`);
            }
        };

        reader.onload = function (e) {
            try {
                console.log("[PREVIEW] FileReader loaded successfully");
                console.log("[PREVIEW] Data URL length:", e.target.result.length);

                previewImage.src = e.target.result;

                // Wait for image to load before displaying
                previewImage.onload = function () {
                    console.log("[PREVIEW] Image element loaded and displayed");
                    placeholderText.style.display = "none";
                    previewImage.style.display = "block";
                    result.innerHTML = "<em style='color: #666;'>✅ Image loaded. Click <strong>'Analyze Health Condition'</strong> to start diagnosis.</em>";
                };

                previewImage.onerror = function (err) {
                    console.error("[PREVIEW] Image failed to load:", err);
                    result.innerHTML = "<span style='color: #f44336; font-weight: 600;'>❌ Failed to load image. Try another file.</span>";
                    placeholderText.style.display = "block";
                    previewImage.style.display = "none";
                };

                // Set a timeout in case onload doesn't fire
                setTimeout(() => {
                    if (previewImage.style.display === "none" && previewImage.src) {
                        console.log("[PREVIEW] Forcing display after timeout");
                        placeholderText.style.display = "none";
                        previewImage.style.display = "block";
                    }
                }, 500);

            } catch (err) {
                console.error("[PREVIEW] Error in onload:", err);
                result.innerHTML = "<span style='color: #f44336; font-weight: 600;'>❌ Error processing image: " + err.message + "</span>";
            }
        };

        reader.onerror = function (err) {
            console.error("[PREVIEW] FileReader error:", err);
            result.innerHTML = "<span style='color: #f44336; font-weight: 600;'>❌ Error reading file. Try again.</span>";
            placeholderText.style.display = "block";
            previewImage.style.display = "none";
        };

        console.log("[PREVIEW] Starting to read file as data URL");
        reader.readAsDataURL(selectedFile);
    });
}

// 2. ANALYZE IMAGE
if (analyzeBtn) {
    analyzeBtn.addEventListener("click", async function (event) {
        event.preventDefault();
        event.stopPropagation();

        if (!selectedFile) {
            result.innerHTML = "<span style='color: #f44336; font-weight: 600;'>⚠️ Please select an image first.</span>";
            return;
        }

        // UI Feedback
        analyzeBtn.disabled = true;
        analyzeBtn.innerText = "🔄 Analyzing...";
        result.innerHTML = "<em style='color: #666;'>Connecting to AI diagnostic engine...</em>";
        searchDiseaseBtn.classList.add("hidden");
        chatWithVetBtn.classList.add("hidden");

        const formData = new FormData();
        formData.append("image", selectedFile);

        // Include animal behavior description
        const descriptionText = behaviorDescription ? behaviorDescription.value.trim() : "";
        if (descriptionText) {
            formData.append("behavior_description", descriptionText);
        }

        console.log('[UPLOAD] Starting upload:', {
            filename: selectedFile.name,
            size: selectedFile.size,
            type: selectedFile.type,
            formDataSize: new Blob(Object.values(formData)).size
        });

        try {
            console.log('[UPLOAD] Sending request to http://127.0.0.1:5000/upload');
            const response = await fetch("http://127.0.0.1:5000/upload", {
                method: "POST",
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            console.log('[UPLOAD] Response status:', response.status, response.statusText);

            // Read response as text first to see potential HTML error pages
            const responseText = await response.text();
            console.log('[UPLOAD] Response text:', responseText.substring(0, 500));

            // Try to parse as JSON
            let data;
            try {
                data = JSON.parse(responseText);
            } catch (e) {
                console.error('[UPLOAD] Failed to parse JSON response:', e);
                throw new Error(`Server returned invalid response: ${responseText.substring(0, 200)}`);
            }

            if (!response.ok) {
                throw new Error(data.error || `Server error: ${response.status}`);
            }

            console.log('[UPLOAD] Success! Received diagnosis:', data);
            currentAnalysisData = data;

            // Store analysis in localStorage for dashboard
            if (data.Diagnosis) {
                saveAnalysisToLocalStorage(data, selectedFile);
            }

            // Show results with animation
            setTimeout(() => {
                resultContainer.classList.remove("hidden");

                // If the backend could not determine the disease, show a helpful guidance panel
                if (data.Status && (data.Status.toLowerCase().includes("unknown") || data.Diagnosis && data.Diagnosis.toLowerCase().includes("unknown"))) {
                    result.innerHTML = `
                    <div style="background: #fff3f2; padding: 18px; border-radius: 12px; border-left: 5px solid #d32f2f; margin-bottom: 14px;">
                        <div style="font-size: 1.1rem; font-weight: 700; color: #b71c1c; margin-bottom: 8px;">Diagnosis Unclear</div>
                        <p style="color: #333; margin: 6px 0 12px; line-height: 1.5">We couldn't confidently identify the disease from this image. The additional description you provided can help - try the suggestions below to improve results or consult a veterinarian.</p>
                        <ul style="color: #333; margin: 0 0 8px 18px;">
                            <li>Retake photo with better lighting and include the whole animal or affected area.</li>
                            <li>Try another angle or a closer shot of symptoms (lesions, hooves, udder).</li>
                            <li>Ensure image is not blurry and use JPG/PNG formats.</li>
                        </ul>
                        <p style="margin-top:8px"><strong>Need immediate help?</strong> Contact a veterinarian or use the "Learn More" button to search for information.</p>
                    </div>
                `;
                    searchDiseaseBtn.classList.remove("hidden");
                    chatWithVetBtn.classList.remove("hidden");
                    analyzeBtn.disabled = false;
                    analyzeBtn.innerText = "📸 Analyze Health Condition";
                    return;
                }

                if (data.error) {
                    result.innerHTML = `<span style='color: #f44336; font-weight: 600;'>❌ Error: ${data.error}</span>`;
                    searchDiseaseBtn.classList.add("hidden");
                } else {
                    currentDisease = data.Diagnosis;

                    let behaviorInsight = "";
                    if (descriptionText) {
                        behaviorInsight = `
                        <div style="background: #f3e5f5; padding: 14px; border-radius: 12px; border-left: 5px solid #9c27b0; margin-bottom: 14px;">
                            <strong style="color: #6a1b9a; display: block; margin-bottom: 6px;">📝 Farmer's Note (Used in Analysis)</strong>
                            <p style="color: #6a1b9a; margin: 0; font-style: italic; font-size: 0.95rem;">"${descriptionText}"</p>
                        </div>
                    `;
                    }

                    // If backend returned a public image URL, show a thumbnail/link
                    let uploadedImageHtml = '';
                    if (data.image_url) {
                        uploadedImageHtml = `
                        <div style="margin-bottom:12px; text-align:center;">
                            <a href="${data.image_url}" target="_blank" rel="noopener">
                                <img src="${data.image_url}" alt="Uploaded image" style="max-width:100%; border-radius:10px; border:1px solid #eee;">
                            </a>
                        </div>
                    `;
                    }

                    result.innerHTML = `
                    ${uploadedImageHtml}
                    ${behaviorInsight}
                    
                    <div style="background: #fff; padding: 16px; border-radius: 12px; border-left: 5px solid #1a472a; margin-bottom: 14px;">
                        <div style="font-size: 0.9rem; color: #666; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">🔍 DIAGNOSIS RESULT</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #1a472a; margin: 10px 0;">${data.Diagnosis || "Unknown"}</div>
                        <div style="font-size: 0.85rem; color: #ff6b35; font-weight: 600;">Confidence: ${data.Confidence || "N/A"}</div>
                    </div>

                    <div style="background: #fff; padding: 14px; border-radius: 12px; border-left: 5px solid #2d5f3f; margin-bottom: 14px;">
                        <strong style="color: #1a472a; display: block; margin-bottom: 8px;">📊 Status</strong>
                        <span style="color: #f44336; font-weight: 600; font-size: 1.1em;">${data.Status || "N/A"}</span>
                    </div>

                    <div style="background: #fff; padding: 14px; border-radius: 12px; border-left: 5px solid #ff9800; margin-bottom: 14px;">
                        <strong style="color: #1a472a; display: block; margin-bottom: 8px;">⚠️ Severity Level</strong>
                        <span style="color: #ff6b35; font-weight: 600;">${data.Severity || "N/A"}</span>
                    </div>

                    <div style="background: #ffebee; padding: 14px; border-radius: 12px; border-left: 5px solid #f44336; margin-bottom: 14px;">
                        <strong style="color: #c62828; display: block; margin-bottom: 8px;">🚨 RECOMMENDED ACTION</strong>
                        <p style="color: #d32f2f; margin: 8px 0; line-height: 1.6; font-weight: 500;">${data.Action || "Consult a veterinarian"}</p>
                    </div>

                    <div style="background: #fff3e0; padding: 14px; border-radius: 12px; border-left: 5px solid #ff9800; margin-bottom: 14px;">
                        <strong style="color: #e65100; display: block; margin-bottom: 8px;">💊 Treatment Guidelines</strong>
                        <p style="color: #e65100; margin: 8px 0; line-height: 1.6; font-size: 0.95rem;">${data.Treatment || "Professional evaluation required"}</p>
                    </div>

                    <div style="background: #e3f2fd; padding: 14px; border-radius: 12px; border-left: 5px solid #2196f3; margin-bottom: 14px;">
                        <strong style="color: #1565c0; display: block; margin-bottom: 8px;">🦠 Contagiousness</strong>
                        <span style="color: #1565c0; font-weight: 600;">${data.Contagious || "Unknown"}</span>
                    </div>

                    <div style="background: #fce4ec; padding: 14px; border-radius: 12px; border-left: 5px solid #e91e63;">
                        <strong style="color: #880e4f; display: block; margin-bottom: 8px;">🔒 Quarantine Status</strong>
                        <span style="color: #880e4f; font-weight: 600;">${data.Quarantine || "As needed"}</span>
                    </div>
                `;

                    // Show search button
                    searchDiseaseBtn.classList.remove("hidden");
                    chatWithVetBtn.classList.remove("hidden");
                    if (reportBtn) reportBtn.classList.remove("hidden");
                }

                analyzeBtn.disabled = false;
                analyzeBtn.innerText = "📸 Analyze Health Condition";
            }, 800);

        } catch (error) {
            console.error("[UPLOAD] Error details:", error);

            let errorMessage = error.message || "Unknown error";

            // Provide specific error messages
            if (error.message.includes("Failed to fetch")) {
                errorMessage = "Cannot connect to server. Make sure Python server is running on http://127.0.0.1:5000";
            } else if (error.message.includes("Server returned invalid")) {
                errorMessage = "Server returned an unexpected response. Check server logs for details.";
            } else if (error.message.includes("Server error")) {
                errorMessage = error.message;
            }

            result.innerHTML = `
            <div style="background: #ffebee; padding: 16px; border-radius: 12px; border-left: 5px solid #f44336;">
                <div style="color: #c62828; font-weight: 700; margin-bottom: 8px;">❌ Upload Failed</div>
                <div style="color: #d32f2f; margin-bottom: 12px; line-height: 1.5;">
                    ${errorMessage}
                </div>
                <div style="background: #fff; padding: 12px; border-radius: 8px; font-size: 0.85rem; color: #666; margin-top: 12px;">
                    <strong>Troubleshooting:</strong>
                    <ul style="margin: 8px 0 0 18px; padding: 0;">
                        <li>Check if Python server is running: <code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">python app.py</code></li>
                        <li>Verify the server is on http://127.0.0.1:5000</li>
                        <li>Check browser console (F12) for detailed errors</li>
                        <li>Ensure image file is valid (JPG, PNG, etc.)</li>
                        <li>Try refreshing the page</li>
                    </ul>
                </div>
            </div>
        `;

            searchDiseaseBtn.classList.add("hidden");
            analyzeBtn.disabled = false;
            analyzeBtn.innerText = "🔄 Retry Analysis";
        }
    });

    // 3. SEARCH DISEASE ONLINE (INTERNET CONNECTIVITY)
    searchDiseaseBtn.addEventListener("click", function () {
        if (currentDisease) {
            const searchQuery = encodeURIComponent(currentDisease + " livestock cattle treatment symptoms");
            const googleSearchUrl = `https://www.google.com/search?q=${searchQuery}`;
            window.open(googleSearchUrl, '_blank');
        }
    });

    // 3B. ADD MORE DETAILS (Chat with context)
    if (chatWithVetBtn) {
        chatWithVetBtn.addEventListener("click", function () {
            const diseaseInfo = currentDisease || "Unknown Disease";
            const behaviorInfo = behaviorDescription?.value || "No additional behavioral notes provided";

            // Open email client to contact veterinarian with pre-filled context
            const subject = encodeURIComponent(`Livestock Disease Query: ${diseaseInfo}`);
            const body = encodeURIComponent(
                `I need help with an animal showing signs of ${diseaseInfo}.\n\n` +
                `Animal Behavior & Symptoms:\n${behaviorInfo}\n\n` +
                `Can you please provide more information or recommendations?`
            );

            // Alternative: If you have a veterinarian contact system, replace with your backend API
            // For now, we'll show a prompt to add more details
            const additionalDetails = prompt("Add more details for the veterinarian:\n(e.g., duration of symptoms, other animals affected, treatment attempts)");

            if (additionalDetails) {
                const updatedBody = encodeURIComponent(
                    `Disease: ${diseaseInfo}\n\n` +
                    `Initial Observations:\n${behaviorInfo}\n\n` +
                    `Additional Details:\n${additionalDetails}\n\n` +
                    `Please provide recommendations.`
                );

                // You can uncomment this to send email or replace with your API endpoint
                // window.location.href = `mailto:veterinarian@example.com?subject=${subject}&body=${updatedBody}`;

                // Show confirmation
                alert("✅ Details noted. You can now:\n1. Report the case (📝 Report Case button)\n2. Search online for more information (magnifying glass button)");
            }
        });
    }

    // 4. REPORT CASE
    if (reportBtn) {
        reportBtn.addEventListener("click", async function () {
            if (!selectedFile) {
                alert("No image available to report. Please analyze an image first.");
                return;
            }

            reportBtn.disabled = true;
            const prevText = reportBtn.innerText;
            reportBtn.innerText = "📤 Reporting...";

            try {
                const formData = new FormData();
                formData.append("image", selectedFile);
                formData.append("Diagnosis", currentDisease || "Unknown");
                formData.append("behavior_description", behaviorDescription?.value || "");

                // Include other diagnostic data
                if (currentAnalysisData) {
                    formData.append("Confidence", currentAnalysisData.Confidence || "");
                    formData.append("Status", currentAnalysisData.Status || "");
                    formData.append("Severity", currentAnalysisData.Severity || "");
                    formData.append("Action", currentAnalysisData.Action || "");
                }

                const resp = await fetch("/report", {
                    method: "POST",
                    body: formData
                });

                const json = await resp.json();
                if (resp.ok && json.ok) {
                    reportBtn.innerText = "✅ Reported";
                    reportBtn.disabled = true;
                    // show small confirmation in results
                    const confirm = document.createElement('div');
                    confirm.style.marginTop = '10px';
                    confirm.style.color = '#2e7d32';
                    confirm.style.fontWeight = '600';
                    confirm.innerText = '✓ Report saved — our team can review this case including your behavioral notes.';
                    result.appendChild(confirm);
                } else {
                    throw new Error(json.message || 'Report failed');
                }

            } catch (err) {
                console.error('Report error', err);
                alert('Could not submit report: ' + err.message);
                reportBtn.disabled = false;
                reportBtn.innerText = prevText;
            }
        });
    }

    // 5. ANALYZE NEW IMAGE
    analyzeNewBtn.addEventListener("click", function () {
        // Reset form
        imageInput.value = '';
        selectedFile = null;
        previewImage.style.display = 'none';
        placeholderText.style.display = 'block';
        placeholderText.innerText = 'No image selected';
        result.innerHTML = '';
        resultContainer.classList.add('hidden');
        analyzeBtn.innerText = '📸 Analyze Health Condition';
        analyzeBtn.disabled = false;
        currentDisease = null;
        currentAnalysisData = null;

        // Clear or keep behavior description based on user preference
        // Currently keeping it for reference, but user can clear manually
    });

    // ===== DASHBOARD INTEGRATION =====
    // Save analysis results to localStorage for dashboard
    function saveAnalysisToLocalStorage(analysisData, imageFile) {
        try {
            // Get existing analyses
            const recent = JSON.parse(localStorage.getItem('recentAnalyses') || '[]');

            // Create analysis entry
            const entry = {
                timestamp: Date.now(),
                diagnosis: analysisData.Diagnosis || 'Unknown',
                confidence: parseFloat(analysisData.Confidence?.replace('%', '') || 0) / 100,
                severity: analysisData.Severity || 'Unknown',
                status: analysisData.Status || 'Unknown',
                filename: imageFile?.name || 'analysis',
                image: generateBase64Thumbnail(imageFile)
            };

            // Add to beginning of array (most recent first)
            recent.unshift(entry);

            // Keep only last 20 analyses
            const trimmed = recent.slice(0, 20);

            // Save to localStorage
            localStorage.setItem('recentAnalyses', JSON.stringify(trimmed));

            console.log('[Dashboard] Analysis saved to local storage', entry);
        } catch (err) {
            console.warn('[Dashboard] Could not save to localStorage:', err);
        }
    }

    // Generate small base64 thumbnail of image
    function generateBase64Thumbnail(imageFile) {
        if (!imageFile) return null;

        const reader = new FileReader();
        reader.addEventListener('load', function () {
            // Store is handled via event, this is synchronous
        });

        // For now, just use a data URL if available
        if (previewImage && previewImage.src && previewImage.src.startsWith('data:')) {
            return previewImage.src.substring(0, 500) + '...'; // truncate for storage
        }

        return null;
    }

    // Listen for storage changes (from other tabs/windows)
    window.addEventListener('storage', function (e) {
        if (e.key === 'recentAnalyses') {
            console.log('[Dashboard] Analysis history updated from another source');
        }
    });

}

