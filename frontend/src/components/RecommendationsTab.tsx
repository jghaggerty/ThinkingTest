import { useState } from 'react';
import type { Recommendation } from '../types';
import { Card, CardHeader, CardBody, CardTitle } from './Card';
import Badge from './Badge';
import { HEURISTIC_LABELS, IMPACT_LABELS, DIFFICULTY_LABELS } from '../utils/constants';
import { Target, Zap, AlertCircle, Info } from 'lucide-react';

interface RecommendationsTabProps {
  recommendations: Recommendation[];
}

export default function RecommendationsTab({ recommendations }: RecommendationsTabProps) {
  const [mode, setMode] = useState<'technical' | 'simplified' | 'both'>('both');

  if (recommendations.length === 0) {
    return (
      <Card>
        <CardBody>
          <div className="text-center py-12">
            <Info className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No recommendations available</p>
            <p className="text-sm text-gray-400 mt-2">
              Recommendations are generated after evaluation completion
            </p>
          </div>
        </CardBody>
      </Card>
    );
  }

  // Sort by priority (descending)
  const sortedRecommendations = [...recommendations].sort((a, b) => b.priority - a.priority);

  const getImpactColor = (impact: string) => {
    const colors = {
      low: 'bg-blue-50 text-blue-700 border-blue-200',
      medium: 'bg-yellow-50 text-yellow-700 border-yellow-200',
      high: 'bg-green-50 text-green-700 border-green-200',
    };
    return colors[impact as keyof typeof colors] || colors.low;
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      easy: 'bg-green-50 text-green-700 border-green-200',
      moderate: 'bg-yellow-50 text-yellow-700 border-yellow-200',
      complex: 'bg-orange-50 text-orange-700 border-orange-200',
    };
    return colors[difficulty as keyof typeof colors] || colors.moderate;
  };

  const getPriorityBadge = (priority: number) => {
    if (priority >= 8) return { variant: 'danger' as const, label: 'High Priority' };
    if (priority >= 5) return { variant: 'warning' as const, label: 'Medium Priority' };
    return { variant: 'info' as const, label: 'Low Priority' };
  };

  return (
    <div className="space-y-6">
      {/* Mode Selector */}
      <Card>
        <CardBody>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Display Mode</h3>
              <p className="text-sm text-gray-600 mt-1">
                Toggle between technical and simplified recommendation descriptions
              </p>
            </div>
            <div className="flex space-x-2 bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setMode('technical')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  mode === 'technical'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Technical
              </button>
              <button
                onClick={() => setMode('both')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  mode === 'both'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Both
              </button>
              <button
                onClick={() => setMode('simplified')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  mode === 'simplified'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Simplified
              </button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardBody>
            <div className="flex items-center space-x-3">
              <div className="bg-indigo-100 p-3 rounded-lg">
                <Target className="h-6 w-6 text-indigo-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Recommendations</p>
                <p className="text-2xl font-bold text-gray-900">{recommendations.length}</p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <div className="flex items-center space-x-3">
              <div className="bg-green-100 p-3 rounded-lg">
                <Zap className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">High Impact</p>
                <p className="text-2xl font-bold text-gray-900">
                  {recommendations.filter((r) => r.estimated_impact === 'high').length}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <div className="flex items-center space-x-3">
              <div className="bg-yellow-100 p-3 rounded-lg">
                <AlertCircle className="h-6 w-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">High Priority</p>
                <p className="text-2xl font-bold text-gray-900">
                  {recommendations.filter((r) => r.priority >= 8).length}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {sortedRecommendations.map((recommendation, index) => {
          const priorityBadge = getPriorityBadge(recommendation.priority);
          return (
            <Card key={recommendation.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="flex items-center justify-center w-8 h-8 bg-indigo-100 text-indigo-700 rounded-full font-bold text-sm">
                        {index + 1}
                      </span>
                      <CardTitle>{recommendation.action_title}</CardTitle>
                    </div>
                    <p className="text-sm text-gray-600">
                      For: <span className="font-medium">{HEURISTIC_LABELS[recommendation.heuristic_type]}</span>
                    </p>
                  </div>
                  <Badge variant={priorityBadge.variant}>
                    {priorityBadge.label}
                  </Badge>
                </div>
              </CardHeader>

              <CardBody>
                {/* Descriptions */}
                <div className="space-y-4 mb-6">
                  {(mode === 'technical' || mode === 'both') && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                        <span className="bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded text-xs mr-2">
                          TECHNICAL
                        </span>
                        Implementation Details
                      </h4>
                      <p className="text-gray-700 bg-gray-50 p-4 rounded-md border border-gray-200">
                        {recommendation.technical_description}
                      </p>
                    </div>
                  )}

                  {(mode === 'simplified' || mode === 'both') && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                        <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs mr-2">
                          SIMPLIFIED
                        </span>
                        Plain Language Explanation
                      </h4>
                      <p className="text-gray-700 bg-green-50 p-4 rounded-md border border-green-200">
                        {recommendation.simplified_description}
                      </p>
                    </div>
                  )}
                </div>

                {/* Metadata */}
                <div className="flex items-center space-x-4">
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Priority Score</p>
                    <p className="text-lg font-bold text-gray-900">{recommendation.priority}/10</p>
                  </div>
                  <div className="border-l border-gray-200 pl-4">
                    <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Estimated Impact</p>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getImpactColor(
                        recommendation.estimated_impact
                      )}`}
                    >
                      {IMPACT_LABELS[recommendation.estimated_impact]}
                    </span>
                  </div>
                  <div className="border-l border-gray-200 pl-4">
                    <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Implementation Difficulty</p>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getDifficultyColor(
                        recommendation.implementation_difficulty
                      )}`}
                    >
                      {DIFFICULTY_LABELS[recommendation.implementation_difficulty]}
                    </span>
                  </div>
                </div>
              </CardBody>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
