"use client";

import { Button } from "@mantine/core";
import { signIn, useSession } from "next-auth/react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AdminLoginPage() {
  const { status } = useSession();
  const router = useRouter();

  // 🔁 Redirect if already logged in
  useEffect(() => {
    if (status === "authenticated") {
      router.push("/admin");
    }
  }, [status, router]);

  return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <h1 className="text-xl">Admin Login</h1>
        <Button onClick={() => signIn("google")}>Sign in with Google</Button>
      </div>
  );
}
