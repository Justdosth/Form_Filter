function resetForm(event) {
    event.preventDefault(); // Prevent default submission behavior

    var form = document.querySelector('form');
    var formData = new FormData(form);

    fetch('/submit-form', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert(data.message);
            form.reset();
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => {
        console.error("Submission Error:", error);
        alert("An unexpected error occurred.");
    });
}

// document.addEventListener("DOMContentLoaded", function () {
//     const form = document.getElementById("multiStepForm");  
//     const submitButton = document.getElementById("submitButton");
//     const successMessage = document.getElementById("successMessage");
//     const errorMessage = document.getElementById("errorMessage");

//     form.addEventListener("submit", function (event) {
//         event.preventDefault(); // Prevent default form submission

//         // Collect form data dynamically
//         const formData = new FormData(form);
//         let jsonData = {};

//         // Convert FormData to JSON
//         formData.forEach((value, key) => {
//             jsonData[key] = value.trim() ? value : null;  // Convert empty strings to None
//         });

//         // Send data to Flask
//         fetch("/submit-form", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" }, 
//             body: JSON.stringify(jsonData)
//         })
//         .then(response => response.json())  
//         .then(data => {
//             if (data.status === "success") {
//                 successMessage.textContent = data.message;
//                 successMessage.style.display = "block";
//                 errorMessage.style.display = "none";
//                 form.reset(); 
//             } else {
//                 errorMessage.textContent = data.message;
//                 errorMessage.style.display = "block";
//                 successMessage.style.display = "none";
//             }
//         })
//         .catch(error => {
//             errorMessage.textContent = "خطا در ارسال اطلاعات. لطفاً دوباره تلاش کنید.";
//             errorMessage.style.display = "block";
//             successMessage.style.display = "none";
//             console.error("Error:", error);
//         });
//     });
// });
