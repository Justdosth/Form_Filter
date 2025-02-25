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

    // Get all required input/select/textarea elements
    const requiredElements = document.querySelectorAll("[required]");
    console.log(requiredElements);

    requiredElements.forEach((inputElement) => {
        const fieldName = inputElement.getAttribute("name") || inputElement.id;
        const errorElement = document.getElementById(`${fieldName}-error`);

        // Clear previous errors
        if (errorElement) {
            errorElement.textContent = "";
            errorElement.style.display = "none";
        }
        inputElement.classList.remove("error");

        // Handle validation for different input types
        if (
            (inputElement.type === "checkbox" && !inputElement.checked) || 
            (inputElement.type === "radio" && !document.querySelector(`input[name="${fieldName}"]:checked`)) ||
            (inputElement.type !== "checkbox" && inputElement.type !== "radio" && !inputElement.value.trim()) ||
            (inputElement.tagName === "SELECT" && inputElement.disabled)
        ) {
            if (errorElement) {
                errorElement.textContent = `لطفاً ${inputElement.getAttribute("data-label") || fieldName} را وارد کنید.`; 
                errorElement.style.display = "block"; // Show error message
            }
            inputElement.classList.add("error"); // Highlight field
            isValid = false;

            // Store the first invalid element for scrolling
            if (!firstInvalidElement) {
                firstInvalidElement = inputElement;
            }
        }
    });

    // Scroll to the first invalid field
    if (!isValid && firstInvalidElement) {
        firstInvalidElement.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    // Prevent form submission if validation fails
    if (!isValid) {
        event.preventDefault();
    }
}




function clearBirthdayField() {
    document.getElementById("تاریخ تولد").value = ""; 
}

// window.onload = function() {
//     clearBirthdayField();
// };

document.addEventListener("DOMContentLoaded", function () {

    clearBirthdayField();
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", validateForm);
    }
});