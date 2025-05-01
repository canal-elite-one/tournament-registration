import nodemailer from "nodemailer";

export class EmailSender {
  private transporter;

  constructor(
      private senderEmail: string,
      private password: string,
      private smtpServer: string = "smtp.gmail.com",
      private smtpPort: number = 587
  ) {
    this.transporter = nodemailer.createTransport({
      host: smtpServer,
      port: smtpPort,
      secure: false, // TLS
      auth: {
        user: senderEmail,
        pass: password,
      },
    });
  }

  async sendEmail(
      recipient: string,
      bcc: string[],
      body: string,
      subject: string
  ): Promise<void> {
    try {
      await this.transporter.sendMail({
        from: this.senderEmail,
        to: recipient,
        bcc,
        subject,
        html: body,
      });
      console.log(`Email sent to ${recipient}`);
    } catch (err) {
      console.error(`Failed sending email to ${recipient}:`, err);
    }
  }
}
