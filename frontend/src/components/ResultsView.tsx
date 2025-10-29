'use client';

import { ClassificationOutput } from '@/lib/types';

interface Props {
  result: ClassificationOutput;
  onReset: () => void;
}

export default function ResultsView({ result, onReset }: Props) {
  const getLevelBadgeClass = (level: number, type: 'krt' | 'loa') => {
    if (type === 'loa') {
      return level === 3 ? 'badge-loa3' : level === 2 ? 'badge-loa2' : 'badge-loa1';
    }
    return level === 3 ? 'badge-k3' : level === 2 ? 'badge-k2' : 'badge-k1';
  };

  const getLevelLabel = (level: number) => {
    return level === 3 ? 'Hög/Kritisk' : level === 2 ? 'Medel/Betydande' : 'Låg/Begränsad';
  };

  const getLoALabel = (loa: number) => {
    return loa === 3 ? 'LoA 3: Hög tillitsnivå (BankID/SITHS)' :
           loa === 2 ? 'LoA 2: Tvåfaktorsautentisering' :
           'LoA 1: Enkel autentisering';
  };

  return (
    <div className="space-y-6">
      {/* Results Header */}
      <div className="card">
        <h2 className="section-header">Klassningsresultat</h2>
        <p className="text-gray-600 mb-6">
          Objektet har klassificerats med följande nivåer:
        </p>

        {/* KRT Levels */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
            <div className="text-sm text-gray-600 mb-2">Konfidentialitet</div>
            <div className="text-5xl font-bold text-klassa-blue mb-2">{result.krt.K}</div>
            <div className={getLevelBadgeClass(result.krt.K, 'krt')}>
              {getLevelLabel(result.krt.K)}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Konfidentialitet: {result.confidence.K.toFixed(0)}%
            </div>
          </div>

          <div className="text-center p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
            <div className="text-sm text-gray-600 mb-2">Riktighet</div>
            <div className="text-5xl font-bold text-green-700 mb-2">{result.krt.R}</div>
            <div className={getLevelBadgeClass(result.krt.R, 'krt')}>
              {getLevelLabel(result.krt.R)}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Konfidens: {(result.confidence.R * 100).toFixed(0)}%
            </div>
          </div>

          <div className="text-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
            <div className="text-sm text-gray-600 mb-2">Tillgänglighet</div>
            <div className="text-5xl font-bold text-purple-700 mb-2">{result.krt.T}</div>
            <div className={getLevelBadgeClass(result.krt.T, 'krt')}>
              {getLevelLabel(result.krt.T)}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Konfidens: {(result.confidence.T * 100).toFixed(0)}%
            </div>
          </div>

          <div className="text-center p-6 bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg">
            <div className="text-sm text-gray-600 mb-2">Level of Assurance</div>
            <div className="text-5xl font-bold text-indigo-700 mb-2">{result.loa}</div>
            <div className={getLevelBadgeClass(result.loa, 'loa')}>
              LoA {result.loa}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              max(K={result.krt.K}, R={result.krt.R})
            </div>
          </div>
        </div>

        {/* LoA Description */}
        <div className="bg-indigo-50 border-l-4 border-indigo-500 p-4 rounded">
          <div className="font-semibold text-indigo-900 mb-1">{getLoALabel(result.loa)}</div>
          <div className="text-sm text-indigo-700">
            {result.rationale.LoA[0]}
          </div>
        </div>
      </div>

      {/* Rationale */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4">Motivering</h3>

        <div className="space-y-4">
          <div>
            <div className="font-semibold text-blue-900 mb-2 flex items-center">
              <span className="inline-block w-8 h-8 bg-klassa-blue text-white rounded-full text-center leading-8 mr-2">
                K
              </span>
              Konfidentialitet - Nivå {result.krt.K}
            </div>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-700 ml-10">
              {result.rationale.K.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>

          <div>
            <div className="font-semibold text-green-900 mb-2 flex items-center">
              <span className="inline-block w-8 h-8 bg-green-600 text-white rounded-full text-center leading-8 mr-2">
                R
              </span>
              Riktighet - Nivå {result.krt.R}
            </div>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-700 ml-10">
              {result.rationale.R.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>

          <div>
            <div className="font-semibold text-purple-900 mb-2 flex items-center">
              <span className="inline-block w-8 h-8 bg-purple-600 text-white rounded-full text-center leading-8 mr-2">
                T
              </span>
              Tillgänglighet - Nivå {result.krt.T}
            </div>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-700 ml-10">
              {result.rationale.T.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Suggested Measures */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4">Föreslagna åtgärder</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="font-semibold text-blue-900 mb-3">Konfidentialitet (K{result.krt.K})</div>
            <ul className="space-y-2">
              {result.suggested_measures.K.map((measure, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-blue-600 mr-2">•</span>
                  <span className="text-sm text-gray-700">{measure}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <div className="font-semibold text-green-900 mb-3">Riktighet (R{result.krt.R})</div>
            <ul className="space-y-2">
              {result.suggested_measures.R.map((measure, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-green-600 mr-2">•</span>
                  <span className="text-sm text-gray-700">{measure}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <div className="font-semibold text-purple-900 mb-3">Tillgänglighet (T{result.krt.T})</div>
            <ul className="space-y-2">
              {result.suggested_measures.T.map((measure, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-purple-600 mr-2">•</span>
                  <span className="text-sm text-gray-700">{measure}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <div className="font-semibold text-indigo-900 mb-3">Autentisering (LoA{result.loa})</div>
            <ul className="space-y-2">
              {result.suggested_measures.LoA.map((measure, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-indigo-600 mr-2">•</span>
                  <span className="text-sm text-gray-700">{measure}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Audit Info */}
      <div className="card bg-gray-50">
        <h3 className="text-lg font-bold mb-3">Revisionsinfo</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-500">Modellversion</div>
            <div className="font-mono">{result.audit.model_version}</div>
          </div>
          <div>
            <div className="text-gray-500">Tidsstämpel</div>
            <div className="font-mono">{new Date(result.audit.timestamp).toLocaleString('sv-SE')}</div>
          </div>
          <div>
            <div className="text-gray-500">Klassificeringstid</div>
            <div className="font-mono">{result.audit.classification_time_ms?.toFixed(0)} ms</div>
          </div>
          <div>
            <div className="text-gray-500">Objekt-ID</div>
            <div className="font-mono text-xs">{result.object_id}</div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-center space-x-4">
        <button
          onClick={onReset}
          className="btn-primary"
        >
          Ny klassning
        </button>
        <button
          onClick={() => {
            const dataStr = JSON.stringify(result, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `klassning-${result.object_id}.json`;
            link.click();
          }}
          className="btn-secondary"
        >
          Exportera JSON
        </button>
      </div>
    </div>
  );
}
