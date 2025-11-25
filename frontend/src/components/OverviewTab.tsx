import type { Evaluation, HeuristicFinding } from '../types';
import { Card, CardHeader, CardBody, CardTitle } from './Card';
import Badge from './Badge';
import { formatScore, formatPercentage } from '../utils/format';
import { HEURISTIC_LABELS, SEVERITY_COLORS, ZONE_COLORS } from '../utils/constants';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface OverviewTabProps {
  evaluation: Evaluation;
  findings: HeuristicFinding[];
}

export default function OverviewTab({ evaluation, findings }: OverviewTabProps) {
  // Prepare chart data
  const chartData = findings.map((finding) => ({
    name: HEURISTIC_LABELS[finding.heuristic_type] || finding.heuristic_type,
    score: finding.severity_score,
    severity: finding.severity,
  }));

  const getBarColor = (severity: string) => {
    const colors = {
      low: '#3b82f6',
      medium: '#f59e0b',
      high: '#f97316',
      critical: '#ef4444',
    };
    return colors[severity as keyof typeof colors] || '#6b7280';
  };

  const stats = [
    {
      label: 'Overall Score',
      value: formatScore(evaluation.overall_score),
      description: 'Weighted average of all heuristic findings',
    },
    {
      label: 'Zone Status',
      value: evaluation.zone_status?.toUpperCase() || 'N/A',
      description: 'Performance classification based on baseline',
      color: evaluation.zone_status,
    },
    {
      label: 'Heuristics Tested',
      value: evaluation.heuristic_types.length,
      description: 'Number of cognitive bias patterns evaluated',
    },
    {
      label: 'Iterations',
      value: evaluation.iteration_count,
      description: 'Test iterations for statistical reliability',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <Card key={index}>
            <CardBody>
              <p className="text-sm text-gray-500 uppercase tracking-wide">{stat.label}</p>
              <p className={`text-3xl font-bold mt-2 ${stat.color && ZONE_COLORS[stat.color as keyof typeof ZONE_COLORS]?.text}`}>
                {stat.value}
              </p>
              <p className="text-xs text-gray-600 mt-1">{stat.description}</p>
            </CardBody>
          </Card>
        ))}
      </div>

      {/* Severity Chart */}
      {findings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Severity Scores by Heuristic</CardTitle>
          </CardHeader>
          <CardBody>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="name"
                    angle={-45}
                    textAnchor="end"
                    height={100}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    label={{ value: 'Severity Score', angle: -90, position: 'insideLeft' }}
                    domain={[0, 100]}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '6px',
                    }}
                  />
                  <Bar dataKey="score" radius={[8, 8, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getBarColor(entry.severity)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Findings Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Findings Summary</CardTitle>
        </CardHeader>
        <CardBody>
          {findings.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No findings available yet</p>
          ) : (
            <div className="space-y-4">
              {findings.map((finding) => {
                const colors = SEVERITY_COLORS[finding.severity];
                return (
                  <div
                    key={finding.id}
                    className={`p-4 border rounded-lg ${colors.border} ${colors.bg}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-gray-900">
                        {HEURISTIC_LABELS[finding.heuristic_type] || finding.heuristic_type}
                      </h4>
                      <div className="flex items-center space-x-2">
                        <Badge variant={finding.severity === 'critical' ? 'danger' : finding.severity === 'high' ? 'warning' : 'info'}>
                          {finding.severity.toUpperCase()}
                        </Badge>
                        <span className="text-sm font-semibold text-gray-700">
                          {formatScore(finding.severity_score)}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{finding.pattern_description}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-600">
                      <span>Confidence: {formatPercentage(finding.confidence_level)}</span>
                      <span>•</span>
                      <span>Detected: {finding.detection_count}/{evaluation.iteration_count} iterations</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardBody>
      </Card>

      {/* Evaluation Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Evaluation Configuration</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Heuristics Tested</p>
              <div className="flex flex-wrap gap-2">
                {evaluation.heuristic_types.map((type) => (
                  <Badge key={type} variant="info">
                    {HEURISTIC_LABELS[type] || type}
                  </Badge>
                ))}
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Test Parameters</p>
              <p className="text-sm text-gray-600">
                Iterations: <span className="font-semibold">{evaluation.iteration_count}</span>
              </p>
              <p className="text-sm text-gray-600">
                Status: <span className="font-semibold">{evaluation.status}</span>
              </p>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
