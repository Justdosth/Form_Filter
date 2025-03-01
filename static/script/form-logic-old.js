// function toggleCountryField(selectElement) {
//     const countryDetails = document.getElementById('country-details');
//     const countryInput = document.getElementById('country-name');

//     if (selectElement.value === 'ساکن شهرستان') {
//         countryDetails.style.display = 'block';
//         countryInput.required = true; // Make it required when visible
//     } else {
//         countryDetails.style.display = 'none';
//         countryInput.required = false; // Remove required if hidden
//         countryInput.value = ''; // Clear the value when hidden
//     }
// }

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

    // Prevent form submission if validation fails
    if (!isValid) {
        event.preventDefault();
    }
}
 
/**
 * Handles AJAX form submission with a beautiful SweetAlert popup.
 * @param {string} formId - The ID of the form.
 * @param {string} submitUrl - The API endpoint for submission.
 */
function setupFormSubmission(formId, submitUrl) {
    const form = document.getElementById(formId);
    
    if (!form) return;

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent traditional form submission

        let formData = new FormData(form); // Collect form data

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
            
        }
    });
}



function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
}

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