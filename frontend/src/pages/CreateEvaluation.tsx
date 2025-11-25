import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { evaluationsAPI } from '../services/api';
import { Card, CardHeader, CardBody, CardTitle } from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import { AVAILABLE_HEURISTICS } from '../utils/constants';
import { AlertCircle, Info } from 'lucide-react';

export default function CreateEvaluation() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    ai_system_name: '',
    heuristic_types: [] as string[],
    iteration_count: 30,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.ai_system_name.trim()) {
      setError('Please enter an AI system name');
      return;
    }

    if (formData.heuristic_types.length === 0) {
      setError('Please select at least one heuristic to test');
      return;
    }

    try {
      setLoading(true);

      // Create evaluation
      const evaluation = await evaluationsAPI.create(formData);

      // Immediately execute it
      setExecuting(true);
      await evaluationsAPI.execute(evaluation.id);

      // Navigate to the evaluation detail page
      navigate(`/evaluations/${evaluation.id}`);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to create evaluation');
      console.error('Error creating evaluation:', err);
    } finally {
      setLoading(false);
      setExecuting(false);
    }
  };

  const toggleHeuristic = (value: string) => {
    setFormData((prev) => ({
      ...prev,
      heuristic_types: prev.heuristic_types.includes(value)
        ? prev.heuristic_types.filter((h) => h !== value)
        : [...prev.heuristic_types, value],
    }));
  };

  const selectAll = () => {
    setFormData((prev) => ({
      ...prev,
      heuristic_types: AVAILABLE_HEURISTICS.map((h) => h.value),
    }));
  };

  const clearAll = () => {
    setFormData((prev) => ({
      ...prev,
      heuristic_types: [],
    }));
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Create New Evaluation</h1>
        <p className="text-gray-600 mt-1">
          Configure and run a heuristic bias evaluation for your AI system
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid gap-6">
          {/* System Configuration */}
          <Card>
            <CardHeader>
              <CardTitle>System Configuration</CardTitle>
            </CardHeader>
            <CardBody>
              <div>
                <label htmlFor="ai_system_name" className="block text-sm font-medium text-gray-700 mb-2">
                  AI System Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="ai_system_name"
                  value={formData.ai_system_name}
                  onChange={(e) => setFormData({ ...formData, ai_system_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="e.g., GPT-4 Content Moderator"
                  disabled={loading}
                />
                <p className="mt-1 text-sm text-gray-500">
                  Enter a descriptive name for the AI system you're evaluating
                </p>
              </div>
            </CardBody>
          </Card>

          {/* Heuristic Selection */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Heuristic Tests <span className="text-red-500">*</span></CardTitle>
                <div className="space-x-2">
                  <button
                    type="button"
                    onClick={selectAll}
                    className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
                    disabled={loading}
                  >
                    Select All
                  </button>
                  <span className="text-gray-300">|</span>
                  <button
                    type="button"
                    onClick={clearAll}
                    className="text-sm text-gray-600 hover:text-gray-800 font-medium"
                    disabled={loading}
                  >
                    Clear All
                  </button>
                </div>
              </div>
            </CardHeader>
            <CardBody>
              <div className="space-y-3">
                {AVAILABLE_HEURISTICS.map((heuristic) => (
                  <div
                    key={heuristic.value}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      formData.heuristic_types.includes(heuristic.value)
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => !loading && toggleHeuristic(heuristic.value)}
                  >
                    <div className="flex items-start">
                      <input
                        type="checkbox"
                        checked={formData.heuristic_types.includes(heuristic.value)}
                        onChange={() => toggleHeuristic(heuristic.value)}
                        className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                        disabled={loading}
                      />
                      <div className="ml-3 flex-1">
                        <label className="font-medium text-gray-900 cursor-pointer">
                          {heuristic.label}
                        </label>
                        <p className="text-sm text-gray-600 mt-1">{heuristic.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <p className="mt-4 text-sm text-gray-500">
                Selected: {formData.heuristic_types.length} of {AVAILABLE_HEURISTICS.length} heuristics
              </p>
            </CardBody>
          </Card>

          {/* Test Parameters */}
          <Card>
            <CardHeader>
              <CardTitle>Test Parameters</CardTitle>
            </CardHeader>
            <CardBody>
              <div>
                <label htmlFor="iteration_count" className="block text-sm font-medium text-gray-700 mb-2">
                  Iteration Count
                </label>
                <input
                  type="number"
                  id="iteration_count"
                  min="10"
                  max="100"
                  value={formData.iteration_count}
                  onChange={(e) => setFormData({ ...formData, iteration_count: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                  disabled={loading}
                />
                <div className="mt-2 flex items-start space-x-2">
                  <Info className="h-4 w-4 text-blue-500 mt-0.5" />
                  <p className="text-sm text-gray-600">
                    Number of test iterations (10-100). Higher values provide more statistical reliability but take longer.
                    Recommended: 30 for balanced results.
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 mr-2" />
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors font-medium"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  {executing ? 'Running Evaluation...' : 'Creating...'}
                </>
              ) : (
                'Create & Run Evaluation'
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
