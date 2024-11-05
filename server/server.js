const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const cors = require('cors');
const sendEmail = require('./email');

const app = express();
const PORT = 3000;

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/patientData', { useNewUrlParser: true, useUnifiedTopology: true });

// Patient data schema
const patientSchema = new mongoose.Schema({
    name: String,
    email: String,
    mobile: String,
    diseases: [{
        label: String,
        probability: Number
    }]
});

const Patient = mongoose.model('Patient', patientSchema);

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Endpoint to save patient data
app.post('/savePatientData', async (req, res) => {
    const { name, email, mobile, diseases } = req.body;

    const patientData = new Patient({
        name,
        email,
        mobile,
        diseases  // Store the array of disease labels and probabilities
    });

    try {
        // Save the patient data to MongoDB
        await patientData.save();
        
        // Prepare the email content
        const subject = "Ocular Diagnostic Result";   
        const diseaseList = diseases.map(disease => 
            `${disease.label}: ${disease.probability.toFixed(2)}%`
        ).join('<br>');  // Create an HTML list of diseases with probabilities
        
        const htmlContent = `
        <html>
          <body>
            <h2 style="color: #4CAF50;">Hello ${name},</h2>
            <p>Thank you for using our service. Your ocular result is:</p>
            <p><strong style="color: #d9534f;">${diseaseList}</strong></p>
            <p>If you have any questions, feel free to contact us.</p>
            <p>Best regards,</p>
            <p>Your Health Team</p>
          </body>
        </html>
        `;

        // Send an email to the patient
        await sendEmail(email, subject, htmlContent);  
        
        res.status(201).send('Patient data saved successfully with probabilities');
    } catch (error) {
        console.error('Error saving patient data:', error);
        res.status(400).send('Error saving patient data');
    }
});


// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
