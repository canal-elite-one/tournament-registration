import {
  DefaultApi,
} from "@/backend_api/backend";
import {NextResponse} from "next/server";

export async function POST(req: Request) {
  try {
    const {licenceNo, email, phone, isPlayerFromDB, totalActualPaid, entryInfo} = await req.json();

    const api = new DefaultApi();

    if (!isPlayerFromDB) {
      try {
        await api.adminAddPlayer({licenceNo: licenceNo, contactInfo: {email: email, phone: phone}});
      } catch (error) {
        console.error(error);
        return NextResponse.json(
            {error: 'An error occurred on player creation.'},
            {status: 500}
        );
      }
    }


    const response = await api.adminRegisterEntries({licenceNo: licenceNo, totalActualPaid: totalActualPaid, entryInfo: entryInfo});

    return NextResponse.json({body: response}, {status: 200});
  } catch (error) {
    console.error(error);
    return NextResponse.json(
        {error: 'An error occurred on entries submission.'},
        {status: 500}
    );
  }
}