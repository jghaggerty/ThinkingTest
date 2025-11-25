import type { HeuristicFinding } from '../types';
import { Card, CardHeader, CardBody, CardTitle } from './Card';
import Badge from './Badge';
import { formatPercentage } from '../utils/format';
import { HEURISTIC_LABELS, HEURISTIC_DESCRIPTIONS, SEVERITY_COLORS } from '../utils/constants';
import { AlertTriangle, CheckCircle2, Info } from 'lucide-react';

interface HeuristicsTabProps {
  findings: HeuristicFinding[];
}

export default function HeuristicsTab({ findings }: HeuristicsTabProps) {
  if (findings.length === 0) {
    return (
      <Card>
        <CardBody>
          <div className="text-center py-12">
            <Info className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No heuristic findings available</p>
          </div>
        </CardBody>
      </Card>
    );
  }

  // Sort findings by severity score (descending)
  const sortedFindings = [...findings].sort((a, b) => b.severity_score - a.severity_score);

  const getSeverityIcon = (severity: string) => {
    if (severity === 'critical' || severity === 'high') {
      return <AlertTriangle className="h-5 w-5 text-orange-500" />;
    }
    return <CheckCircle2 className="h-5 w-5 text-blue-500" />;
  };

  return (
    <div className="space-y-6">
      {/* Summary */}
      <Card>
        <CardBody>
          <div className="grid grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-sm text-gray-500">Total Findings</p>
              <p className="text-2xl font-bold text-gray-900">{findings.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Critical/High</p>
              <p className="text-2xl font-bold text-red-600">
                {findings.filter((f) => f.severity === 'critical' || f.severity === 'high').length}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Medium</p>
              <p className="text-2xl font-bold text-yellow-600">
                {findings.filter((f) => f.severity === 'medium').length}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Low</p>
              <p className="text-2xl font-bold text-blue-600">
                {findings.filter((f) => f.severity === 'low').length}
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Detailed Findings */}
      <div className="space-y-4">
        {sortedFindings.map((finding) => {
          const colors = SEVERITY_COLORS[finding.severity];
          return (
            <Card key={finding.id}>
              <CardHeader className={`${colors.bg} border-b ${colors.border}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getSeverityIcon(finding.severity)}
                    <div>
                      <CardTitle className="text-gray-900">
                        {HEURISTIC_LABELS[finding.heuristic_type] || finding.heuristic_type}
                      </CardTitle>
                      <p className="text-sm text-gray-600 mt-1">
                        {HEURISTIC_DESCRIPTIONS[finding.heuristic_type]}
                      </p>
                    </div>
                  </div>
                  <Badge variant={finding.severity === 'critical' ? 'danger' : finding.severity === 'high' ? 'warning' : finding.severity === 'medium' ? 'warning' : 'info'}>
                    {finding.severity.toUpperCase()}
                  </Badge>
                </div>
              </CardHeader>

              <CardBody>
                {/* Metrics */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Severity Score</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {finding.severity_score.toFixed(2)}
                      <span className="text-sm text-gray-500 font-normal ml-1">/ 100</span>
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Confidence Level</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {formatPercentage(finding.confidence_level)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Detection Rate</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {finding.detection_count}
                      <span className="text-sm text-gray-500 font-normal ml-1">instances</span>
                    </p>
                  </div>
                </div>

                {/* Pattern Description */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">Pattern Analysis</h4>
                  <p className="text-gray-700 bg-gray-50 p-4 rounded-md border border-gray-200">
                    {finding.pattern_description}
                  </p>
                </div>

                {/* Example Instances */}
                {finding.example_instances.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-3">Example Instances</h4>
                    <div className="space-y-2">
                      {finding.example_instances.map((example, index) => (
                        <div
                          key={index}
                          className="bg-gray-50 p-3 rounded-md border border-gray-200 text-sm text-gray-700"
                        >
                          <span className="font-medium text-gray-900">#{index + 1}:</span> {example}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardBody>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
