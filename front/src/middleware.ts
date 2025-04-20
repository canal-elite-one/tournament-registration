import { getToken } from "next-auth/jwt";
import {NextRequest, NextResponse} from "next/server";

export async function middleware(req: NextRequest) {
  const url = new URL(req.url);
  const token = await getToken({ req, secret: process.env.NEXTAUTH_SECRET });

  const isProtectedAdminRoute =
      url.pathname.startsWith("/admin") && !url.pathname.startsWith("/admin/login");

  if (isProtectedAdminRoute && !token) {
    return NextResponse.redirect(new URL("/admin/login", req.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*"], // Moved here
};