let uploadedEyeImage = null;
// Set up the image preview functionality
document.getElementById('eyePicture').addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
            uploadedEyeImage = event.target.result;
            document.getElementById('eyePreviewImg').src = uploadedEyeImage;
            document.getElementById('eyeImagePreview').classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
});
document.getElementById('jaundiceForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    // Show loading
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    // Collect form data
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    // Convert relevant fields to numbers
    data.age = Number(data.age);
    data.totalBilirubin = Number(data.totalBilirubin);
    data.directBilirubin = Number(data.directBilirubin);
    data.alt = Number(data.alt);
    data.ast = Number(data.ast);
    data.alkalinePhosphatase = Number(data.alkalinePhosphatase);
    data.hemoglobin = Number(data.hemoglobin);
    // Remove the file object and use the base64 string instead
    delete data.eyePicture;
    data.eyeImageBase64 = uploadedEyeImage;
    // Clear previous timeout
    if (timeoutId) clearTimeout(timeoutId);
    // Simulate processing delay
    timeoutId = setTimeout(async () => {
        try {
            const response = await fetch('/api/assess', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            // Display results
            document.getElementById('riskLevel').textContent = result.riskLevel + ' Risk';
            // Set color based on risk level
            const riskElement = document.getElementById('riskLevel');
            const recommendationBox = document.getElementById('recommendationBox');
            if (result.riskLevel === 'High') {
                riskElement.className = 'text-5xl font-bold my-6 text-red-600';
                recommendationBox.className = 'p-4 rounded-lg mb-6 bg-red-100 text-red-800';
            } else if (result.riskLevel === 'Moderate') {
                riskElement.className = 'text-5xl font-bold my-6 text-yellow-600';
                recommendationBox.className = 'p-4 rounded-lg mb-6 bg-yellow-100 text-yellow-800';
            } else {
                riskElement.className = 'text-5xl font-bold my-6 text-green-600';
                recommendationBox.className = 'p-4 rounded-lg mb-6 bg-green-100 text-green-800';
            }
            // Display risk factors
            const factorsElement = document.getElementById('riskFactors');
            factorsElement.innerHTML = '';
            if (result.factors.length === 0) {
                factorsElement.innerHTML = '<li>No significant risk factors identified</li>';
            } else {
                result.factors.forEach(factor => {
                    const li = document.createElement('li');
                    li.textContent = factor;
                    factorsElement.appendChild(li);
                });
            }
            // Display eye image if one was uploaded
            if (uploadedEyeImage) {
                document.getElementById('resultEyeImage').src = uploadedEyeImage;
                document.getElementById('eyePictureResult').classList.remove('hidden');
            } else {
                document.getElementById('eyePictureResult').classList.add('hidden');
            }
            // Display recommendation
            document.getElementById('recommendation').textContent = result.recommendation;
            // Hide loading, show results
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('results').classList.remove('hidden');
        } catch (err) {
            console.error('Error:', err);
            alert('An error occurred. Please try again.');
            document.getElementById('loading').classList.add('hidden');
        }
    }, 1000);
});
