"use client";

import {Category, Player } from "@/backend_api/backend";
import {useState} from "react";

export default function PlayerFormComponent({
                         player,
                         categories,
                       }: {
  player: Player;
  categories: Category[];
}) {
  const [email, setEmail] = useState(player.email);
  const [phone, setPhone] = useState(player.phone || "");

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    console.log("Submitting form with:", { email, phone });
    // TODO: connect with your API for submission
  };

  return (
      <div className="flex justify-between">
        {/* Left Column */}
        <div className="w-1/2 p-4">
          <div className="w-full mx-auto bg-white shadow-md rounded-md overflow-hidden">
            <form className="px-6 py-4" onSubmit={handleSubmit}>
              <div className="font-bold text-xl mb-2">Inscription</div>

              {/* Name Fields */}
              <div className="mb-4 flex">
                <div className="w-1/2 pr-2">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Prénom
                  </label>
                  <input
                      disabled
                      value={player.firstName}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
                <div className="w-1/2 pl-2">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Nom
                  </label>
                  <input
                      disabled
                      value={player.lastName}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
              </div>

              {/* Licence, Points, Gender */}
              <div className="mb-4 flex">
                <div className="w-1/3 pr-2">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Numéro de licence
                  </label>
                  <input
                      disabled
                      value={player.licenceNo}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
                <div className="w-1/3 px-2">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Classement
                  </label>
                  <input
                      disabled
                      value={player.nbPoints}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
                <div className="w-1/3 pl-2">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Sexe
                  </label>
                  <input
                      disabled
                      value={player.gender}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
              </div>

              {/* Club */}
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Club
                </label>
                <input
                    disabled
                    value={player.club}
                    className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                    type="text"
                />
              </div>

              {/* Email */}
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Adresse email
                </label>
                <input
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                    type="email"
                    placeholder="Votre adresse courriel"
                />
              </div>

              {/* Phone */}
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Numéro de téléphone
                </label>
                <input
                    required
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                    type="tel"
                    placeholder="Votre numéro de téléphone"
                />
              </div>

              {/* Submit Button */}
              <div className="flex mt-auto">
                <button
                    type="submit"
                    className="bg-blue-950 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-4 ml-auto"
                >
                  S&lsquo;inscrire
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Right Column (Tables) */}
        <div className="w-1/2 p-4 relative">
          <h2 className="text-lg font-bold mb-4">Tableaux</h2>

          {/* Example table: Render categories */}
          <table className="w-full border mb-4">
            <thead className="bg-blue-950 rounded-t-lg">
            <tr>
              <th colSpan={4} className="text-white">Catégories</th>
            </tr>
            <tr>
              <th className="text-white">ID</th>
              <th className="text-white">Nom</th>
              <th className="text-white">Min Points</th>
              <th className="text-white">Max Points</th>
            </tr>
            </thead>
            <tbody>
            {categories.map((category) => (
                <tr key={category.categoryId}>
                  <td className="border px-4 py-2">{category.categoryId}</td>
                  <td className="border px-4 py-2">{category.alternateName}</td>
                  <td className="border px-4 py-2">{category.minPoints}</td>
                  <td className="border px-4 py-2">{category.maxPoints}</td>
                </tr>
            ))}
            </tbody>
          </table>
        </div>
      </div>
  );
}