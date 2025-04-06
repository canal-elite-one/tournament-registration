'use client';


export default function RulesPage() {
  return (
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-md shadow-md">
        <div className="border border-gray-300 rounded-md">
          <embed src="/static/reglement.pdf"
                 type="application/pdf" className="w-full h-screen"/>
        </div>
      </div>
  );
}
