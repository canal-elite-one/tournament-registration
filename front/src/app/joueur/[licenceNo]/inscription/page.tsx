export default async function Page({
                                     params,
                                   }: {
  params: Promise<{ licenceNo: string }>;
}) {
  const {licenceNo} = await params;
  return <div>{licenceNo}</div>
};