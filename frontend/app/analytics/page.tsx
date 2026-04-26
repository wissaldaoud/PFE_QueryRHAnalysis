'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import MainLayout from '@/components/MainLayout';

export default function AnalyticsPage() {
  const router = useRouter();
  const [qlikUrl] = useState('http://localhost:4848/sense/app/QueryHrAnalysis.qvf');
  const [showIframeError, setShowIframeError] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }
  }, [router]);

  const openInNewTab = () => {
    window.open(qlikUrl, '_blank');
  };

  return (
    <MainLayout>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Dashboard Qlik Sense - Analyse RH
          </h1>
          <button
            onClick={openInNewTab}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Ouvrir dans un nouvel onglet
          </button>
        </div>

        {showIframeError && (
          <div className="bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 text-yellow-800 dark:text-yellow-200 px-4 py-3 rounded">
            <p className="font-medium">Note:</p>
            <p className="text-sm">
              Si le dashboard ne s'affiche pas ci-dessous, cliquez sur le bouton ci-dessus pour l'ouvrir dans un nouvel onglet.
              Qlik Sense Desktop peut bloquer l'affichage en iframe pour des raisons de sécurité.
            </p>
          </div>
        )}

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden" style={{ height: 'calc(100vh - 200px)' }}>
          <iframe
            src={qlikUrl}
            className="w-full h-full border-0"
            title="Qlik Sense Dashboard"
            onError={() => setShowIframeError(true)}
            allow="fullscreen"
          />
        </div>

        <div className="bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            <strong>📊 Dashboard Qlik Sense:</strong> {qlikUrl}
          </p>
          <p className="text-xs text-blue-600 dark:text-blue-300 mt-2">
            Assurez-vous que Qlik Sense Desktop est en cours d'exécution sur votre PC.
          </p>
        </div>
      </div>
    </MainLayout>
  );
}


