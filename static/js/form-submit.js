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
