export default async function Page({
                                     params,
                                   }: {
  params: Promise<{ licenceNo: string }>;
}) {
  const licenceNo = (await params).licenceNo;

  
  return (
      <div>
        <div key="recap">
          <h1 className="text-2xl font-bold">Joueur {licenceNo}</h1>
        </div>
      </div>
  );
}
