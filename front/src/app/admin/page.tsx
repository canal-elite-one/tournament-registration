import { redirect } from "next/navigation";
import {getServerSession} from "next-auth";
import { authOptions } from "@/lib/authOptions";

export default async function AdminDashboard() {

  const session = await getServerSession(authOptions);

  if (!session) {
    redirect("/admin/login");
  }


  return (
      <div className="p-6">
      <h1 className="text-2xl font-semibold">Welcome to the admin
        dashboard!</h1>
    </div>
  );
}
