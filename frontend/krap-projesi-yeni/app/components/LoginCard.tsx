// app/components/LoginCard.tsx
"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation'; // 1. EKLEME: Router'ı içe aktar

export default function LoginCard() {
  const [tc, setTc] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  
  const router = useRouter(); // 2. EKLEME: Router'ı tanımla

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (tc.length !== 11) {
      setMessage('TC 11 haneli olmalıdır!');
      return;
    }

    // --- BURASI DEĞİŞTİ ---
    setMessage('Giriş başarılı! Yönlendiriliyorsunuz...');
    
    // Simülasyon: 1 saniye bekle ve dashboard sayfasına git
    setTimeout(() => {
      router.push('/dashboard'); // 3. EKLEME: Sayfayı değiştir
    }, 1000);
  };

  return (
    <div className="bg-white rounded-xl shadow-2xl p-8 w-full max-w-md">
      <h1 className="text-2xl font-bold text-center text-indigo-600 mb-6">
        Sisteme Giriş
      </h1>

      {message && (
        <div className={`p-3 rounded mb-4 text-sm ${message.includes('başarılı') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">TC Kimlik No</label>
          <input
            type="text"
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-black"
            placeholder="11 haneli TC"
            value={tc}
            onChange={(e) => setTc(e.target.value.replace(/[^0-9]/g, ''))}
            maxLength={11}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Şifre</label>
          <input
            type="password"
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-black"
            placeholder="******"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button
          type="submit"
          className="w-full bg-indigo-600 text-white py-3 rounded-lg font-bold hover:bg-indigo-700 transition"
        >
          Giriş Yap
        </button>
      </form>
    </div>
  );
}