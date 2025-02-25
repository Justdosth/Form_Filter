function toggleCountryField(selectElement) {
    const countryDetails = document.getElementById('country-details');
    const countryInput = document.getElementById('country-name');

    if (selectElement.value === 'ساکن شهرستان') {
        countryDetails.style.display = 'block';
        countryInput.required = true; // Make it required when visible
    } else {
        countryDetails.style.display = 'none';
        countryInput.required = false; // Remove required if hidden
        countryInput.value = ''; // Clear the value when hidden
    }
}


function validateForm(event) {
    let isValid = true;
    let firstInvalidElement = null;

    // Find all labels containing <span class="required">*</span>
    const requiredLabels = document.querySelectorAll("label:has(.required)");

    requiredLabels.forEach((label) => {
        const fieldId = label.getAttribute("for"); // Get the 'for' attribute that links to input/select
        const field = document.getElementById(fieldId); // Find the input/select with the corresponding ID
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

function clearBirthdayField() {
    const birthdayField = document.querySelector("input[name='birth_date']");

    if (birthdayField) {
        // Clear the value of the input field
        birthdayField.value = "";
    }
}



document.addEventListener("DOMContentLoaded", function () {
    clearBirthdayField();

    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", validateForm);
    }
});