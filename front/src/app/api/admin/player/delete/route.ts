import {
  DefaultApi,
} from "@/backend_api/backend";
import {NextResponse} from "next/server";

export async function DELETE(req: Request) {
  try {
    const {licenceNo} = await req.json();

    const api = new DefaultApi();
    const response = await api.adminDeletePlayer({licenceNo: licenceNo});

    return NextResponse.json({body: response}, {status: 200});
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (error: any) {
    console.error(await error.response.json());
    return NextResponse.json(
        {error: 'An error occurred on player deletion.'},
        {status: 500}
    );
  }
}