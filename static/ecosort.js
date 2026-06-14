(function () {
    const categoryInfo = {
        cardboard: {
            imageExplanation: "The image model predicts this item as cardboard because it appears to have a paper-like texture or box-like shape.",
            textExplanation: "The text assistant matches words such as 'cardboard', 'box', 'carton', or 'package' with the Cardboard category.",
            tip: "Flatten cardboard boxes before recycling."
        },
        glass: {
            imageExplanation: "The image model predicts this item as glass because it may show transparent, shiny, or jar-like visual features.",
            textExplanation: "The text assistant matches words such as 'glass', 'bottle', or 'jar' with the Glass category.",
            tip: "Rinse glass bottles and jars before recycling."
        },
        metal: {
            imageExplanation: "The image model predicts this item as metal because it may show can-like, reflective, or metallic visual features.",
            textExplanation: "The text assistant matches words such as 'metal', 'can', 'tin', 'aluminum', or 'soda can' with the Metal category.",
            tip: "Empty and rinse metal cans before recycling."
        },
        paper: {
            imageExplanation: "The image model predicts this item as paper because it may show thin, flat, or sheet-like visual features.",
            textExplanation: "The text assistant matches words such as 'paper', 'newspaper', 'magazine', 'book', or 'notebook' with the Paper category.",
            tip: "Keep paper clean and dry before recycling."
        },
        plastic: {
            imageExplanation: "The image model predicts this item as plastic because it may look like a bottle, container, wrapper, or packaging material.",
            textExplanation: "The text assistant matches words such as 'plastic', 'bottle', 'bag', 'container', or 'wrapper' with the Plastic category.",
            tip: "Rinse plastic containers before recycling and check the recycling label if available."
        },
        trash: {
            imageExplanation: "The image model predicts this item as trash because it does not clearly match common recyclable categories such as paper, plastic, glass, metal, or cardboard.",
            textExplanation: "The text assistant matches words such as 'food', 'banana peel', 'tissue', 'napkin', 'dirty', or 'broken' with the Trash category.",
            tip: "Dirty, mixed, or food-contaminated waste usually belongs in general trash."
        }
    };

    const textLookupKeywords = {
        cardboard: ["cardboard", "box", "carton", "package"],
        glass: ["glass", "bottle", "jar"],
        metal: ["metal", "can", "tin", "aluminum", "soda can"],
        paper: ["paper", "newspaper", "magazine", "book", "notebook"],
        plastic: ["plastic", "bottle", "bag", "container", "wrapper"],
        trash: ["food", "banana peel", "tissue", "napkin", "dirty", "broken"]
    };

    const categoryLabels = {
        cardboard: "Cardboard",
        glass: "Glass",
        metal: "Metal",
        paper: "Paper",
        plastic: "Plastic",
        trash: "Trash"
    };

    function normalizeText(value) {
        return String(value || "").trim().toLowerCase();
    }

    function getCategoryDetails(category, fallbackTip, sourceType) {
        const normalizedCategory = normalizeText(category);
        const sharedInfo = categoryInfo[normalizedCategory];
        const normalizedSourceType = sourceType === "text" ? "text" : "image";
        const fallbackExplanation = normalizedSourceType === "text"
            ? "The text assistant could not find a clear keyword match for this category."
            : "The image model could not find a clear visual explanation for this category.";

        return {
            key: normalizedCategory,
            label: categoryLabels[normalizedCategory] || "Unknown",
            explanation: sharedInfo
                ? (normalizedSourceType === "text"
                    ? sharedInfo.textExplanation
                    : sharedInfo.imageExplanation)
                : fallbackExplanation,
            tip: sharedInfo
                ? sharedInfo.tip
                : fallbackTip || "Follow your local waste sorting guide for this item."
        };
    }

    function applyCategoryDetails(container, category, fallbackTip, sourceType) {
        if (!container) {
            return null;
        }

        const details = getCategoryDetails(category, fallbackTip, sourceType);
        const categoryField = container.querySelector("[data-field='category']");
        const headingField = container.querySelector("[data-field='heading-category']");
        const explanationField = container.querySelector("[data-field='explanation']");
        const tipField = container.querySelector("[data-field='tip']");

        if (categoryField) {
            categoryField.textContent = details.label;
        }

        if (headingField) {
            headingField.textContent = details.label;
        }

        if (explanationField) {
            explanationField.textContent = details.explanation;
        }

        if (tipField) {
            tipField.textContent = details.tip;
        }

        return details;
    }

    function findCategoryFromText(inputValue) {
        const normalizedInput = normalizeText(inputValue);

        if (!normalizedInput) {
            return { status: "empty" };
        }

        const categories = Object.keys(textLookupKeywords);
        let bestMatch = null;

        for (let index = 0; index < categories.length; index += 1) {
            const category = categories[index];
            const keywords = textLookupKeywords[category];
            const matchedKeywords = keywords.filter(function (keyword) {
                return normalizedInput.includes(keyword);
            });

            if (!matchedKeywords.length) {
                continue;
            }

            const currentMatch = {
                category: category,
                score: matchedKeywords.length,
                longestKeywordLength: matchedKeywords.reduce(function (longest, keyword) {
                    return Math.max(longest, keyword.length);
                }, 0)
            };

            if (
                !bestMatch ||
                currentMatch.score > bestMatch.score ||
                (
                    currentMatch.score === bestMatch.score &&
                    currentMatch.longestKeywordLength > bestMatch.longestKeywordLength
                )
            ) {
                bestMatch = currentMatch;
            }
        }

        if (bestMatch) {
            return { status: "matched", category: bestMatch.category };
        }

        return { status: "unknown" };
    }

    function setLookupMessage(messageBox, text, isError) {
        messageBox.textContent = text;
        messageBox.classList.remove("hidden");

        if (isError) {
            messageBox.classList.add("error");
        } else {
            messageBox.classList.remove("error");
        }
    }

    function initImagePreview() {
        const imageInput = document.getElementById("image");
        const previewBox = document.getElementById("preview-box");
        const previewImage = document.getElementById("preview-image");

        if (!imageInput || !previewBox || !previewImage) {
            return;
        }

        imageInput.addEventListener("change", function () {
            const file = imageInput.files[0];

            if (!file) {
                previewBox.classList.add("hidden");
                previewImage.src = "";
                return;
            }

            previewImage.src = URL.createObjectURL(file);
            previewBox.classList.remove("hidden");
        });
    }

    function initTextLookup() {
        const input = document.getElementById("text-item-input");
        const button = document.getElementById("text-lookup-button");
        const resultBox = document.getElementById("text-result");
        const messageBox = document.getElementById("text-result-message");
        const detailsBox = document.getElementById("text-result-details");
        const categoryBox = document.getElementById("text-result-category");
        const explanationBox = document.getElementById("text-result-why");
        const tipBox = document.getElementById("text-result-tip");

        if (!input || !button || !resultBox || !messageBox || !detailsBox) {
            return;
        }

        function handleLookup() {
            const lookupResult = findCategoryFromText(input.value);

            resultBox.classList.remove("hidden");

            if (lookupResult.status === "empty") {
                detailsBox.classList.add("hidden");
                setLookupMessage(
                    messageBox,
                    "Please enter an item name.",
                    true
                );
                return;
            }

            if (lookupResult.status === "unknown") {
                detailsBox.classList.add("hidden");
                setLookupMessage(
                    messageBox,
                    "Not sure about this item. Try a common item name or upload an image instead.",
                    false
                );
                return;
            }

            const details = getCategoryDetails(lookupResult.category, "", "text");

            categoryBox.textContent = details.label;
            explanationBox.textContent = details.explanation;
            tipBox.textContent = details.tip;

            messageBox.classList.add("hidden");
            messageBox.textContent = "";
            detailsBox.classList.remove("hidden");
        }

        button.addEventListener("click", handleLookup);
    }

    function initResultCards() {
        const resultCards = document.querySelectorAll("[data-result-card]");

        resultCards.forEach(function (card) {
            applyCategoryDetails(
                card,
                card.getAttribute("data-category"),
                card.getAttribute("data-tip"),
                "image"
            );
        });
    }

    window.EcoSortUI = {
        categoryInfo: categoryInfo,
        findCategoryFromText: findCategoryFromText,
        getCategoryDetails: getCategoryDetails,
        applyCategoryDetails: applyCategoryDetails
    };

    document.addEventListener("DOMContentLoaded", function () {
        initImagePreview();
        initTextLookup();
        initResultCards();
    });
})();
