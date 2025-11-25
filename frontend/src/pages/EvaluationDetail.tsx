import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { evaluationsAPI, heuristicsAPI, recommendationsAPI } from '../services/api';
import type { Evaluation, HeuristicFinding, Recommendation } from '../types';
import { Card, CardBody } from '../components/Card';
import Badge from '../components/Badge';
import LoadingSpinner from '../components/LoadingSpinner';
import { formatDate, formatScore } from '../utils/format';
import { ZONE_COLORS, STATUS_LABELS } from '../utils/constants';
import { ArrowLeft, Download, FileText, TrendingUp, Target } from 'lucide-react';
import OverviewTab from '../components/OverviewTab';
import HeuristicsTab from '../components/HeuristicsTab';
import RecommendationsTab from '../components/RecommendationsTab';

export default function EvaluationDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [findings, setFindings] = useState<HeuristicFinding[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'heuristics' | 'recommendations'>('overview');

  useEffect(() => {
    if (id) {
      loadEvaluationData();
    }
  }, [id]);

  const loadEvaluationData = async () => {
    try {
      setLoading(true);
      const [evalData, findingsData] = await Promise.all([
        evaluationsAPI.get(id!),
        heuristicsAPI.getAll(id!),
      ]);

      setEvaluation(evalData);
      setFindings(findingsData.findings);

      // Load recommendations if evaluation is completed
      if (evalData.status === 'completed') {
        const recsData = await recommendationsAPI.getAll(id!, 'both');
        setRecommendations(recsData.recommendations);
      }

      setError(null);
    } catch (err) {
      setError('Failed to load evaluation details');
      console.error('Error loading evaluation:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (!evaluation) return;

    const exportData = {
      evaluation,
      findings,
      recommendations,
      exportedAt: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `evaluation-${evaluation.ai_system_name.replace(/\s+/g, '-')}-${evaluation.id.slice(0, 8)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !evaluation) {
    return (
      <Card>
        <CardBody>
          <div className="text-center py-12">
            <p className="text-red-600 font-medium">{error || 'Evaluation not found'}</p>
            <button
              onClick={() => navigate('/')}
              className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </CardBody>
      </Card>
    );
  }

  const getZoneBadge = (zone: string | null) => {
    if (!zone) return null;
    const colors = ZONE_COLORS[zone as keyof typeof ZONE_COLORS];
    return (
      <div
        className={`inline-flex items-center px-4 py-2 rounded-full text-base font-semibold border ${colors.bg} ${colors.text} ${colors.border}`}
      >
        <div className={`h-3 w-3 rounded-full mr-2 ${zone === 'green' ? 'bg-green-500' : zone === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'}`} />
        {zone.charAt(0).toUpperCase() + zone.slice(1)} Zone
      </div>
    );
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FileText },
    { id: 'heuristics', label: 'Heuristic Analysis', icon: TrendingUp },
    { id: 'recommendations', label: 'Recommendations', icon: Target },
  ] as const;

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Dashboard
        </button>

        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{evaluation.ai_system_name}</h1>
            <p className="text-gray-600 mt-1">Evaluation ID: {evaluation.id.slice(0, 8)}</p>
          </div>
          <button
            onClick={handleExport}
            className="flex items-center px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            <Download className="h-4 w-4 mr-2" />
            Export Results
          </button>
        </div>

        {/* Status Bar */}
        <div className="mt-4 flex items-center space-x-4">
          <Badge variant={evaluation.status === 'completed' ? 'success' : 'info'}>
            {STATUS_LABELS[evaluation.status]}
          </Badge>
          {evaluation.zone_status && getZoneBadge(evaluation.zone_status)}
          <span className="text-sm text-gray-500">
            Created: {formatDate(evaluation.created_at)}
          </span>
          {evaluation.overall_score !== null && (
            <span className="text-sm font-semibold text-gray-900">
              Overall Score: {formatScore(evaluation.overall_score)}
            </span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-5 w-5 mr-2" />
                {tab.label}
                {tab.id === 'heuristics' && findings.length > 0 && (
                  <Badge variant="default" className="ml-2">
                    {findings.length}
                  </Badge>
                )}
                {tab.id === 'recommendations' && recommendations.length > 0 && (
                  <Badge variant="default" className="ml-2">
                    {recommendations.length}
                  </Badge>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'overview' && <OverviewTab evaluation={evaluation} findings={findings} />}
        {activeTab === 'heuristics' && <HeuristicsTab findings={findings} />}
        {activeTab === 'recommendations' && <RecommendationsTab recommendations={recommendations} />}
      </div>
    </div>
  );
}
