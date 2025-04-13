"use client";

export default function EntriesSummary({
                                         entries,
                                         emailContact,
                                         licenceNo,
                                       }: {
  entries: { id: string; label: string }[];
  emailContact?: string;
  licenceNo: string;
}) {
  return (
      <div className="flex justify-center items-center min-h-screen bg-gray-50 px-4 sm:px-6 overflow-y-auto font-sans antialiased">
        <div className="bg-white rounded-lg shadow-md w-full max-w-xl p-6 sm:p-8 space-y-6">
          <div className="text-center space-y-2">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-800">
              Bonjour {licenceNo} !
            </h2>
            <h3 className="text-base sm:text-lg font-semibold text-gray-700">
              Vous êtes inscrit(s) aux tableaux suivants :
            </h3>
          </div>

          <ul className="list-disc list-inside space-y-2 text-gray-700 text-sm sm:text-base leading-relaxed">
            {entries.map((entry) => (
                <li key={entry.id}>{entry.label}</li>
            ))}
          </ul>

          <p className="text-gray-600 text-sm sm:text-base text-center leading-relaxed">
            Si vous souhaitez modifier vos informations ou vos inscriptions, veuillez{" "}
            <a
                href={`mailto:${emailContact}`}
                className="font-bold text-blue-600 hover:underline"
            >
              envoyer un mail
            </a>{" "}
            aux organisateurs à l&apos;adresse suivante :{" "}
            <a
                href={`mailto:${emailContact}`}
                className="font-bold text-blue-600 hover:underline"
            >
              {emailContact}
            </a>.
          </p>
        </div>
      </div>
  );
}
