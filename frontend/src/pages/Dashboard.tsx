import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { evaluationsAPI } from '../services/api';
import type { Evaluation } from '../types';
import { Card, CardBody } from '../components/Card';
import Badge from '../components/Badge';
import LoadingSpinner from '../components/LoadingSpinner';
import { formatDate, formatScore } from '../utils/format';
import { ZONE_COLORS, STATUS_LABELS, HEURISTIC_LABELS } from '../utils/constants';
import { AlertCircle, CheckCircle2, Clock, XCircle, ChevronRight } from 'lucide-react';

export default function Dashboard() {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadEvaluations();
  }, []);

  const loadEvaluations = async () => {
    try {
      setLoading(true);
      const data = await evaluationsAPI.list(50, 0);
      setEvaluations(data.evaluations);
      setError(null);
    } catch (err) {
      setError('Failed to load evaluations. Please ensure the backend is running.');
      console.error('Error loading evaluations:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'info' | 'success' | 'danger'> = {
      pending: 'default',
      running: 'info',
      completed: 'success',
      failed: 'danger',
    };

    const icons = {
      pending: Clock,
      running: Clock,
      completed: CheckCircle2,
      failed: XCircle,
    };

    const Icon = icons[status as keyof typeof icons] || Clock;

    return (
      <Badge variant={variants[status] || 'default'}>
        <Icon className="h-3 w-3 mr-1" />
        {STATUS_LABELS[status] || status}
      </Badge>
    );
  };

  const getZoneBadge = (zone: string | null) => {
    if (!zone) return null;

    const colors = ZONE_COLORS[zone as keyof typeof ZONE_COLORS];
    return (
      <div
        className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${colors.bg} ${colors.text} ${colors.border}`}
      >
        <div className={`h-2 w-2 rounded-full mr-2 ${zone === 'green' ? 'bg-green-500' : zone === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'}`} />
        {zone.charAt(0).toUpperCase() + zone.slice(1)} Zone
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardBody>
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <p className="text-red-600 font-medium">{error}</p>
              <button
                onClick={loadEvaluations}
                className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </CardBody>
      </Card>
    );
  }

  return (
    <div>
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Evaluation Dashboard</h1>
          <p className="text-gray-600 mt-1">Monitor and analyze AI system heuristic evaluations</p>
        </div>
        <button
          onClick={() => navigate('/create')}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors font-medium"
        >
          + New Evaluation
        </button>
      </div>

      {evaluations.length === 0 ? (
        <Card>
          <CardBody>
            <div className="text-center py-12">
              <p className="text-gray-500 mb-4">No evaluations found. Create your first evaluation to get started.</p>
              <button
                onClick={() => navigate('/create')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors font-medium"
              >
                Create Evaluation
              </button>
            </div>
          </CardBody>
        </Card>
      ) : (
        <div className="space-y-4">
          {evaluations.map((evaluation) => (
            <Card
              key={evaluation.id}
              className="hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => navigate(`/evaluations/${evaluation.id}`)}
            >
              <CardBody className="py-5">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {evaluation.ai_system_name}
                      </h3>
                      {getStatusBadge(evaluation.status)}
                      {evaluation.zone_status && getZoneBadge(evaluation.zone_status)}
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                      <div>
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Overall Score</p>
                        <p className="text-lg font-semibold text-gray-900 mt-1">
                          {formatScore(evaluation.overall_score)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Iterations</p>
                        <p className="text-lg font-semibold text-gray-900 mt-1">
                          {evaluation.iteration_count}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Heuristics Tested</p>
                        <p className="text-lg font-semibold text-gray-900 mt-1">
                          {evaluation.heuristic_types.length}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Created</p>
                        <p className="text-sm text-gray-700 mt-1">
                          {formatDate(evaluation.created_at)}
                        </p>
                      </div>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2">
                      {evaluation.heuristic_types.map((type) => (
                        <Badge key={type} variant="info">
                          {HEURISTIC_LABELS[type] || type}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <ChevronRight className="h-5 w-5 text-gray-400 ml-4" />
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
