const nodemailer = require('nodemailer');

const sendEmail = async (email, subject, htmlContent) => {
    try {
        const transporter = nodemailer.createTransport({
            host: 'smtp.gmail.com', 
            port: 587,
            secure: false,
            requireTLS: true,
            auth: {
                user: "kedarnathrothe2003@gmail.com", // Replace with your email
                pass: 'scmpzcmtrocqcvbv', // Replace with your email password
            },
        });

        await transporter.sendMail({
            from: 'kedarnathrothe2003@gmail.com', // Replace with your email
            to: email,
            subject: subject,
            html: htmlContent, // Use 'html' instead of 'text'
        });
        console.log("Email sent successfully");
    } catch (error) {
        console.log("Email not sent!");
        console.log(error);
        return error;
    }
};


module.exports = sendEmail;
