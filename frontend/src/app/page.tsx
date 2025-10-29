'use client';

import { useState } from 'react';
import QuestionnaireForm from '@/components/QuestionnaireForm';
import ResultsView from '@/components/ResultsView';
import { ClassificationOutput } from '@/lib/types';

export default function Home() {
  const [result, setResult] = useState<ClassificationOutput | null>(null);
  const [loading, setLoading] = useState(false);

  const handleClassificationComplete = (output: ClassificationOutput) => {
    setResult(output);
    setLoading(false);
  };

  const handleReset = () => {
    setResult(null);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Klassa
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            AI-drivet informationsklassningssystem för svensk offentlig sektor
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Klassificering enligt K/R/T (Konfidentialitet, Riktighet, Tillgänglighet) + LoA
          </p>
        </div>

        {/* Main Content */}
        {!result ? (
          <QuestionnaireForm
            onComplete={handleClassificationComplete}
            loading={loading}
            setLoading={setLoading}
          />
        ) : (
          <ResultsView
            result={result}
            onReset={handleReset}
          />
        )}

        {/* Footer */}
        <div className="mt-16 text-center text-sm text-gray-500">
          <p>Klassa v1.0.0 - KRT Klassningssystem</p>
          <p className="mt-2">
            Privacy by design: Systemet hanterar endast metadata, aldrig råa personuppgifter.
          </p>
        </div>
      </div>
    </main>
  );
}
