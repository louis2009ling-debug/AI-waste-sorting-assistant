(function () {
    const requiredElementIds = [
        "start-camera-button",
        "capture-button",
        "camera-video",
        "camera-canvas",
        "camera-message",
        "camera-result",
        "captured-image"
    ];

    const missingElementIds = requiredElementIds.filter(function (id) {
        return !document.getElementById(id);
    });

    if (missingElementIds.length) {
        console.error(
            "EcoSort camera page is missing required elements:",
            missingElementIds.join(", ")
        );
        return;
    }

    const startCameraButton = document.getElementById("start-camera-button");
    const captureButton = document.getElementById("capture-button");
    const video = document.getElementById("camera-video");
    const canvas = document.getElementById("camera-canvas");
    const messageBox = document.getElementById("camera-message");
    const resultBox = document.getElementById("camera-result");
    const capturedImage = document.getElementById("captured-image");

    let cameraStream = null;
    let isCameraReady = false;

    function showMessage(text, isError) {
        messageBox.textContent = text;
        messageBox.classList.remove("hidden");

        if (isError) {
            messageBox.classList.add("error");
        } else {
            messageBox.classList.remove("error");
        }
    }

    function setCaptureEnabled(enabled) {
        captureButton.disabled = !enabled;
    }

    function stopCurrentStream() {
        if (!cameraStream) {
            return;
        }

        cameraStream.getTracks().forEach(function (track) {
            track.stop();
        });
    }

    function fillTop3(listId, items) {
        const list = document.getElementById(listId);

        if (!list) {
            console.error("EcoSort camera page is missing list:", listId);
            return;
        }

        list.innerHTML = "";

        items.forEach(function (item, index) {
            const row = document.createElement("li");
            row.innerHTML = "<span>" + (index + 1) + ". " + item.label + "</span><strong>" + item.score + "%</strong>";
            list.appendChild(row);
        });
    }

    function fillResult(prefix, result) {
        const card = document.getElementById(prefix + "-card");
        const name = document.getElementById(prefix + "-name");
        const heading = document.getElementById(prefix + "-class");
        const confidence = document.getElementById(prefix + "-confidence");
        const score = document.getElementById(prefix + "-score");
        const suggestion = document.getElementById(prefix + "-suggestion");

        if (!card || !name || !heading || !confidence || !score || !suggestion) {
            console.error("EcoSort camera result card is missing fields for prefix:", prefix);
            return;
        }

        name.textContent = result.model_name;
        heading.textContent = result.predicted_class;
        confidence.textContent = result.confidence + "%";
        score.textContent = result.recognition_score + " / 100";
        fillTop3(prefix + "-top3", result.top_predictions || []);

        if (window.EcoSortUI) {
            card.setAttribute("data-category", result.predicted_class);
            card.setAttribute("data-tip", result.suggestion || "");
            window.EcoSortUI.applyCategoryDetails(card, result.predicted_class, result.suggestion, "image");
        } else {
            suggestion.textContent = result.suggestion || "";
        }
    }

    function waitForVideoReady() {
        return new Promise(function (resolve, reject) {
            if (video.videoWidth > 0 && video.videoHeight > 0) {
                resolve();
                return;
            }

            const timeoutId = window.setTimeout(function () {
                cleanup();
                reject(new Error("Video metadata did not load in time."));
            }, 4000);

            function cleanup() {
                window.clearTimeout(timeoutId);
                video.removeEventListener("loadedmetadata", onReady);
                video.removeEventListener("loadeddata", onReady);
                video.removeEventListener("canplay", onReady);
                video.removeEventListener("playing", onReady);
            }

            function onReady() {
                if (video.videoWidth > 0 && video.videoHeight > 0) {
                    cleanup();
                    resolve();
                }
            }

            video.addEventListener("loadedmetadata", onReady);
            video.addEventListener("loadeddata", onReady);
            video.addEventListener("canplay", onReady);
            video.addEventListener("playing", onReady);
        });
    }

    setCaptureEnabled(false);

    startCameraButton.addEventListener("click", async function () {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showMessage("Camera is not supported in this browser.", true);
            return;
        }

        startCameraButton.disabled = true;
        setCaptureEnabled(false);
        isCameraReady = false;
        showMessage("Opening camera...", false);

        try {
            stopCurrentStream();
            cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = cameraStream;
            await video.play();
            await waitForVideoReady();
            isCameraReady = true;
            setCaptureEnabled(true);
            showMessage("Camera is ready.", false);
        } catch (error) {
            console.error("EcoSort camera start failed:", error);
            stopCurrentStream();
            cameraStream = null;
            video.srcObject = null;
            showMessage("Could not open camera.", true);
        } finally {
            startCameraButton.disabled = false;
        }
    });

    captureButton.addEventListener("click", async function () {
        if (!video.srcObject) {
            showMessage("Please open the camera first.", true);
            return;
        }

        if (!isCameraReady || video.videoWidth <= 0 || video.videoHeight <= 0) {
            showMessage("Camera is still loading. Please wait a second and try again.", true);
            return;
        }

        const context = canvas.getContext("2d");

        if (!context) {
            console.error("EcoSort camera page could not get 2D canvas context.");
            showMessage("Could not capture the camera image.", true);
            return;
        }

        captureButton.disabled = true;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL("image/png");
        showMessage("Sending image for prediction...", false);

        try {
            const response = await fetch("/camera-predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ image_data: imageData })
            });

            const data = await response.json();

            if (!response.ok) {
                showMessage(data.error || "Prediction failed.", true);
                return;
            }

            capturedImage.src = data.image_url;
            fillResult("mobilenet", data.mobilenet_result);
            fillResult("cnn", data.simple_cnn_result);
            resultBox.classList.remove("hidden");
            showMessage("Prediction completed.", false);
        } catch (error) {
            console.error("EcoSort camera prediction request failed:", error);
            showMessage("Could not send camera image.", true);
        } finally {
            setCaptureEnabled(isCameraReady);
        }
    });
})();
