// app/dashboard/page.tsx
export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Üst Menü (Header) */}
      <header className="bg-white shadow p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold text-indigo-600">
            <i className="bi bi-heart-pulse-fill mr-2"></i>KHTS Paneli
          </h1>
          <button className="text-gray-500 hover:text-red-600 text-sm">
            Çıkış Yap
          </button>
        </div>
      </header>

      {/* Ana İçerik */}
      <main className="flex-grow container mx-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Örnek Kart 1 */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-700 mb-2">Hastalarım</h2>
            <p className="text-3xl font-bold text-indigo-600">12</p>
            <p className="text-sm text-gray-400 mt-1">Aktif takipli hasta</p>
          </div>

          {/* Örnek Kart 2 */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-700 mb-2">Randevular</h2>
            <p className="text-3xl font-bold text-purple-600">3</p>
            <p className="text-sm text-gray-400 mt-1">Bugün beklenen</p>
          </div>

          {/* Örnek Kart 3 */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-700 mb-2">Analizler</h2>
            <p className="text-3xl font-bold text-blue-600">%94</p>
            <p className="text-sm text-gray-400 mt-1">Başarı oranı</p>
          </div>

        </div>

        <div className="mt-8 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4">Son İşlemler</h3>
          <p className="text-gray-500">Henüz bir işlem kaydı bulunmamaktadır.</p>
        </div>
      </main>
    </div>
  );
}