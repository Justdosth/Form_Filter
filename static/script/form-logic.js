/**
 * Handles AJAX form submission with a beautiful SweetAlert popup.
 * @param {string} formId - The ID of the form.
 * @param {string} submitUrl - The API endpoint for submission.
 */
function setupFormSubmission(formId, submitUrl) {
    const form = document.getElementById(formId);
    
    if (!form) return;

    form.addEventListener("submit", function (event) {
        // Prevent traditional form submission
        event.preventDefault();

        // Call the validateForm function to check validation before submission
        let validationPassed = validateForm(event);

        // If validation fails, stop further processing (form submission)
        if (!validationPassed) return;

        // If validation passes, collect form data
        let formData = new FormData(form); // Collect form data

        // Send data via AJAX
        fetch(submitUrl, {
            method: "POST",
            body: formData
        })
        .then(response => response.json()) // Parse JSON response
        .then(data => {
            showPopupMessage(data.success, data.message);
            if (data.success) {
                setTimeout(() => window.location.reload(), 2000); // Reload on success
            }
        })
        .catch(() => {
            showPopupMessage(false, "Something went wrong! Please try again.");
        });
    });
}

/**
 * Validates the form and returns whether validation is successful.
 * @param {Event} event - The form submit event.
 * @returns {boolean} - Whether the form passes validation or not.
 */
function validateForm(event) {
    let isValid = true;
    let firstInvalidElement = null;

    // Find all labels containing <span class="required">*</span>
    const requiredLabels = document.querySelectorAll("label:has(.required)");

    requiredLabels.forEach((label) => {
        const fieldId = label.getAttribute("for"); // Get related field ID
        const field = document.getElementById(fieldId); // Get the field
        const errorElement = document.getElementById(`${fieldId}-error`);

        if (field) {
            // Clear previous error messages
            if (errorElement) {
                errorElement.textContent = "";
                errorElement.style.display = "none";
            }
            field.classList.remove("error");

            // Validate field: Check if it's empty
            if (!field.value.trim()) {
                if (errorElement) {
                    errorElement.textContent = `لطفاً ${label.textContent.replace('*', '').trim()} را وارد کنید.`;
                    errorElement.style.display = "block";
                }
                field.classList.add("error");

                isValid = false;

                // Store the first invalid element to focus on
                if (!firstInvalidElement) {
                    firstInvalidElement = field;
                }
            }
        }
    });

    // Scroll to the first invalid field if any
    if (!isValid && firstInvalidElement) {
        firstInvalidElement.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    // If validation fails, prevent form submission
    if (!isValid) {
        event.preventDefault();
    }

    return isValid; // Return validation result
}

/**
 * Displays a styled SweetAlert popup message.
 * @param {boolean} isSuccess - Whether the submission was successful.
 * @param {string} message - The message to display.
 */
function showPopupMessage(isSuccess, message) {
    // Disable body scrolling before the popup is shown
    document.body.style.overflow = 'hidden';

    Swal.fire({
        icon: isSuccess ? 'success' : 'error',
        title: isSuccess ? '🎉 Success!' : '⚠️ Error!',
        html: `<div class="custom-swal-text">${message.replace(/\n/g, "<br>")}</div>`,
        showConfirmButton: true,
        confirmButtonText: isSuccess ? '🎯 Great!' : '🔁 Try Again',
        confirmButtonColor: isSuccess ? '#28a745' : '#dc3545',
        timer: isSuccess ? 2500 : null, // Don't auto-close errors
        customClass: {
            popup: 'custom-swal-popup',
            title: 'custom-swal-title',
            confirmButton: 'custom-swal-button'
        },
        focusConfirm: true, // Focus on the confirm button to prevent scrolling
    }).then((result) => {
        // Re-enable body scrolling after the popup is closed
        document.body.style.overflow = 'auto';  // Restore page scroll

        if (!isSuccess && result.isConfirmed) {
            // Handle retry or other actions after failure
        }
    });
}

/**
 * Scrolls the page to the top smoothly.
 */
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
}

/**
 * Scrolls the page to the bottom smoothly.
 */
function scrollToBottom() {
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
}

document.addEventListener("scroll", function () {
    const topBtn = document.getElementById("scrollToTopBtn");
    if (window.scrollY > 300) {
        topBtn.style.display = "block";
    } else {
        topBtn.style.display = "none";
    }
});

document.addEventListener("DOMContentLoaded", function () {
    setupFormSubmission("myForm", "/submit-form");
});
