import type {NextAuthOptions} from "next-auth";
import GoogleProvider from "next-auth/providers/google";

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async signIn({ user }) {
      if (!user.email) {
        return false; // no email, reject
      }

      const allowedEmails = (process.env.ADMIN_ALLOWED_EMAILS ?? '')
          .split(',')
          .map((email) => email.trim())
          .filter((email) => email.length > 0);

      return allowedEmails.includes(user.email ?? "");
    },
    async session({ session }) {
      return session;
    },
  },
  pages: {
    signIn: "/admin/login",
  },
  secret: process.env.NEXTAUTH_SECRET,
};