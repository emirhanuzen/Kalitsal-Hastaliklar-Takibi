import './globals.css'; // Özel stillerimiz
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Kalıtsal Hastalık Takip Sistemi',
  description: 'Kalıtsal hastalık risk analizi ve takibi',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="tr">
      <head>
        {/* BOOTSTRAP BAĞLANTISI (Tasarımı düzelten sihirli değnek) */}
        <link 
          href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" 
          rel="stylesheet" 
          integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM" 
          crossOrigin="anonymous"
        />
        {/* İKON BAĞLANTISI */}
        <link 
          rel="stylesheet" 
          href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css"
        />
      </head>
      <body>
        {children}
        {/* Bootstrap JavaScript (Gerekirse diye ekliyoruz) */}
        <script 
          src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" 
          integrity="sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz" 
          crossOrigin="anonymous"
        ></script>
      </body>
    </html>
  );
}