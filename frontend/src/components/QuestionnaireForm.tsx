'use client';

import { useState } from 'react';
import { klassaApi } from '@/lib/api';
import {
  ClassificationInput,
  ClassificationOutput,
  PersonalDataCategory,
  DecisionImpact,
  PersonalDataCategoryLabels,
  DecisionImpactLabels,
} from '@/lib/types';

interface Props {
  onComplete: (result: ClassificationOutput) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

export default function QuestionnaireForm({ onComplete, loading, setLoading }: Props) {
  const [formData, setFormData] = useState<Partial<ClassificationInput>>({
    object_id: `obj-${Date.now()}`,
    object_name: '',
    object_type: 'system',
    personal_data_categories: [],
    decision_impact: DecisionImpact.NONE,
    legal: {
      osl_secret: false,
      article9: false,
      article10: false,
      minors: false,
      public_exposure: false,
      automated_decision: false,
    },
    external_dependencies: [],
    recipients: [],
  });

  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.object_name) {
      setError('Systemnamn krävs');
      return;
    }

    try {
      setLoading(true);
      const input: ClassificationInput = {
        object_id: formData.object_id!,
        object_name: formData.object_name!,
        object_type: formData.object_type || 'system',
        personal_data_categories: formData.personal_data_categories || [],
        volumes: formData.volumes,
        rto_hours: formData.rto_hours,
        legal: formData.legal!,
        decision_impact: formData.decision_impact!,
        external_dependencies: formData.external_dependencies || [],
        recipients: formData.recipients || [],
        free_text_context: formData.free_text_context,
      };

      const result = await klassaApi.classify(input);
      onComplete(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ett fel uppstod vid klassificering');
      setLoading(false);
    }
  };

  const toggleDataCategory = (category: PersonalDataCategory) => {
    const current = formData.personal_data_categories || [];
    const updated = current.includes(category)
      ? current.filter(c => c !== category)
      : [...current, category];
    setFormData({ ...formData, personal_data_categories: updated });
  };

  return (
    <form onSubmit={handleSubmit} className="card max-w-4xl mx-auto">
      <h2 className="section-header">Klassningsformulär</h2>
      <p className="text-gray-600 mb-6">
        Fyll i informationen nedan för att få en KRT-klassning. Beräknad tid: 5-7 minuter.
      </p>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {/* Basic Information */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Grundläggande information</h3>

        <div className="mb-4">
          <label className="label">Systemnamn *</label>
          <input
            type="text"
            className="input-field"
            value={formData.object_name || ''}
            onChange={(e) => setFormData({ ...formData, object_name: e.target.value })}
            placeholder="T.ex. Skoladministrationssystem"
            required
          />
        </div>

        <div className="mb-4">
          <label className="label">Typ</label>
          <select
            className="input-field"
            value={formData.object_type}
            onChange={(e) => setFormData({ ...formData, object_type: e.target.value })}
          >
            <option value="system">System</option>
            <option value="application">Applikation</option>
            <option value="process">Process/Behandling</option>
            <option value="dataset">Datamängd</option>
          </select>
        </div>
      </div>

      {/* Personal Data Categories */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Personuppgiftskategorier</h3>
        <p className="text-sm text-gray-600 mb-4">
          Välj alla kategorier som förekommer i systemet:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {Object.entries(PersonalDataCategoryLabels).map(([key, label]) => (
            <label key={key} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer">
              <input
                type="checkbox"
                className="checkbox-field mt-1"
                checked={(formData.personal_data_categories || []).includes(key as PersonalDataCategory)}
                onChange={() => toggleDataCategory(key as PersonalDataCategory)}
              />
              <span className="text-sm">{label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Volume */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Volym och omfattning</h3>

        <div className="mb-4">
          <label className="label">Antal registrerade personer</label>
          <input
            type="number"
            className="input-field"
            value={formData.volumes?.data_subjects || ''}
            onChange={(e) => setFormData({
              ...formData,
              volumes: { ...formData.volumes, data_subjects: parseInt(e.target.value) || 0 }
            })}
            placeholder="T.ex. 5000"
          />
        </div>
      </div>

      {/* RTO */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Tillgänglighetskrav</h3>

        <div className="mb-4">
          <label className="label">RTO (Recovery Time Objective) i timmar</label>
          <input
            type="number"
            step="0.5"
            className="input-field"
            value={formData.rto_hours || ''}
            onChange={(e) => setFormData({ ...formData, rto_hours: parseFloat(e.target.value) || undefined })}
            placeholder="T.ex. 4 (för 4 timmar)"
          />
          <p className="text-xs text-gray-500 mt-1">
            RTO ≤4h = Kritisk, ≤24h = Viktig, &gt;24h = Tolerant
          </p>
        </div>
      </div>

      {/* Decision Impact */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Beslutspåverkan</h3>

        <div className="space-y-2">
          {Object.entries(DecisionImpactLabels).map(([key, label]) => (
            <label key={key} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer">
              <input
                type="radio"
                name="decision_impact"
                className="h-4 w-4 text-klassa-blue focus:ring-klassa-blue"
                checked={formData.decision_impact === key}
                onChange={() => setFormData({ ...formData, decision_impact: key as DecisionImpact })}
              />
              <span className="text-sm">{label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Legal Context */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Juridiska flaggor</h3>

        <div className="space-y-3">
          <label className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
            <input
              type="checkbox"
              className="checkbox-field mt-1"
              checked={formData.legal?.osl_secret || false}
              onChange={(e) => setFormData({
                ...formData,
                legal: { ...formData.legal!, osl_secret: e.target.checked }
              })}
            />
            <div>
              <div className="font-medium">OSL-sekretess</div>
              <div className="text-xs text-gray-600">Sekretessbelagt enligt Offentlighets- och sekretesslagen</div>
            </div>
          </label>

          <label className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
            <input
              type="checkbox"
              className="checkbox-field mt-1"
              checked={formData.legal?.minors || false}
              onChange={(e) => setFormData({
                ...formData,
                legal: { ...formData.legal!, minors: e.target.checked }
              })}
            />
            <div>
              <div className="font-medium">Barn (&lt;18 år)</div>
              <div className="text-xs text-gray-600">Systemet innehåller uppgifter om barn</div>
            </div>
          </label>

          <label className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
            <input
              type="checkbox"
              className="checkbox-field mt-1"
              checked={formData.legal?.automated_decision || false}
              onChange={(e) => setFormData({
                ...formData,
                legal: { ...formData.legal!, automated_decision: e.target.checked }
              })}
            />
            <div>
              <div className="font-medium">Automatiserade beslut</div>
              <div className="text-xs text-gray-600">Systemet fattar eller påverkar beslut automatiskt</div>
            </div>
          </label>

          <label className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
            <input
              type="checkbox"
              className="checkbox-field mt-1"
              checked={formData.legal?.public_exposure || false}
              onChange={(e) => setFormData({
                ...formData,
                legal: { ...formData.legal!, public_exposure: e.target.checked }
              })}
            />
            <div>
              <div className="font-medium">Publik exponering</div>
              <div className="text-xs text-gray-600">Data exponeras publikt (öppna data)</div>
            </div>
          </label>
        </div>
      </div>

      {/* Submit */}
      <div className="flex justify-end space-x-4">
        <button
          type="button"
          className="btn-secondary"
          onClick={() => window.location.reload()}
          disabled={loading}
        >
          Rensa
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={loading}
        >
          {loading ? 'Klassificerar...' : 'Klassificera'}
        </button>
      </div>
    </form>
  );
}
