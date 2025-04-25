import {NextResponse} from "next/server";
import {DefaultApi, RegisterEntriesRequest} from "@/backend_api/backend";

export async function POST(req: Request) {
  try {
    const {licenceNumber, email, phone, selectedCategories} = await req.json();

    const api = new DefaultApi();

    const registrationRequest: RegisterEntriesRequest = {
      licenceNo: licenceNumber,
      registerEntriesBody: {
        contactInfo: {
          email: email,
          phone: phone,
        },
        categoryIds: selectedCategories
      },
    }

    const registeredEntries = await api.registerEntries(registrationRequest);
    return NextResponse.json(registeredEntries);

  } catch (error) {
    console.error(error);
    return NextResponse.json(
        {error: 'An error occurred on registration.'},
        {status: 500}
    );
  }
}